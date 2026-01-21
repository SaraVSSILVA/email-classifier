import os
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def analyze_email_with_ai(email_content):
    system_prompt = """
You are an expert email analyst for a finance company. Your task is reading and returning ONLY one object in JSON format with two fields:
1. "category": "productive" or "unproductive".
2. "suggestion_response": A short answer and professional based on category.

Rules:
- Productive: Solicitations of support, doubts, status, problems.
- Unproductive: Spam, advertisements, irrelevant content, simple thanks, felicitations, ok.
"""

try:
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analise este email:\n\n{email_content}"}
    ],
    response_format={"type": "json_object"}
)
return response.choices[0].message.content
except Exception as e:
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_email():
    email_text = ""

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file.filename.endswith('.pdf'):
            email_text = extract_text_from_pdf(file)
        elif file.filename.endswith('.txt'):
            email_text = file.read().decode('utf-8')
    else:
        email_text = request.form.get('email_text', '')
    
    if not email_text.strip():
        return jsonify({"error": "No email content provided."}), 400
    
    ai_result = analyze_email_with_ai(email_text)

    if ai_result:
        return ai_result
    else:
        return jsonify({"error": "Error to the processing with AI."}), 500
if __name__ == '__main__':
    app.run(debug=True)

    
