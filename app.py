import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)


####################################################
### SEÇÃO 1: FUNÇÃO DE CORREÇÃO BASE (SIMPLIFICADA)
####################################################

def aplicar_correcoes_base(soup):
    """
    Aplica correções universais.
    (Corrige o 'outline' de foco).
    """
    print("Aplicando correções de base...")
    
    style_tag = soup.find('style')
    if style_tag and 'outline: none' in style_tag.string:
        style_tag.decompose() 
        print("Corrigido (Base): CSS do Outline removido.")
        
    return soup


####################################################
### SEÇÃO 2: FUNÇÕES DE PERFIL
####################################################

def aplicar_perfil_cego(soup):
    print("Aplicando Perfil Cego...")
    soup = aplicar_correcoes_base(soup)
    
    api_call_count = 0
    for img in soup.find_all('img'):
        if not img.get('alt'):
            if api_call_count > 0: 
                print(f"Aguardando 31 segundos para evitar limite de taxa (Erro 429)...")
                time.sleep(31) 
            img_url = img.get('src')
            alt_text = get_alt_text_from_ai(img_url) 
            img['alt'] = alt_text
            api_call_count += 1
            print(f"Corrigido (Cego): alt='{alt_text}'")

    botao_div = soup.find('div', class_='btn-primary')
    if botao_div:
        botao_div['role'] = 'button'
        botao_div['tabindex'] = '0'
        print("Corrigido (Cego): Botão-Div")

    for input_tag in soup.find_all(['input', 'textarea']):
        if not input_tag.has_attr('aria-label') and input_tag.get('placeholder'):
            placeholder = input_tag.get('placeholder')
            input_tag['aria-label'] = placeholder
            print(f"Corrigido (Cego): aria-label='{placeholder}'")
    
    return soup

def aplicar_perfil_dislexia(soup):
    print("Aplicando Perfil Dislexia...")
    soup = aplicar_correcoes_base(soup)
    
    head = soup.find('head')
    if head:
        new_style = soup.new_tag('style')
        new_style.string = """
        html { 
            font-size: 140% !important; 
        }
        body { 
            font-family: 'Verdana', sans-serif !important; 
            line-height: 1.6 !important; 
        }
        """
        head.append(new_style)
    
    paragrafo = soup.find('p', class_='lead')
    if paragrafo and paragrafo.string:
        texto_original = paragrafo.string
        texto_simplificado = get_simplified_text_from_ai(texto_original)
        paragrafo.string = texto_simplificado
        print("Corrigido (Dislexia): Texto simplificado")
        
    return soup

def aplicar_perfil_alto_contraste(soup):
    """Aplica um CSS de Alto Contraste (Modo Escuro) melhorado e corrigido."""
    print("Aplicando Perfil Alto Contraste (Versão 2.0)...")
    
    soup = aplicar_correcoes_base(soup)
    
    head = soup.find('head')
    if head:
        new_style = soup.new_tag('style')
        
        # --- NOVO CSS DE ALTO CONTRASTE ---
        new_style.string = """
        /* Fundo principal e cor de texto base (Branco no Preto) */
        body, .container, .card, .modal-content, .modal-body { 
            background-color: #000 !important; 
            color: #FFF !important; 
        }
        
        /* Áreas de navegação/rodapé um pouco mais claras */
        .navbar, footer, .modal-header, .modal-footer {
            background-color: #111 !important;
        }
        
        /* Títulos: Agora brancos, confiando no tamanho para hierarquia */
        h1, h2, h5, .modal-title {
             color: #FFF !important; 
        }

        /* Links: Amarelo brilhante. Este é o nosso novo destaque principal. */
        a, .nav-link {
            color: #FFFF00 !important; /* Amarelo Brilhante para todos os links */
            text-decoration: underline !important; /* Sublinhado para clareza extra */
        }

        /* Botões: Alto contraste (Branco no Preto) */
        .btn-primary, .btn-success, .btn {
            background-color: #FFF !important;
            color: #000 !important;
            border: 2px solid #FFF !important;
        }
        
        /* --- A CORREÇÃO DO BUG DO INPUT --- */
        input, textarea {
            background-color: #222 !important; /* Fundo escuro */
            color: #FFF !important; /* Texto digitado (branco) */
            border-color: #FFF !important;
        }
        
        /* Corrigindo o placeholder invisível */
        input::placeholder, textarea::placeholder {
            color: #BBB !important; /* Cinza claro para o placeholder */
            opacity: 1 !important;
        }

        /* Bordas */
        .border-bottom, .border-top {
            border-color: #444 !important;
        }
        """
        head.append(new_style)
        print("Corrigido (Alto Contraste): CSS v2.0 injetado.")
        
    return soup

def aplicar_perfil_surdo(soup):
    print("Aplicando Perfil Surdo (Transcrição de Áudio)...")
    soup = aplicar_correcoes_base(soup)
    
    for video_tag in soup.find_all('video'):
        source_tag = video_tag.find('source')
        if source_tag and source_tag.get('src'):
            video_url = source_tag.get('src')
            transcription_text = get_transcription_from_ai(video_url)
            
            transcription_div = soup.new_tag('div')
            transcription_div['class'] = 'alert alert-info mt-2' 
            transcription_div['role'] = 'status' 
            title_p = soup.new_tag('p')
            title_p.string = "Transcrição do Vídeo (Gerada por IA):"
            title_p['class'] = 'fw-bold'
            text_p = soup.new_tag('p')
            text_p.string = transcription_text
            transcription_div.append(title_p)
            transcription_div.append(text_p)
            
            video_parent_div = video_tag.parent
            if video_parent_div:
                video_parent_div.insert_after(transcription_div)
                print(f"Corrigido (Surdo): Transcrição adicionada para {video_url}")
    return soup

def aplicar_perfil_narracao_cegos(soup):
    print("Aplicando Perfil Narração para Cegos (Audio Description)...")
    soup = aplicar_correcoes_base(soup)
    
    for video_tag in soup.find_all('video'):
        source_tag = video_tag.find('source')
        if source_tag and source_tag.get('src'):
            video_url = source_tag.get('src')
            description_text = get_visual_description_from_ai(video_url)
            
            desc_div = soup.new_tag('div')
            desc_div['class'] = 'alert alert-warning mt-2' 
            desc_div['role'] = 'status' 
            title_p = soup.new_tag('p')
            title_p.string = "Narração de Vídeo para Cegos (Gerada por IA):"
            title_p['class'] = 'fw-bold'
            text_p = soup.new_tag('p')
            text_p.string = description_text
            desc_div.append(title_p)
            desc_div.append(text_p)
            
            video_parent_div = video_tag.parent
            if video_parent_div:
                video_parent_div.insert_after(desc_div)
                print(f"Corrigido (Narração): Narração adicionada para {video_url}")
    return soup

def aplicar_perfil_visao_limitada(soup, tipo_necessidade):
    print(f"Aplicando Perfil Visão Limitada: {tipo_necessidade}")
    soup = aplicar_correcoes_base(soup)
    
    head = soup.find('head')
    if not head:
        return soup
        
    new_style = soup.new_tag('style')
    css_string = ""
    
    if tipo_necessidade == "aumentar_texto":
        css_string = """
        html { 
            font-size: 140% !important; 
        }
        """
        print("Corrigido (Visão): Texto aumentado (proporcionalmente para 140%).")
        
    elif tipo_necessidade == "protanopia":
        css_string = """
        .btn-success {
            background-color: #FFA500 !important; /* Laranja */
            border-color: #FFA500 !important;
        }
        """
        print("Corrigido (Visão): Filtro Protanopia (Verde -> Laranja) aplicado.")

    elif tipo_necessidade == "deuteranopia":
        css_string = """
        .btn-success {
            background-color: #FFFF00 !important; /* Amarelo */
            border-color: #FFFF00 !important;
            color: #000 !important; /* Texto preto no botão amarelo */
        }
        """
        print("Corrigido (Visão): Filtro Deuteranopia (Verde -> Amarelo) aplicado.")

    new_style.string = css_string
    head.append(new_style)
    return soup


####################################################
### SEÇÃO 3: FUNÇÕES DE IA (O "CÉREBRO")
####################################################

def get_alt_text_from_ai(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status() 
        image_part = {
            "mime_type": response.headers['Content-Type'],
            "data": response.content
        }
        model = genai.GenerativeModel('models/gemini-2.5-pro') 
        prompt = """Descreva esta imagem para um usuário de leitor de tela cego. 
                    Seja conciso, no máximo 10 palavras. Responda em português.
                    NÃO inclua nenhuma frase de confirmação ou introdução. 
                    Forneça APENAS a descrição."""
        response = model.generate_content([prompt, image_part])
        print(f"API de Visão OK: {response.text.strip()}")
        return response.text.strip()
    except Exception as e:
        print(f"ERRO na API de Visão para {image_url}: {e}")
        return "Erro ao gerar descrição pela IA"

def get_simplified_text_from_ai(text):
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = """Simplifique o texto a seguir para uma pessoa com dislexia ou dificuldade cognitiva. 
                    Use frases curtas e diretas. Responda em português.
                    NÃO inclua nenhuma frase de confirmação ou introdução.
                    Forneça APENAS o texto simplificado."""
        response = model.generate_content(prompt)
        print(f"API de Texto OK: Texto simplificado.")
        return response.text.strip()
    except Exception as e:
        print(f"ERRO na API de Texto: {e}")
        return text 

def get_video_ai_response(video_url, task_prompt):
    local_filename = f"temp_video_{int(time.time())}.mp4"
    video_file = None 
    try:
        print(f"Baixando vídeo para tarefa: {video_url} ...")
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print("Download concluído.")

        print("Enviando vídeo para a IA...")
        video_file = genai.upload_file(path=local_filename, display_name="Hackathon Video")
        print(f"Upload iniciado. ID: {video_file.name}. Aguardando processamento...")

        while video_file.state.name == "PROCESSING":
            print("Vídeo ainda está processando... aguardando 5 segundos.")
            time.sleep(5)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name != "ACTIVE":
            raise Exception(f"Processamento do arquivo falhou no servidor. Estado: {video_file.state.name}")
        
        print("Vídeo está 'ACTIVE'. Solicitando IA...")
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        response = model.generate_content([task_prompt, video_file])
        
        print("Limpando arquivos temporários...")
        genai.delete_file(video_file.name) 
        os.remove(local_filename) 
        print(f"API de Vídeo OK: Texto gerado.")
        return response.text.strip()
    except Exception as e:
        print(f"ERRO GIGANTE na API de Vídeo: {e}")
        if os.path.exists(local_filename):
            os.remove(local_filename)
        if video_file and video_file.name:
             try:
                 genai.delete_file(video_file.name)
             except Exception as cleanup_e:
                 pass
        return "Erro ao processar o vídeo."

def get_transcription_from_ai(video_url):
    prompt = """Ouça o áudio deste vídeo e transcreva exatamente o que é dito. 
                Se não houver fala, descreva os sons (ex: '[música instrumental]'). 
                Responda em português.
                NÃO inclua nenhuma frase de confirmação ou introdução.
                Forneça APENAS a transcrição."""
    return get_video_ai_response(video_url, prompt)

def get_visual_description_from_ai(video_url):
    prompt = """Você é um narrador de audiodescrição para uma pessoa cega. 
                Assista a este vídeo e descreva apenas as informações visuais que não são óbvias pelo som. 
                O que está acontecendo visualmente? Responda em português.
                NÃO inclua nenhuma frase de confirmação ou introdução.
                Forneça APENAS a descrição."""
    return get_video_ai_response(video_url, prompt)


####################################################
### SEÇÃO 4: O SERVIDOR FLASK
####################################################

@app.route("/")
def hello():
    # página inicial simples para sabermos que o servidor está no ar
    return "Servidor do Adaptador de Acessibilidade está no ar!"

@app.route("/adaptar", methods=["POST"])
def handle_adaptation():
    print("\n--- REQUISIÇÃO RECEBIDA NO ENDPOINT /adaptar ---")
    
    # pega os dados que a "Parte 1" (a extensão) enviaria
    data = request.json
    html_quebrado = data.get("html_content")
    perfil = data.get("profile") # Ex: "cego", "dislexia", "visao_limitada"
    
    if not html_quebrado or not perfil:
        return jsonify({"erro": "Faltando 'html_content' ou 'profile'"}), 400

    # usa a lógica do seu adaptador
    soup = BeautifulSoup(html_quebrado, 'html.parser')
    html_corrigido = ""

    try:
        # chama a função de perfil apropriada
        if perfil == "cego":
            soup_corrigido = aplicar_perfil_cego(soup)
        elif perfil == "dislexia":
            soup_corrigido = aplicar_perfil_dislexia(soup)
        elif perfil == "alto_contraste":
            soup_corrigido = aplicar_perfil_alto_contraste(soup)
        elif perfil == "surdo":
            soup_corrigido = aplicar_perfil_surdo(soup)
        elif perfil == "narracao_cegos":
            soup_corrigido = aplicar_perfil_narracao_cegos(soup)
        elif perfil == "visao_limitada":
            # este perfil precisa de um segundo parâmetro
            tipo_necessidade = data.get("necessidade") # Ex: "aumentar_texto", "protanopia"
            if not tipo_necessidade:
                return jsonify({"erro": "Perfil 'visao_limitada' precisa de 'necessidade'"}), 400
            soup_corrigido = aplicar_perfil_visao_limitada(soup, tipo_necessidade)
        else:
            return jsonify({"erro": f"Perfil '{perfil}' desconhecido"}), 400
        
        html_corrigido = str(soup_corrigido)
        
        # retorna o HTML corrigido para a "Parte 1"
        print(f"--- REQUISIÇÃO CONCLUÍDA (Perfil: {perfil}) ---")
        return jsonify({"html_corrigido": html_corrigido})

    except Exception as e:
        print(f"ERRO 500 - FALHA GERAL NO PROCESSAMENTO: {e}")
        return jsonify({"erro": f"Erro interno do servidor: {e}"}), 500


####################################################
### SEÇÃO 5: EXECUÇÃO PRINCIPAL (Para rodar o servidor)
####################################################

if __name__ == "__main__":
    # Remove a lógica antiga de criar arquivos
    # e inicia o servidor Flask
    print("Iniciando o servidor Flask em http://127.0.0.1:5000")
    app.run(debug=True, port=5000)