# 📧 AutoMail AI - Classificador Inteligente de Emails

Solução de IA para classificação automática de emails e geração de sugestões de resposta para empresas do setor financeiro.

## 🎯 Sobre o Projeto

O **AutoMail AI** é uma aplicação web que utiliza Inteligência Artificial para automatizar a triagem de emails corporativos, classificando-os como **Produtivos** ou **Improdutivos** e gerando sugestões de resposta profissionais quando necessário.

### Problema Resolvido

Empresas do setor financeiro recebem centenas de emails diariamente, incluindo:
- Solicitações de suporte e status de requisições
- Compartilhamento de documentos
- Mensagens improdutivas (felicitações, spam, etc.)

Esta solução **libera tempo da equipe** ao automatizar a classificação e sugerir respostas, eliminando trabalho manual repetitivo.

## ✨ Funcionalidades

- ✅ **Classificação Inteligente**: Categoriza emails em Produtivo ou Improdutivo
- ✅ **Sugestões de Resposta**: Gera respostas profissionais contextualizadas para emails produtivos
- ✅ **Múltiplos Formatos**: Aceita texto direto, arquivos .txt e .pdf
- ✅ **Interface Intuitiva**: Design moderno e responsivo com Tailwind CSS
- ✅ **API Rápida**: Integração com Groq (Llama 3.3 70B) para respostas em segundos

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.x**
- **Flask** - Framework web
- **Groq API** - IA generativa (Llama 3.3 70B Versatile)
- **pypdf** - Extração de texto de PDFs
- **python-dotenv** - Gerenciamento de variáveis de ambiente

### Frontend
- **HTML5 + JavaScript**
- **Tailwind CSS** - Estilização
- **Font Awesome** - Ícones

### Deploy
- **Render** - Hospedagem em nuvem
- **Gunicorn** - Servidor WSGI para produção

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.8+
- Chave de API do Groq (gratuita em https://console.groq.com/keys)

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/email-classifier.git
cd email-classifier
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```env
GROQ_API_KEY=sua_chave_aqui
```

6. **Execute a aplicação**
```bash
python app.py
```

7. **Acesse no navegador**
```
http://127.0.0.1:5000
```

## 📁 Estrutura do Projeto

```
email-classifier/
├── app.py                 # Backend Flask + integração com IA
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (não commitado)
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Documentação
└── templates/
    └── index.html        # Interface web
```

## 🎮 Como Usar

1. **Insira o conteúdo do email** diretamente no campo de texto, OU
2. **Faça upload de um arquivo** (.txt ou .pdf)
3. **Clique em "Analisar Email"**
4. **Visualize os resultados**:
   - Classificação (Produtivo/Improdutivo)
   - Sugestão de resposta (apenas para emails produtivos)

## 🧠 Como Funciona a IA

### Classificação

**Produtivo:**
- Solicitações de suporte ou problemas técnicos
- Consultas sobre status de requisições
- Compartilhamento ou solicitação de documentos
- Perguntas específicas sobre serviços
- Reclamações que requerem resolução

**Improdutivo:**
- Mensagens genéricas (Feliz Natal, Parabéns)
- Agradecimentos simples sem perguntas
- Spam ou propagandas
- Conteúdo completamente irrelevante

### Geração de Respostas

Para emails **produtivos**, a IA:
- Analisa o contexto e detalhes específicos (números de ticket, datas, etc.)
- Gera resposta empática e profissional em português
- Fornece próximos passos ou soluções

Para emails **improdutivos**, não gera sugestão de resposta.


## 👤 Autor

Sara Silva
Desenvolvido para o Desafio IA da AutoU

## 📄 Licença

Este projeto está sob a licença MIT.
