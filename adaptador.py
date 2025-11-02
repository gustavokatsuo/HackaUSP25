import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


####################################################
### SEÇÃO 1: FUNÇÃO DE CORREÇÃO BASE
####################################################

def aplicar_correcoes_base(soup):
    """
    Aplica correções universais.
    (Corrige o 'outline' de foco).
    """
    print("Aplicando correções de base...")
    
    # corrige o 'outline: none' que quebra a navegação por teclado
    style_tag = soup.find('style')
    if style_tag and 'outline: none' in style_tag.string:
        style_tag.decompose()
        print("Corrigido (Base): CSS do Outline removido.")
        
    return soup


####################################################
### SEÇÃO 2: FUNÇÕES DE PERFIL DE ACESSIBILIDADE
####################################################

def aplicar_perfil_cego(soup):
    """Corrige problemas de navegação e alt text para leitores de tela."""
    print("Aplicando Perfil Cego...")
    
    soup = aplicar_correcoes_base(soup)

    # corrigir imagens sem 'alt'
    api_call_count = 0
    for img in soup.find_all('img'):
        if not img.get('alt'): # Se não tiver 'alt'
            
            if api_call_count > 0:
                print(f"Aguardando 31 segundos para evitar limite de taxa (Erro 429)...")
                time.sleep(31)

            img_url = img.get('src')
            alt_text = get_alt_text_from_ai(img_url) 
            img['alt'] = alt_text
            api_call_count += 1
            print(f"Corrigido: alt='{alt_text}'")

    # corrigir BOTÃO-DIV
    botao_div = soup.find('div', class_='btn-primary')
    if botao_div:
        botao_div['role'] = 'button'
        botao_div['tabindex'] = '0'
        print("Corrigido: Botão-Div")

    # corrigir formulário sem label
    for input_tag in soup.find_all(['input', 'textarea']):
        if not input_tag.has_attr('aria-label') and input_tag.get('placeholder'):
            placeholder = input_tag.get('placeholder')
            input_tag['aria-label'] = placeholder
            print(f"Corrigido: aria-label='{placeholder}'")
    
    return soup

def aplicar_perfil_dislexia(soup):
    """Muda fonte e simplifica texto para dificuldade cognitiva."""
    print("Aplicando Perfil Dislexia...")
    
    soup = aplicar_correcoes_base(soup)

    # mudar a fonte
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
    
    # simplificar texto
    paragrafo = soup.find('p', class_='lead')
    if paragrafo and paragrafo.string:
        texto_original = paragrafo.string
        texto_simplificado = get_simplified_text_from_ai(texto_original)
        paragrafo.string = texto_simplificado
        print("Corrigido: Texto simplificado")
        
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
    """Procura por tags <video> e injeta uma transcrição de texto abaixo delas."""
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
                print(f"Corrigido: Transcrição adicionada para {video_url}")
    
    return soup

def aplicar_perfil_narracao_cegos(soup):
    """Procura por <video> e injeta uma DESCRIÇÃO VISUAL (audiodescrição)."""
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
                print(f"Corrigido: Narração adicionada para {video_url}")
    
    return soup

def aplicar_perfil_visao_limitada(soup, tipo_necessidade):
    """
    Aplica filtros de CSS baseados na necessidade do usuário (Tamanho ou Daltonismo).
    """
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
        print("Corrigido (Visão): Texto aumentado (proporcionalmente).")
        
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
### SEÇÃO 3: FUNÇÕES DE IA
####################################################

def get_alt_text_from_ai(image_url):
    """Usa o Gemini 2.5 Pro para descrever uma imagem a partir de uma URL."""
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
    """Usa o Gemini 2.5 Flash para simplificar um texto."""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"Simplifique o texto a seguir para uma pessoa com dislexia ou dificuldade cognitiva. Use frases curtas e diretas. Responda em português. Texto original: '{text}'"
        response = model.generate_content(prompt)
        
        print(f"API de Texto OK: Texto simplificado.")
        return response.text.strip()
        
    except Exception as e:
        print(f"ERRO na API de Texto: {e}")
        return text 

def get_video_ai_response(video_url, task_prompt):
    """Função genérica para Download, Upload, Processamento de Vídeo e Limpeza."""
    local_filename = f"temp_video_{int(time.time())}.mp4"
    video_file = None 

    try:
        # DOWNLOAD
        print(f"Baixando vídeo para tarefa: {video_url} ...")
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print("Download concluído.")

        # UPLOAD E ESPERA
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

        # CHAMADA DA API
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        response = model.generate_content([task_prompt, video_file])

        # LIMPEZA
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
    """Pede à IA para OUVIR e TRANSCREVER o vídeo."""
    
    prompt = """Ouça o áudio deste vídeo e transcreva exatamente o que é dito. 
                Se não houver fala, descreva os sons (ex: '[música instrumental]'). 
                Responda em português.
                NÃO inclua nenhuma frase de confirmação ou introdução.
                Forneça APENAS a transcrição."""
                
    return get_video_ai_response(video_url, prompt)

def get_visual_description_from_ai(video_url):
    """Pede à IA para ASSISTIR e DESCREVER o vídeo."""
    
    prompt = """Você é um narrador de audiodescrição para uma pessoa cega. 
                Assista a este vídeo e descreva apenas as informações visuais que não são óbvias pelo som. 
                O que está acontecendo visualmente? Responda em português.
                NÃO inclua nenhuma frase de confirmação ou introdução.
                Forneça APENAS a descrição."""
                
    return get_video_ai_response(video_url, prompt)


####################################################
### SEÇÃO 4: EXECUÇÃO PRINCIPAL
####################################################

if __name__ == "__main__":
    
    # carrega o arquivo "quebrado"
    try:
        with open('antes.html', 'r', encoding='utf-8') as f:
            soup_original = BeautifulSoup(f, 'html.parser')
        print("Arquivo 'antes.html' carregado com sucesso.")
    except FileNotFoundError:
        print("\n!!! ERRO CRÍTICO !!!")
        print("O arquivo 'antes.html' não foi encontrado.")
        print("Certifique-se que ele está na mesma pasta que o adaptador.py")
        print("Lembre-se que 'antes.html' deve conter o <video>.\n")
        exit()

    # roda o perfil 1 (cego)
    print("\n--- INICIANDO PERFIL 1: CEGO ---")
    soup_para_cego = BeautifulSoup(str(soup_original), 'html.parser') 
    soup_corrigido_cego = aplicar_perfil_cego(soup_para_cego)
    with open('depois_perfil_cego.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_corrigido_cego))
    print("Arquivo 'depois_perfil_cego.html' salvo!\n")

    # roda o perfil 2 (dislexia)
    print("--- INICIANDO PERFIL 2: DISLEXIA ---")
    soup_para_dislexia = BeautifulSoup(str(soup_original), 'html.parser')
    soup_corrigido_dislexia = aplicar_perfil_dislexia(soup_para_dislexia)
    with open('depois_perfil_dislexia.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_corrigido_dislexia))
    print("Arquivo 'depois_perfil_dislexia.html' salvo!\n")

    # roda o perfil 3 (alto contraste)
    print("--- INICIANDO PERFIL 3: ALTO CONTRASTE ---")
    soup_para_contraste = BeautifulSoup(str(soup_original), 'html.parser')
    soup_corrigido_contraste = aplicar_perfil_alto_contraste(soup_para_contraste)
    with open('depois_perfil_alto_contraste.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_corrigido_contraste))
    print("Arquivo 'depois_perfil_alto_contraste.html' salvo!\n")

    # roda o perfil 4 (surdo)
    print("--- INICIANDO PERFIL 4: SURDO (TRANSCRIÇÃO) ---")
    soup_para_surdo = BeautifulSoup(str(soup_original), 'html.parser')
    soup_corrigido_surdo = aplicar_perfil_surdo(soup_para_surdo)
    with open('depois_perfil_surdo.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_corrigido_surdo))
    print("Arquivo 'depois_perfil_surdo.html' salvo!\n")

    # roda o perfil 5 (narração cegos)
    print("--- INICIANDO PERFIL 5: NARRAÇÃO CEGOS ---")
    soup_para_narracao = BeautifulSoup(str(soup_original), 'html.parser')
    soup_corrigido_narracao = aplicar_perfil_narracao_cegos(soup_para_narracao)
    with open('depois_perfil_narracao_cegos.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_corrigido_narracao))
    print("Arquivo 'depois_perfil_narracao_cegos.html' salvo!\n")

    # roda o perfil 6 (visão limitada - 3 simulações)
    
    print("--- INICIANDO PERFIL 6a: AUMENTAR TEXTO ---")
    soup_aumentar_texto = BeautifulSoup(str(soup_original), 'html.parser')
    soup_aumentar_texto = aplicar_perfil_visao_limitada(soup_aumentar_texto, "aumentar_texto")
    with open('depois_perfil_aumentar_texto.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_aumentar_texto))
    print("Arquivo 'depois_perfil_aumentar_texto.html' salvo!\n")

    print("--- INICIANDO PERFIL 6b: DALTONISMO (PROTANOPIA) ---")
    soup_protanopia = BeautifulSoup(str(soup_original), 'html.parser')
    soup_protanopia = aplicar_perfil_visao_limitada(soup_protanopia, "protanopia")
    with open('depois_perfil_protanopia.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_protanopia))
    print("Arquivo 'depois_perfil_protanopia.html' salvo!\n")
    
    print("--- INICIANDO PERFIL 6c: DALTONISMO (DEUTERANOPIA) ---")
    soup_deuteranopia = BeautifulSoup(str(soup_original), 'html.parser')
    soup_deuteranopia = aplicar_perfil_visao_limitada(soup_deuteranopia, "deuteranopia")
    with open('depois_perfil_deuteranopia.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_deuteranopia))
    print("Arquivo 'depois_perfil_deuteranopia.html' salvo!\n")

    print("--- PROCESSAMENTO CONCLUÍDO ---")
    print("Total de 8 arquivos 'depois_perfil_...' gerados com sucesso.")