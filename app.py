import os
import json
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = Flask(__name__)
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('GROQ_API_KEY'):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except Exception as e:
        print(f"Erro ao ler .env: {e}")

if not api_key:
    raise ValueError("GROQ_API_KEY não foi configurada no .env")

client = Groq(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def analyze_email_with_ai(email_content):
    system_prompt = """You are an expert email analyst for a finance company. Analyze emails and return ONLY a JSON object with two fields:
1. "category": "productive" or "unproductive"
2. "suggestion_response": A response suggestion (empty string for unproductive emails)

Classification Rules:
- PRODUCTIVE: Emails requiring action or specific response:
  * Support requests or technical issues
  * Status inquiries about ongoing requests
  * Document sharing or requests
  * Specific questions about services
  * Complaints or problems requiring resolution
  * Information requests

- UNPRODUCTIVE: Emails not requiring immediate action:
  * Generic greetings (Merry Christmas, Happy Birthday)
  * Simple thanks without questions
  * Spam or advertisements
  * Completely irrelevant content

Response Rules:
- For PRODUCTIVE emails: Write a professional, empathetic response IN PORTUGUESE addressing the customer's specific request. Reference details from their email (ticket numbers, dates, issues mentioned). Provide next steps or solutions.
- For UNPRODUCTIVE emails: Return an empty string ""

Examples:
{
  "category": "productive",
  "suggestion_response": "Prezado(a), obrigado por entrar em contato. Verificamos que sua solicitação #9988 está em processamento. O reembolso será depositado em até 5 dias úteis. Caso tenha outras dúvidas, estamos à disposição."
}

{
  "category": "unproductive",
  "suggestion_response": ""
}

Return ONLY valid JSON, nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this email:\n\n{email_content}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
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
        print(f"Resposta recebida: {response_text}")
        return None
    except Exception as e:
        print(f"Erro na análise com Groq: {e}")
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

    
