import requests
from bs4 import BeautifulSoup
from google import genai
import time
import csv
import os
import json
from datetime import datetime

# --- 🛡️ CONFIGURAÇÃO SEGURA (Cofre) ---
# O script agora busca as chaves nas variáveis do sistema (Secrets)
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

client = genai.Client(api_key=GOOGLE_API_KEY)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- 🧠 CÉREBRO (IA) ---
prompt_sistema = """
Analise a descrição da vaga.
Meus Critérios: Nível Júnior/Iniciante. Tech: Python.
Regra: Se pedir experiência Sênior/Pleno (+3 anos), match é FALSE.

Responda APENAS JSON válido:
{"cargo": "...", "match": true/false, "motivo": "..."}
"""

# --- 📤 FUNÇÕES ---

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

def analisar_vaga(texto_vaga):
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt_sistema + "\n\n" + texto_vaga
        )
        return response.text
    except:
        return ""

# --- 🚀 PROGRAMA PRINCIPAL ---
url_lista = "https://www.python.org/jobs/"
print(f"🚀 Iniciando Agente na Nuvem...")

response = requests.get(url_lista, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
vagas = soup.find_all('h2', class_='listing-company')

# Analisando as 5 primeiras na nuvem
for vaga in vagas[:5]:
    empresa = vaga.find('span', class_='listing-company-name').get_text(strip=True)
    link = "https://www.python.org" + vaga.find('a')['href']
    
    print(f"🔎 Analisando: {empresa}...")
    
    # Entra na vaga
    resp_vaga = requests.get(link, headers=headers)
    desc = BeautifulSoup(resp_vaga.text, 'html.parser').get_text()[:5000]
    
    # IA Decide
    res_json = analisar_vaga(desc)
    
    try:
        dados = json.loads(res_json.strip().replace('```json', '').replace('```', ''))
        
        if dados.get('match'):
            print("✅ MATCH ENCONTRADO! Enviando alerta...")
            msg = f"🎯 VAGA TOP!\n\n🏢 {empresa}\n💼 {dados.get('cargo')}\n🔗 {link}\n\n💡 {dados.get('motivo')}"
            enviar_telegram(msg)
            
    except Exception as e:
        print(f"⚠️ Erro JSON: {e}")
    
    time.sleep(1) # Respeito ao servidor

print("🏁 Fim da execução.")