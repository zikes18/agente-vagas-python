import requests
from bs4 import BeautifulSoup
from google import genai
import time
import os
import json
from datetime import datetime

# --- CONFIGURAÇÃO E CONSTANTES ---
# Tenta pegar do ambiente (Nuvem/Seguro), senão usa string vazia (Local/Teste)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "SUA_CHAVE_AQUI_SE_FOR_TESTE_LOCAL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "SEU_TOKEN_AQUI_SE_FOR_TESTE_LOCAL")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "SEU_ID_AQUI_SE_FOR_TESTE_LOCAL")

ARQUIVO_HISTORICO = "historico_vagas.json"

TERMOS_BUSCA = [
    "python", "java", "sql", "estagio", "inteligencia-artificial",
    "javascript", "node", "angular", "react", "react-native",
    "typescript", "spring", "django", "flask", "fastapi",
    "bootstrap", "full-stack", "automacao", "c-sharp", "c-plus-plus"
]

class AgenteVagas:
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.historico = self.carregar_historico()

    def carregar_historico(self):
        """Carrega a lista de vagas já enviadas para não repetir."""
        if os.path.exists(ARQUIVO_HISTORICO):
            try:
                with open(ARQUIVO_HISTORICO, "r") as f:
                    return set(json.load(f)) # Set é mais rápido para buscar
            except:
                return set()
        return set()

    def salvar_historico(self):
        """Salva o histórico atualizado no arquivo."""
        try:
            with open(ARQUIVO_HISTORICO, "w") as f:
                json.dump(list(self.historico), f)
        except Exception as e:
            print(f"⚠️ Erro ao salvar histórico: {e}")

    def enviar_telegram(self, mensagem):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"❌ Erro Telegram: {e}")

    def analisar_com_ia(self, texto_vaga):
        prompt = """
        Você é um Recrutador Tech Senior. Analise a vaga.
        CRITÉRIOS DE MATCH:
        1. Nível: Júnior, Estágio, Trainee (Recusar Sênior/Pleno > 2 anos).
        2. Local: DF (Brasília), Curitiba ou 100% Remoto.

        Responda APENAS JSON:
        {"cargo": "Titulo", "cidade": "Local", "match": true/false, "motivo": "Resumo < 10 palavras"}
        """
        
        tentativas = 0
        while tentativas < 3:
            try:
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt + "\n\n" + texto_vaga
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "503" in str(e):
                    print(f"   ⏳ API cheia. Pause de 60s... ({tentativas+1}/3)")
                    time.sleep(60)
                    tentativas += 1
                else:
                    return ""
        return ""

    def processar_categoria(self, termo):
        url = f"https://programathor.com.br/jobs-{termo}"
        print(f"\n📂 CATEGORIA: {termo.upper()}")
        
        try:
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            vagas = soup.find_all('div', class_='cell-list')

            if not vagas:
                print("   📭 Nenhuma vaga.")
                return

            print(f"   🔎 Encontrei {len(vagas)} vagas. Verificando novas...")
            
            # Analisa até 5 vagas por categoria
            for vaga in vagas[:5]:
                tag_a = vaga.find('a')
                if not tag_a: continue
                
                link = "https://programathor.com.br" + tag_a['href']
                
                # --- FILTRO DE MEMÓRIA (O Pulo do Gato 🐱) ---
                # Se o link já estiver no histórico, pula imediatamente!
                if link in self.historico:
                    print(f"   ⏭️ Já analisada: {link.split('/')[-1]}")
                    continue

                titulo = vaga.find('h3').get_text(strip=True) if vaga.find('h3') else "Vaga"
                print(f"   👉 Analisando: {titulo}")

                # Extração
                r_vaga = requests.get(link, headers=self.headers)
                s_vaga = BeautifulSoup(r_vaga.text, 'html.parser')
                div_desc = s_vaga.find('div', class_='wrapper-content-job-show')
                texto = div_desc.get_text() if div_desc else s_vaga.get_text()

                # Inteligência
                res_json = self.analisar_com_ia(texto[:4000])
                
                try:
                    dados = json.loads(res_json.strip().replace('```json', '').replace('```', ''))
                    
                    # Salva no histórico INDEPENDENTE se for match ou não
                    # (Para não gastar IA analisando vaga ruim duas vezes)
                    self.historico.add(link)
                    
                    if dados.get('match'):
                        print("      ✅ MATCH! Notificando...")
                        msg = f"🎯 *VAGA ENCONTRADA!* ({termo.upper()})\n\n🏢 *{dados.get('cargo')}*\n📍 {dados.get('cidade')}\n🔗 [Ver Vaga]({link})\n\n💡 _{dados.get('motivo')}_"
                        self.enviar_telegram(msg)
                    else:
                        print(f"      ❌ {dados.get('motivo')}")

                except:
                    pass
                
                # Salva o arquivo a cada iteração para garantir
                self.salvar_historico()
                time.sleep(5) # Delay ético

        except Exception as e:
            print(f"❌ Erro em {termo}: {e}")

    def iniciar(self):
        print(f"🚀 Agente Vagas Pro Iniciado at {datetime.now()}")
        
        # --- DETECÇÃO INTELIGENTE DE AMBIENTE ---
        # Se estiver no GitHub Actions, a variável 'GITHUB_ACTIONS' existe e é 'true'.
        modo_automatico = os.environ.get('GITHUB_ACTIONS') == 'true'

        lista_execucao = []

        if modo_automatico:
            print("🤖 Modo Nuvem Detectado: Executando varredura completa.")
            lista_execucao = TERMOS_BUSCA
        else:
            # Menu Interativo para Local
            print("\n📋 MENU DE CATEGORIAS:")
            print("0. [TODAS]")
            for i, termo in enumerate(TERMOS_BUSCA):
                print(f"{i+1}. {termo.upper()}")
            
            try:
                escolha = input("\nEscolha (ou Enter para Todas): ")
                if not escolha or escolha == '0':
                    lista_execucao = TERMOS_BUSCA
                else:
                    idx = int(escolha) - 1
                    if 0 <= idx < len(TERMOS_BUSCA):
                        lista_execucao = [TERMOS_BUSCA[idx]]
                    else:
                        print("Opção inválida. Rodando todas.")
                        lista_execucao = TERMOS_BUSCA
            except:
                lista_execucao = TERMOS_BUSCA

        # Execução
        for termo in lista_execucao:
            self.processar_categoria(termo)
            print("⏳ ...")
            time.sleep(2)
        
        print("🏁 Fim da execução.")

# --- ENTRY POINT ---
if __name__ == "__main__":
    bot = AgenteVagas()
    bot.iniciar()
