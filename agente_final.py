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

# --- 📋 SUA LISTA DE DESEJOS ---
# Coloque aqui o que você quer buscar.
# Use hifens no lugar de espaços (ex: "data-science", "banco-de-dados")
TERMOS_BUSCA = [
    "python",
    "data-science",
    "suporte",
    "banco-de-dados",
    "front-end" # Adicionei mais um de exemplo
]

# --- 🧠 CÉREBRO (IA) ---
prompt_sistema = """
Você é um Recrutador Especialista. Analise a vaga abaixo.

MEUS CRITÉRIOS:
1. Nível: Júnior, Estágio, Trainee ou "Sem Experiência".
   (Aceitar Pleno APENAS se pedir menos de 2 anos de xp).
2. LOCALIZAÇÃO (Crítico):
   - Aceitar: Distrito Federal (Brasília e satélites).
   - Aceitar: Curitiba (PR) e região.
   - Aceitar: 100% Remoto (Home Office).
   - REJEITAR: Presencial em outras cidades.

Responda APENAS JSON válido:
{"cargo": "Título", "cidade": "Cidade/Remoto", "match": true/false, "motivo": "Resumo curto"}
"""

# --- FUNÇÕES ---
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=data)
    except:
        pass

def analisar_vaga(texto_vaga):
    if len(texto_vaga) < 50: return ""
    
    tentativas = 0
    while tentativas < 3:
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt_sistema + "\n\n" + texto_vaga
            )
            return response.text
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                print(f"   ⏳ API cheia. Esperando 60s... (Tentativa {tentativas+1}/3)")
                time.sleep(60)
                tentativas += 1
            else:
                return ""
    return ""

# --- 🚀 PROGRAMA PRINCIPAL ---
print(f"🚀 Iniciando Patrulha Multi-Missão...")

# Loop Principal: Para cada termo na sua lista...
for termo in TERMOS_BUSCA:
    url_atual = f"https://programathor.com.br/jobs-{termo}"
    print(f"\n📂 CATEGORIA: {termo.upper()}")
    print(f"🌍 Acessando: {url_atual}")
    
    try:
        response = requests.get(url_atual, headers=headers)
        if response.status_code != 200:
            print(f"❌ Não consegui acessar a página de {termo}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        vagas = soup.find_all('div', class_='cell-list')
        
        if len(vagas) == 0:
            print("📭 Nenhuma vaga encontrada nesta categoria.")
            continue
            
        print(f"🔎 Encontrei {len(vagas)} vagas. Analisando as 3 primeiras...")

        # Analisa as 3 primeiras de CADA categoria
        for vaga in vagas[:3]:
            tag_a = vaga.find('a')
            if not tag_a: continue
            
            link = "https://programathor.com.br" + tag_a['href']
            titulo = vaga.find('h3').get_text(strip=True) if vaga.find('h3') else "Vaga"
            
            print(f"   👉 {titulo}")
            
            # Entra na vaga
            resp_vaga = requests.get(link, headers=headers)
            soup_vaga = BeautifulSoup(resp_vaga.text, 'html.parser')
            div_desc = soup_vaga.find('div', class_='wrapper-content-job-show')
            texto = div_desc.get_text() if div_desc else soup_vaga.get_text()
            
            # IA Analisa
            res_json = analisar_vaga(texto[:5000])
            
            try:
                dados = json.loads(res_json.strip().replace('```json', '').replace('```', ''))
                
                if dados.get('match'):
                    print("      ✅ MATCH! Notificando...")
                    msg = f"🎯 VAGA DE {termo.upper()}!\n\n💼 {dados.get('cargo')}\n📍 {dados.get('cidade')}\n🔗 {link}\n💡 {dados.get('motivo')}"
                    enviar_telegram(msg)
                else:
                    print(f"      ❌ {dados.get('motivo')}")
                    
            except:
                print("      ⚠️ Erro na leitura da IA")
            
            # Pausa curta entre vagas
            time.sleep(5) 

    except Exception as e:
        print(f"❌ Erro na categoria {termo}: {e}")

    # Pausa longa entre CATEGORIAS
    print("⏳ Trocando de categoria...")
    time.sleep(10)

print("\n🏁 Varredura completa!")
