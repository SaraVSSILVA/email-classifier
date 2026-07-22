import json
import os
import re
import unicodedata
from datetime import datetime

import gspread  
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq
import requests

load_dotenv()

app = Flask(__name__)

gc = None
planilha = None
spreadsheet_id = os.environ.get("SPREADSHEET_ID")
spreadsheet_url = os.environ.get("SPREADSHEET_URL")

system_prompt = system_prompt = """Você é um assistente de caixa rápido para uma cantina. Sua função é extrair informações de vendas de mensagens de texto enviadas por atendentes.
Sua saída DEVE ser estritamente um JSON válido, sem nenhum texto adicional, markdown ou explicações.
Regras de extração:
1. 'itens': Uma lista de objetos, cada um contendo 'produto' (string, nome padronizado do item) e 'quantidade' (inteiro). ATENÇÃO: TUDO que for comida ou bebida (ex: suco, mousse, doce, torta, água, salgado, combo, etc.) DEVE ser listado como item.
2. 'pagamento': Identifique a forma de pagamento (ex: 'pix', 'dinheiro', 'cartao'). Se não for mencionado, retorne null.
3. 'observacao': Qualquer detalhe extra sobre o pedido (ex: 'para viagem', 'sem gelo'). NUNCA coloque nomes de comidas ou bebidas aqui. Se não houver observação real, retorne null."""


def extrair_cabecalho_manual(mensagem):
    nome = "-"
    total = "-"
    texto_limpo = mensagem

    nome_match = re.search(r"\bnome\s*[:\-=]?\s*(.*?)\s*(?=\btotal\b|\||$)", mensagem, re.IGNORECASE)
    if nome_match:
        nome = nome_match.group(1).strip()
        texto_limpo = re.sub(r"\bnome\s*[:\-=]?\s*.*?(?=\btotal\b|\||$)", "", texto_limpo, flags=re.IGNORECASE)

    total_match = re.search(r"\btotal\s*[:\-=]?\s*([0-9]+(?:[.,][0-9]{1,2})?)", mensagem, re.IGNORECASE)
    if total_match:
        total = total_match.group(1).strip()
        texto_limpo = re.sub(r"\btotal\s*[:\-=]?\s*[0-9]+(?:[.,][0-9]{1,2})?", "", texto_limpo, flags=re.IGNORECASE)
    elif total == "-":
        valor_match = re.search(r"\b[0-9]+(?:[.,][0-9]{2})\b", mensagem)
        if valor_match:
            total = valor_match.group(0).strip()
            texto_limpo = texto_limpo.replace(valor_match.group(0), "")

    if nome == "-":
        inicio_match = re.match(r"^\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]*)\b", mensagem)
        if inicio_match:
            possivel_nome = inicio_match.group(1).strip()
            if possivel_nome.lower() not in {"nome", "total", "saiu", "sai", "pagou", "pago"}:
                nome = possivel_nome
                texto_limpo = re.sub(rf"^\s*{re.escape(possivel_nome)}\b", "", texto_limpo, flags=re.IGNORECASE)

    texto_limpo = re.sub(r"\s*\|\s*", " ", texto_limpo)
    texto_limpo = re.sub(r"\s+", " ", texto_limpo).strip(" |")

    return nome or "-", total or "-", texto_limpo


def extrair_observacao_manual(mensagem_limpa):
    texto = unicodedata.normalize("NFKD", mensagem_limpa.lower()).encode("ascii", "ignore").decode("ascii")

    for termo in ["saiu", "sai", "vendeu", "vendido", "pagou", "pago", "nao", "não", "pix", "dinheiro", "cartao", "cartão", "no", "na", "em", "e", "total", "observacao", "observacao:"]:
        texto = re.sub(rf"\b{re.escape(termo)}\b", " ", texto)

    for termo in [
        r"\b\d+\s+(?:agua|aguas|bolo|bolos|refri|refrigerante|refrigerantes|cachorro quente|cachorro-quente|coca|coca cola|salgado|salgados|cafe|cafes|suco|sucos|mousse|mousses|doce|doces|torta|tortas|combo|combos)\b",
        r"\b[0-9]+(?:[.,][0-9]{2})\b",
    ]:
        texto = re.sub(termo, " ", texto)

    for termo in ["agua", "aguas", "bolo", "bolos", "refri", "refrigerante", "refrigerantes", "cachorro quente", "cachorro-quente", "coca", "coca cola", "salgado", "salgados", "cafe", "cafes", "suco", "sucos", "mousse", "mousses", "doce", "doces", "torta", "tortas", "combo", "combos"]:
        texto = re.sub(rf"\b{re.escape(termo)}\b", " ", texto)

    texto = re.sub(r"\s+", " ", texto).strip(" ,;:-|")
    return texto or None


def extrair_pagamento_manual(mensagem_limpa):
    texto = unicodedata.normalize("NFKD", mensagem_limpa.lower()).encode("ascii", "ignore").decode("ascii")

    if re.search(r"\bnao\s+pagou\b", texto) or re.search(r"\bn[aã]o\s+pagou\b", mensagem_limpa, re.IGNORECASE):
        return "fiado"
    if "pix" in texto:
        return "pix"
    if "dinheiro" in texto or "cash" in texto:
        return "dinheiro"
    if "cartao" in texto or "cartão" in texto:
        return "cartao"
    if "fiado" in texto:
        return "fiado"
    return None


def extrair_localmente(mensagem):
    texto = unicodedata.normalize("NFKD", mensagem.lower()).encode("ascii", "ignore").decode("ascii")

    itens = []
    # Dicionário atualizado com novos produtos
    produto_mapa = {
        "agua": "agua",
        "aguas": "agua",
        "bolo": "bolo",
        "bolos": "bolo",
        "refri": "refrigerante",
        "refrigerante": "refrigerante",
        "refrigerantes": "refrigerante",
        "cachorro quente": "cachorro quente",
        "cachorro-quente": "cachorro quente",
        "coca": "refrigerante",
        "coca cola": "refrigerante",
        "salgado": "salgado",
        "salgados": "salgado",
        "cafe": "cafe",
        "cafes": "cafe",
        "suco": "suco",
        "sucos": "suco",
        "mousse": "mousse",
        "mousses": "mousse",
        "doce": "doce",
        "doces": "doce",
        "torta": "torta",
        "tortas": "torta",
        "combo": "combo",
        "combos": "combos",
    }

    for termo, produto in produto_mapa.items():
        for match in re.finditer(rf"(\d+)\s+{re.escape(termo)}\b", texto):
            itens.append({"produto": produto, "quantidade": int(match.group(1))})

    if not itens:
        for termo, produto in produto_mapa.items():
            if re.search(rf"\b{re.escape(termo)}\b", texto):
                itens.append({"produto": produto, "quantidade": 1})

    pagamento = None
    if "pix" in texto:
        pagamento = "pix"
    elif "dinheiro" in texto:
        pagamento = "dinheiro"
    elif "cartao" in texto or "cartão" in texto:
        pagamento = "cartao"

    observacao = None
    for termo in ["sem gelo", "fiado", "troco", "entregar", "entrega"]:
        if termo in texto:
            observacao = termo
            break

    return {
        "itens": itens,
        "pagamento": pagamento,
        "observacao": observacao,
    }


def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def get_gspread_client():
    global gc

    if gc is not None:
        return gc

    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "credentials.json"
    if os.path.exists(credentials_path):
        gc = gspread.service_account(filename=credentials_path)
        return gc

    credentials_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        gc = gspread.service_account_from_dict(json.loads(credentials_json))
        return gc

    return None


def classificar_venda(mensagem):
    try:
        client = get_client()
        if client is None:
            return extrair_localmente(mensagem)

        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensagem},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        return json.loads(chat_completion.choices[0].message.content)
    except Exception:
        return extrair_localmente(mensagem)


def get_planilha():
    global planilha
    if planilha is None:
        client = get_gspread_client()
        if client is None:
            return None
        if spreadsheet_id:
            planilha = client.open_by_key(spreadsheet_id).sheet1
        elif spreadsheet_url:
            planilha = client.open_by_url(spreadsheet_url).sheet1
        else:
            return None
    return planilha


def enviar_mensagem_telegram(chat_id, texto):
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não foi configurado no ambiente")

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": texto},
        timeout=15,
    )
    response.raise_for_status()
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return jsonify({"status": "Cantina Bot Operacional"}), 200

    if not request.is_json:
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    mensagem = data.get('message', {}).get('text')
    chat_id = data.get('message', {}).get('chat', {}).get('id')

    if not mensagem or not chat_id:
        return jsonify({"status": "ok"}), 200

    nome, total, mensagem_limpa = extrair_cabecalho_manual(mensagem)

    try:
        resultado = classificar_venda(mensagem_limpa)
        pagamento_manual = extrair_pagamento_manual(mensagem_limpa)
        
        itens_formatados = ", ".join(
            [f"{item.get('quantidade', 1)}x {item.get('produto', 'Item')}" for item in resultado.get('itens', [])]
        )
        
        pagamento = pagamento_manual or resultado.get('pagamento') or 'Não identificado'
        pagamento = str(pagamento).upper()
        observacao = resultado.get('observacao') or extrair_observacao_manual(mensagem_limpa) or "-"
        resultado['observacao'] = observacao if observacao != "-" else None
        
        if pagamento_manual:
            resultado['pagamento'] = pagamento_manual
            
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nome_formatado = nome or "-"
        total_formatado = total or "-"

        sheet = get_planilha()
        salvo_na_planilha = False
        
        if sheet is not None:
            nova_linha = [nome_formatado, data_hora, itens_formatados, pagamento, observacao, total_formatado]
            sheet.append_row(nova_linha, value_input_option="USER_ENTERED")
            salvo_na_planilha = True

        try:
            enviar_mensagem_telegram(chat_id, "✅ Venda registrada com sucesso na planilha!")
        except Exception:
            pass

        return jsonify({
            "status": "success",
            "message": "Salvo na planilha com sucesso!" if salvo_na_planilha else "Planilha não configurada; venda processada sem persistência.",
            "nome": nome_formatado,
            "total": total_formatado,
            "data": resultado,
        }), 200
    except Exception as error:
        try:
            enviar_mensagem_telegram(chat_id, f"❌ Não foi possível registrar a venda: {error}")
        except Exception:
            pass
        return jsonify({"error": str(error)}), 200


if __name__ == '__main__':
    app.run(debug=True)