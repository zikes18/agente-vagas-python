# 🕵️‍♂️ Agente de Vagas com IA 

Um robô inteligente e autônomo que monitora vagas de emprego, analisa os requisitos usando Inteligência Artificial (Gemini) e envia apenas as oportunidades ideais para o seu Telegram.

## 🚀 Funcionalidades

* **Busca Multi-Categoria:** Monitora vagas em diversas tecnologias (Python, Java, React, Dados, etc.).
* **Análise com IA:** Utiliza o Google Gemini Flash Latest para ler a descrição da vaga e filtrar por:
    * **Nível:** Júnior, Estágio, Trainee (Filtra Sênior/Pleno).
    * **Localização:** Brasília, Curitiba ou Remoto.
* **Memória Persistente:** Salva o histórico de vagas analisadas (`historico_vagas.json`) para evitar notificações repetidas.
* **Anti-Bloqueio:** Utiliza `cloudscraper` para simular um navegador real e acessar sites protegidos.
* **Modo Híbrido:**
    * 🖥️ **PC Local:** Menu interativo para escolher qual categoria buscar.
    * ☁️ **Nuvem (GitHub Actions):** Varredura automática e completa todos os dias.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **IA:** Google Generative AI (Gemini)
* **Web Scraping:** BeautifulSoup4 & CloudScraper
* **Notificações:** Telegram Bot API
* **Automação:** GitHub Actions (CI/CD)

---

## ⚙️ Configuração Local (No seu PC)

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/LeoSousaJesus/agente-vagas-python.git](https://github.com/LeoSousaJesus/agente-vagas-python.git)
    cd agente-vagas-python
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure as Chaves de Acesso:**
    Crie variáveis de ambiente no seu sistema ou edite o código para testes (não recomendado comitar chaves reais):
    * `GOOGLE_API_KEY`: Sua chave do Google AI Studio.
    * `TELEGRAM_TOKEN`: Token do seu bot (BotFather).
    * `TELEGRAM_CHAT_ID`: Seu ID numérico do Telegram.

4.  **Execute:**
    ```bash
    python agente_final.py
    ```

---

## ☁️ Configuração na Nuvem (GitHub Actions)

O robô roda automaticamente todos os dias às **08:00 (Horário de Brasília)**.

### 1. Secrets (Cofre)
No seu repositório GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:
* `GOOGLE_API_KEY`
* `TELEGRAM_TOKEN`
* `TELEGRAM_CHAT_ID`

### 2. Permissões de Escrita
Para que a "Memória" funcione (salvar o histórico), vá em **Settings > Actions > General > Workflow permissions** e marque a opção:
✅ **Read and write permissions**

---

## 📂 Estrutura do Projeto

* `agente_final.py`: O cérebro do robô (Scraping + IA + Lógica).
* `.github/workflows/main.yml`: O agendamento da automação.
* `requirements.txt`: Lista de bibliotecas necessárias.
* `historico_vagas.json`: Banco de dados local das vagas já vistas.

## 🤝 Como Contribuir

Sinta-se à vontade para abrir Issues ou enviar Pull Requests com novas funcionalidades, como adicionar novos sites de emprego ou critérios de filtro!

---
*Desenvolvido por Leo Sousa com ajuda de Josias Alves e Python em parceria com o Gemini.*
