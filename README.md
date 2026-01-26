# 📧 AutoMail AI - Classificador Inteligente de Emails

**Deploy:** [Acesse a Aplicação Online](https://email-classifier-je4s.onrender.com/)

Solução de IA para classificação automática de emails e geração de sugestões de resposta para empresas do setor financeiro.

## 📺 Demo

[Link para o Vídeo de Apresentação no YouTube](SEU_LINK_DO_VIDEO_AQUI)

---

## 🎯 Sobre o Projeto

O **AutoMail AI** é uma aplicação web fullstack que utiliza Inteligência Artificial para automatizar a triagem de emails corporativos. O sistema classifica mensagens recebidas como **Produtivas** ou **Improdutivas** e gera, automaticamente, minutas de respostas profissionais, reduzindo drasticamente o tempo de processamento da equipe financeira.

### Problema Resolvido
Empresas do setor financeiro lidam com alto volume de comunicação. Esta solução resolve:
* **Gargalo Operacional:** Elimina a leitura manual de emails irrelevantes (spam, felicitações).
* **Padronização:** Garante que todas as respostas sigam um tom profissional e consistente.
* **Agilidade:** Processamento em tempo real de requisições e dúvidas.

---

## ✨ Funcionalidades

* ✅ **Classificação Inteligente:** Categoriza emails usando LLMs de última geração.
* ✅ **Sugestões de Resposta:** Gera respostas empáticas e contextuais apenas para demandas reais.
* ✅ **Suporte a Arquivos:** Leitura e extração de texto de arquivos `.txt` e `.pdf`.
* ✅ **Interface Responsiva:** UX amigável construída com Tailwind CSS.
* ✅ **Alta Performance:** Integração com Groq para inferência em milissegundos.

---

## 💡 Decisões Técnicas

A escolha da stack foi focada em **performance, custo-benefício e simplicidade**:

* **Groq + Llama 3:** Optei pela API da Groq em vez da OpenAI devido à **latência extremamente baixa** (essencial para UX em tempo real) e ao uso do modelo Llama 3.3 70B, que oferece excelente compreensão de contexto em português com custo reduzido.
* **JSON Mode:** A IA foi configurada para retornar estritamente JSON. Isso evita erros de *parsing* no frontend e garante que a aplicação nunca quebre por formatação inesperada do texto gerado.
* **Tailwind CSS:** Utilizado via CDN para prototipagem rápida de uma interface limpa, moderna e responsiva sem a complexidade de *build steps* do Node.js.

---

## 🛠️ Tecnologias Utilizadas

**Backend**
* Python 3.10+
* Flask (Web Framework)
* Groq API (Inference Engine)
* PyPDF (Processamento de Arquivos)

**Frontend**
* HTML5 / JavaScript (Vanilla)
* Tailwind CSS (Estilização)

**Infraestrutura**
* Render (Cloud Hosting)
* Gunicorn (WSGI Server)

---

## 🚀 Como Executar Localmente

**Pré-requisitos:** Python 3.8+ e uma chave de API da [Groq Cloud](https://console.groq.com/).

1. **Clone o repositório**
   ```bash
   git clone [https://github.com/SEU_USUARIO/email-classifier.git](https://github.com/SEU_USUARIO/email-classifier.git)
   cd email-classifier
   ````
2. **Configure o Ambiente**

```Bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```
3. **Instale as dependências**

```
pip install -r requirements.txt
````
4. **Variáveis de Ambiente Crie um arquivo .env na raiz e adicione:**

```
GROQ_API_KEY=sua_chave_aqui
````
5. **Execute**

```
python app.py
```
Acesse em: http://127.0.0.1:5000

🧠 Como Funciona a IA
O Prompt do Sistema: A IA atua como um assistente sênior de triagem. Ela analisa o texto extraído e aplica regras de negócio:

Produtivo: Solicitações de reembolso, dúvidas sobre taxas, envio de comprovantes. -> Gera Resposta.

Improdutivo: "Bom dia", "Obrigado", Spam. -> Não gera resposta.

👤 Autor
Sara Silva Desenvolvido para o Desafio Técnico AutoU
