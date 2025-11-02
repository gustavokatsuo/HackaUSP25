import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# Carrega a chave de API e configura o Gemini
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)

# Habilita CORS para permitir a comunicação com o front-end
CORS(app)

####################################################
### SEÇÃO 1: FUNÇÃO DE CORREÇÃO BASE E UTILITÁRIAS
####################################################

def aplicar_correcoes_base(soup):
    """
    Aplica correções universais.
    (Corrige o 'outline' de foco).
    """
    style_tag = soup.find('style')
    if style_tag and 'outline: none' in style_tag.string:
        style_tag.decompose() 
    return soup

def modulo_aplicar_estilos_base(soup, new_styles):
    """Função utilitária para injetar estilos CSS no <head>."""
    head = soup.find('head')
    if head:
        new_style_tag = soup.new_tag('style')
        new_style_tag.string = new_styles
        head.append(new_style_tag)
    return soup

# Funções de IA simplificadas para foco na lógica.

def get_alt_text_from_ai(image_url):
    try:
        response = genai.GenerativeModel('models/gemini-2.5-pro').generate_content(
            [f"Descreva esta imagem para uma pessoa cega, de forma concisa e útil, para ser usada como alt text. Responda APENAS com a descrição, sem introdução ou frase final.", image_url]
        )
        return response.text.strip()
    except Exception as e:
        return "Descrição gerada por IA falhou."
    
def get_simplified_text_from_ai(text):
    try:
        prompt = f"Simplifique o seguinte texto para o nível de leitura de uma criança, mantendo o significado principal. Responda APENAS com o texto simplificado. Texto original: '{text}'"
        response = genai.GenerativeModel('models/gemini-2.5-flash').generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Simplificação gerada por IA falhou."

def get_video_transcript_from_ai(video_source):
    try:
        prompt = f"Gere uma transcrição concisa (máx 3 frases) deste vídeo para acessibilidade. Responda APENAS com a transcrição. URL: {video_source}"
        response = genai.GenerativeModel('models/gemini-2.5-pro').generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Transcrição gerada por IA falhou."

def get_visual_description_from_ai(video_url):
    try:
        prompt = "Você é um narrador de audiodescrição para uma pessoa cega. Descreva as informações visuais que não são óbvias pelo som. APENAS a descrição em português."
        response = genai.GenerativeModel('models/gemini-2.5-pro').generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Descrição visual do vídeo da IA falhou."

####################################################
### SEÇÃO 2: FUNÇÕES DE PERFIL FINAL E MODULAR
####################################################

def aplicar_perfil_visual(soup, config):
    """
    PERFIL VISUAL (Configuração Modular)
    Implementa: Baixa Visão, Cegueira Total, Daltonismo, Hipersensibilidade Visual.
    """
    
    # 1. ESTILOS BASE (CSS)
    print(f"--- INICIANDO PERFIL VISUAL (MODULAR) ---")
    soup = aplicar_correcoes_base(soup)
    head = soup.find('head')
    if not head: return soup

    new_styles = ""
    
    # A. Aumentar Escala (Baixa Visão) - Ajustado para ser visível
    escala = config.get("aumentar_escala")
    ESCALAS = {"leve": "150%", "moderada": "200%", "severa": "250%"}
    if escala in ESCALAS:
        tamanho_escala = ESCALAS[escala]
        # Aplica o aumento na fonte raiz para escalar tudo
        new_styles += f"html {{ font-size: {tamanho_escala} !important; }}"
        print(f"Módulo: Baixa Visão (Escala {escala}) aplicado.")

    # B. Ajustes de Cores (Daltonismo ou Hipersensibilidade)
    daltonismo_tipo = config.get("daltonismo_tipo")
    
    if config.get("hipersensibilidade_visual"):
        # 1. Neutralização do Fundo e Cores (Filtro Monocromático de Baixa Luminosidade)
        new_styles += """
            body { 
                /* Força o fundo para preto neutro e sobrescreve o azul vibrante */
                background-color: #111111 !important; 
                color: #EEEEEE !important;
                /* Filtro extremo: Remove toda a cor e reduz o brilho */
                filter: grayscale(100%) brightness(0.85) contrast(1.1); 
                background-image: none !important; 
            }
            /* Remove as sombras e animações (ruído visual) */
            .card { box-shadow: none !important; }
            *, ::before, ::after { transition-property: none !important; animation: none !important; }
            
            /* Reintrodução de Foco Acessível (Branco sobre Preto) */
            .btn-primary, .btn-success { background-color: #555 !important; border: 3px solid #00FFFF !important; color: white !important; }
        """
        print("Módulo: Hipersensibilidade Visual (Neutralização Extrema) ativado.")

    # C. Daltonismo (Se não houver hipersensibilidade ativa)
    elif daltonismo_tipo == "protanopia":
        new_styles += ".btn-primary, .btn-success { background-color: #000080 !important; border-color: #000080 !important; color: white !important; }"
        new_styles += "body { filter: hue-rotate(180deg); }"
        print("Módulo: Daltonismo (Protanopia) aplicado.")
    
    # Injeta estilos no <head>
    if new_styles:
        soup = modulo_aplicar_estilos_base(soup, new_styles)

    # 2. ALT-TEXT PARA IMAGENS (Cegueira Total)
    if config.get("cegueira_total"):
        img_tags = soup.find_all('img')
        for img in img_tags:
            img_src = img.get('src')
            if img_src and not img.get('alt'):
                alt_text = get_alt_text_from_ai(img_src)
                img['alt'] = alt_text
                print(f"Alt Text Gerado para: {img_src}")
        print("Módulo: Alt Text (Cegueira Total) aplicado.")

    return soup

def aplicar_perfil_auditivo(soup, config):
    """
    PERFIL AUDITIVO (Configuração Modular)
    Implementa: Transcrição de Vídeo e Desativar Autoplay.
    """
    
    # 1. TRANSCRIÇÃO DE VÍDEO (Surdez Total)
    if config.get("transcricao_surdez"):
        video_tag = soup.find('video')
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and source_tag.get('src'):
                video_source = source_tag.get('src')
                print(f"Gerando transcrição para: {video_source}")
                
                # Chamada da IA
                transcricao_texto = get_video_transcript_from_ai(video_source)
                
                # Injeta a transcrição como uma caixa de texto
                transcricao_html = f"""
                <div style="background-color: #e0f7fa; border: 1px solid #00bcd4; padding: 15px; margin-top: 15px; border-radius: 5px;" aria-live="polite">
                    <strong>Transcrição (Gerada por IA):</strong>
                    <p>{transcricao_texto}</p>
                </div>
                """
                video_tag.parent.append(BeautifulSoup(transcricao_html, 'html.parser'))
                print("Módulo: Transcrição (Surdez Total) aplicada.")

    # 2. DESATIVAR AUTOPLAY (Hiperacusia ou Distração)
    if config.get("desativar_autoplay"):
        video_tag = soup.find('video')
        if video_tag:
            if video_tag.get('autoplay'):
                del video_tag['autoplay']
                print("Módulo: Autoplay desativado.")
            video_tag['preload'] = 'metadata'
            
    return soup

def aplicar_perfil_cognitivo(soup, config):
    """
    PERFIL COGNITIVO (Configuração Modular)
    Implementa: Simplificação de Texto (Dislexia), Barra de Progresso (TDAH) e Estilos de Foco.
    """
    print("--- INICIANDO PERFIL COGNITIVO (MODULAR) ---")
    soup = aplicar_correcoes_base(soup)
    head = soup.find('head')
    if not head: return soup
    
    # 1. MÓDULOS DE ESCALA (NOVO AQUI!)
    ESCALAS = {"leve": "150%", "moderada": "175%", "severa": "200%"}
    escala = config.get("aumentar_escala")
    
    # 2. SIMPLIFICAÇÃO DE TEXTO (IA)
    if config.get("simplificar_texto"):
        hero_section = soup.find('div', class_='col-lg-6')
        if hero_section:
            lead_paragraph = hero_section.find('p', class_='lead')
            if lead_paragraph:
                original_text = lead_paragraph.get_text().strip()
                if original_text:
                    simplified_text = get_simplified_text_from_ai(original_text)
                    lead_paragraph.string = simplified_text
                    print("Módulo: Simplificação de Texto (Dislexia) aplicado.")
                    
    # 3. ESTILOS GERAIS
    css_estilos = ""

    # A. Adiciona a escala se solicitada
    if escala in ESCALAS:
        tamanho_escala = ESCALAS[escala]
        css_estilos += f"html {{ font-size: {tamanho_escala} !important; }}"
        print(f"Módulo: Escala (Cognitivo) aplicado em {tamanho_escala}.")
    
    # B. Outros estilos cognitivos
    if config.get("destaque_botoes"):
        css_estilos += "button, .btn { border: 10px solid red !important; box-shadow: 0 0 15px red !important; }"
        print("Módulo: Destaque de Botões aplicado.")
        
    if config.get("diminuir_espacamento"):
        css_estilos += "body { letter-spacing: normal !important; line-height: 1.2 !important; }"
        print("Módulo: Espaçamento de linha diminuído.")

    if css_estilos:
        soup = modulo_aplicar_estilos_base(soup, css_estilos)


    # 4. BARRA DE PROGRESSO (TDAH) - Lógica de injeção HTML
    if config.get("barra_progresso"):
        body = soup.find('body')
        if body:
            progress_bar_html = """
            <div style="position: sticky; top: 0; width: 100%; height: 8px; background-color: #ddd; z-index: 1000;" role="progressbar" aria-valuenow="33" aria-valuemin="0" aria-valuemax="100">
                <div style="width: 33%; height: 100%; background-color: #4CAF50;"></div>
            </div>
            """
            progress_bar_soup = BeautifulSoup(progress_bar_html, 'html.parser').find('div')
            body.insert(0, progress_bar_soup)
            print("Módulo: Barra de progresso estática adicionada.")

    return soup

####################################################
### SEÇÃO 3: ROTEAMENTO PRINCIPAL (O ENDPOINT /adaptar)
####################################################

@app.route("/adaptar", methods=["POST"])
def handle_adaptation():
    print("\n--- REQUISIÇÃO RECEBIDA NO ENDPOINT /adaptar ---")
    
    try:
        data = request.json
        perfil = data.get("profile")
        config = data.get("config", {}) 
        
        html_quebrado = data.get("html_content") 

        if not html_quebrado:
             return jsonify({"erro": "Faltando 'html_content' no payload (Verifique Finished.html)."}), 400

        soup = BeautifulSoup(html_quebrado, 'html.parser') 
        soup = aplicar_correcoes_base(soup)
        
        soup_corrigido = soup

        # Roteamento dos Perfis
        if perfil == "visual":
            soup_corrigido = aplicar_perfil_visual(soup, config)
            print(f"--- INICIANDO PERFIL VISUAL (MODULAR) ---")
        elif perfil == "auditivo":
            soup_corrigido = aplicar_perfil_auditivo(soup, config)
            print(f"--- INICIANDO PERFIL AUDITIVO (MODULAR) ---\n")
        elif perfil == "cognitivo":
            soup_corrigido = aplicar_perfil_cognitivo(soup, config)
            print(f"--- INICIANDO PERFIL COGNITIVO (MODULAR) ---")
        else:
            return jsonify({"erro": f"Perfil '{perfil}' desconhecido"}), 400
        
        html_corrigido = str(soup_corrigido)
        
        print(f"--- REQUISIÇÃO CONCLUÍDA (Perfil: {perfil}) ---")
        return jsonify({"html_corrigido": html_corrigido})

    except Exception as e:
        # Imprime o erro no console do Flask para diagnóstico
        print(f"ERRO 500 - FALHA GERAL NO PROCESSAMENTO: {e}")
        return jsonify({"erro": f"Erro interno do servidor: {e}"}), 500


####################################################
### SEÇÃO 4: EXECUÇÃO PRINCIPAL (Para rodar o servidor)
####################################################

if __name__ == "__main__":
    print(f"Iniciando o servidor Flask em http://127.0.0.1:5000")
    app.run(debug=True)
