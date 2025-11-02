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
    # Removemos o bloco de estilo que desativa o outline de foco
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

def get_alt_text_from_ai(image_url):
    """Gera Alt Text (descrição da imagem) usando o Gemini."""
    try:
        response = genai.GenerativeModel('gemini-2.5-flash').generate_content(
            [f"Descreva esta imagem para uma pessoa cega, de forma concisa e útil, para ser usada como alt text. Responda APENAS com a descrição, sem introdução ou frase final.", image_url]
        )
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao gerar alt text: {e}")
        return "Descrição gerada por IA falhou."
    
def get_simplified_text_from_ai(text):
    """Simplifica um bloco de texto usando o Gemini."""
    try:
        prompt = f"Simplifique o seguinte texto para o nível de leitura de uma criança, mantendo o significado principal. Responda APENAS com o texto simplificado. Texto original: '{text}'"
        response = genai.GenerativeModel('gemini-2.5-flash').generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao simplificar texto: {e}")
        return "Simplificação gerada por IA falhou."

def get_video_transcript_from_ai(video_source):
    """Gera uma transcrição simples para um vídeo."""
    try:
        # Nota: O Gemini 2.5 Pro é usado para maior precisão em tarefas mais complexas.
        prompt = f"Gere uma transcrição concisa (máx 3 frases) deste vídeo para acessibilidade. Responda APENAS com a transcrição. URL: {video_source}"
        response = genai.GenerativeModel('gemini-2.5-pro').generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao gerar transcrição: {e}")
        return "Transcrição gerada por IA falhou."


####################################################
### SEÇÃO 2: FUNÇÕES DE PERFIL FINAL E MODULAR
####################################################

def aplicar_perfil_visual(soup, config):
    """
    PERFIL VISUAL (Configuração Modular)
    Implementa: Baixa Visão, Cegueira Total, Daltonismo, Hipersensibilidade Visual.
    """
    
    # 1. ESTILOS BASE (CSS)
    new_styles = ""
    
    # A. Aumentar Escala (Baixa Visão)
    escala = config.get("aumentar_escala")
    if escala == "moderada":
        new_styles += "body { font-size: 160% !important; line-height: 1.6 !important; }\n"
        print("Módulo: Baixa Visão (Moderada) aplicado.")
    elif escala == "grave":
        new_styles += "body { font-size: 190% !important; line-height: 1.8 !important; letter-spacing: 0.05em; }\n"
        print("Módulo: Baixa Visão (Grave) aplicado.")

    # B. Daltonismo e Hipersensibilidade (Filtros CSS)
    daltonismo_tipo = config.get("daltonismo_tipo")
    if daltonismo_tipo == "protanopia":
        # Nota: Filtros de daltonismo exigem injeção de SVG na tag <body> ou <svg> na página,
        # mas aqui simplificamos com um filtro de matiz para demonstração.
        new_styles += "body { filter: hue-rotate(180deg); }\n"
        print("Módulo: Daltonismo (Protanopia) aplicado.")
    elif daltonismo_tipo == "deuteranopia":
        new_styles += "body { filter: hue-rotate(90deg); }\n"
        print("Módulo: Daltonismo (Deuteranopia) aplicado.")
    elif config.get("sensibilidade_luz"):
        new_styles += "body { background-color: #222 !important; color: #EEE !important; filter: invert(0.8); }\n"
        print("Módulo: Hipersensibilidade/Luz aplicado.")

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

    # 4. HIPERSENSIBILIDADE VISUAL / CORES NEUTRAS E ANIMAÇÕES (A VERSÃO EXTRAORDINÁRIA)
    if config.get("hipersensibilidade_visual"):
        
        # A. Reduzir cores vibrantes (MONOCROMÁTICO + BRILHO)
        styles += """
            body { 
                /* O filtro mais forte: Remove a saturação total e aumenta o contraste/brilho */
                filter: grayscale(100%) brightness(1.2) contrast(1.1); 
                background-image: none !important; /* Limpa o fundo */
            }
        """
        
        # B. Desativar Animações (Foco/Hipersensibilidade)
        styles += """
            *, ::before, ::after {
                transition-property: none !important;
                animation: none !important;
                /* Remove sombras e degradês que causam ruído visual */
                box-shadow: none !important; 
            }
        """
        # C. Reintrodução de Cor Acessível (Brilho nos botões)
        styles += ".btn-primary, .btn-success { filter: none !important; border: 3px solid #0000FF !important; }"
        
        print("Módulo: Hipersensibilidade Visual (Monocromático Extremo/Sem Animação) ativado.")

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

    # 1. SIMPLIFICAÇÃO DE TEXTO (Dislexia)
    if config.get("simplificar_texto"):
        # Encontra o parágrafo principal do Hero Section para simplificação
        hero_section = soup.find('div', class_='col-lg-6')
        if hero_section:
            lead_paragraph = hero_section.find('p', class_='lead')
            if lead_paragraph:
                original_text = lead_paragraph.get_text().strip()
                if original_text:
                    simplified_text = get_simplified_text_from_ai(original_text)
                    lead_paragraph.string = simplified_text
                    print("Módulo: Simplificação de Texto (Dislexia) aplicado.")
                    
        # Injeta CSS de espaçamento/fonte para Dislexia
        new_styles = "p, h1, h2, h3, li { line-height: 1.6 !important; letter-spacing: 0.1em; font-family: sans-serif !important; }"
        soup = modulo_aplicar_estilos_base(soup, new_styles)


    # 2. BARRA DE PROGRESSO (TDAH / Orientação) - CORREÇÃO FINAL
    # *AVISO*: Injetamos apenas o HTML estático para evitar falhas de parsing do JavaScript.
    if config.get("barra_progresso"):
        body = soup.find('body')
        if body:
            # HTML da Barra (Estático) - Sem JS para evitar quebras.
            progress_bar_html = """
            <div style="position: sticky; top: 0; width: 100%; height: 8px; background-color: #ddd; z-index: 1000;" role="progressbar" aria-valuenow="33" aria-valuemin="0" aria-valuemax="100">
                <div style="width: 33%; height: 100%; background-color: #4CAF50;"></div>
            </div>
            """
            
            # Injeção no TOPO do BODY
            progress_bar_soup = BeautifulSoup(progress_bar_html, 'html.parser').find('div')
            body.insert(0, progress_bar_soup)
            
            print("Módulo: Barra de progresso estática adicionada (Não animada, mas não quebra o HTML).")

    # 3. DESTAQUE DE BOTÕES (Hipersensibilidade Sensorial / Foco)
    if config.get("destaque_botoes"):
        new_styles = "button, .btn { border: 3px solid red !important; box-shadow: 0 0 10px red !important; }"
        soup = modulo_aplicar_estilos_base(soup, new_styles)
        print("Módulo: Destaque de Botões aplicado.")

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
        
        # O HTML bruto está sendo enviado pelo cliente no campo 'html_content'
        html_quebrado = data.get("html_content") 

        if not html_quebrado:
             return jsonify({"erro": "Faltando 'html_content' no payload (Verifique Finished.html)."}), 400

        # Aplica a correção de segurança (remove o outline: none)
        soup = BeautifulSoup(html_quebrado, 'html.parser') 
        soup = aplicar_correcoes_base(soup)
        
        soup_corrigido = soup

        # Roteamento dos Perfis
        if perfil == "visual":
            soup_corrigido = aplicar_perfil_visual(soup, config)
            print(f"--- INICIANDO PERFIL VISUAL (MODULAR) ---")
        elif perfil == "auditivo":
            soup_corrigido = aplicar_perfil_auditivo(soup, config)
            print(f"--- INICIANDO PERFIL AUDITIVO (MODULAR) ---")
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
        # Retorna uma mensagem de erro para o cliente
        return jsonify({"erro": f"Erro interno do servidor: {e}"}), 500


####################################################
### SEÇÃO 4: EXECUÇÃO PRINCIPAL (Para rodar o servidor)
####################################################

if __name__ == "__main__":
    print(f"Iniciando o servidor Flask em http://127.0.0.1:5000")
    # debug=True é essencial para recarregar o servidor automaticamente
    app.run(debug=True)