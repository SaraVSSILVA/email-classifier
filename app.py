import os
import json
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api_key = os.getenv("OPENAI_API_KEY")  # Renomear para GEMINI_API_KEY se preferir
if not api_key:
    raise ValueError("OPENAI_API_KEY não foi configurada no .env")
genai.configure(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def analyze_email_with_ai(email_content):
    system_prompt = """You are an expert email analyst for a finance company. Your task is reading and returning ONLY a JSON object with two fields:
1. "category": "productive" or "unproductive".
2. "suggestion_response": A short answer and professional based on category.

Rules:
- Productive: Solicitations of support, doubts, status, problems.
- Unproductive: Spam, advertisements, irrelevant content, simple thanks, felicitations, ok.

Return ONLY valid JSON, nothing else."""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            f"{system_prompt}\n\nAnalyze this email:\n\n{email_content}"
        )
        
        # Extrair o texto da resposta
        response_text = response.text.strip()
        
        # Se a resposta vem com markdown code blocks, remover
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        result = json.loads(response_text.strip())
        return result
    except json.JSONDecodeError as e:
        print(f"Erro ao fazer parse do JSON: {e}")
        return None
    except Exception as e:
        print(f"Erro na análise com Gemini: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_email():
    email_text = ""

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            email_text = extract_text_from_pdf(file)
        elif filename.endswith('.txt'):
            email_text = file.read().decode('utf-8')
        else:
            return jsonify({"error": "Only PDF and TXT files are supported."}), 400
    else:
        email_text = request.form.get('email_text', '')
    
    if not email_text.strip():
        return jsonify({"error": "No email content provided."}), 400
    
    ai_result = analyze_email_with_ai(email_text)

    if ai_result:
        return jsonify(ai_result)
    else:
        return jsonify({"error": "Error processing email with AI."}), 500
if __name__ == '__main__':
    app.run(debug=True)

    
