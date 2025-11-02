import requests
import json
import os
import time

# --- CONFIGURAÇÃO DE ACESSO ---
URL_SERVIDOR = "http://127.0.0.1:5000/adaptar"
ARQUIVO_QUEBRADO = 'antes.html'
# -----------------------------

def rodar_teste(perfil_nome, perfil_id, config_data):
    """Função principal para enviar requisições ao servidor."""
    print(f"\n--- INICIANDO TESTE: {perfil_nome} ({perfil_id}) ---")
    
    # 1. Carrega o HTML (Assume que antes.html existe)
    try:
        with open(ARQUIVO_QUEBRADO, 'r', encoding='utf-8') as f:
            html_quebrado = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{ARQUIVO_QUEBRADO}' não encontrado.")
        return

    # 2. Prepara o Payload
    dados_para_enviar = {
        "html_content": html_quebrado,
        "profile": perfil_id,
        "config": config_data
    }

    # 3. Envia o Pedido
    try:
        if perfil_id in ["auditivo", "narracao_cegos"]:
            print("AVISO: O teste de vídeo/áudio pode levar 20-30s (download/upload/processamento da IA)...")
            
        response = requests.post(URL_SERVIDOR, json=dados_para_enviar)
        response.raise_for_status() # Lança erro para 4xx/5xx

        # 4. Pega a Resposta e Salva
        dados_da_resposta = response.json()
        html_corrigido = dados_da_resposta.get("html_corrigido")

        if html_corrigido:
            # Nomeia o arquivo com o ID e o nome do teste
            output_filename = f"resultado_modular_{perfil_id}_{perfil_nome.replace(' ', '_')}.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_corrigido)
            print(f"SUCESSO! Arquivo salvo como: {output_filename}")
        else:
            print("ERRO: Servidor retornou resposta vazia.")

    except requests.exceptions.ConnectionError:
        print("\n--- ERRO CRÍTICO: SERVIDOR OFF-LINE ---")
        print("Certifique-se de que 'python3 app.py' está rodando no Terminal 1.")
    except Exception as e:
        print(f"ERRO INESPERADO no teste: {e}")


def main():
    """Define e executa todos os casos de teste."""
    
    # --- DICIONÁRIO CENTRAL DE TESTES ---
    TESTES = [
        
        # --- PERFIL VISUAL (Condição: Cor e Brilho) ---
        {
            "nome": "VISUAL_1_Escala_e_Protanopia", 
            "id": "visual", 
            "config": {"aumentar_escala": True, "daltonismo_tipo": "protanopia", "cegueira_total": False, "sensibilidade_luz": False, "hipersensibilidade_visual": False}
        },
        {
            "nome": "VISUAL_2_Cegueira_Total", 
            "id": "visual", 
            "config": {"aumentar_escala": False, "daltonismo_tipo": None, "cegueira_total": True, "sensibilidade_luz": False, "hipersensibilidade_visual": False}
        },
        {
            "nome": "VISUAL_3_Hipersensibilidade_Visual", 
            "id": "visual", 
            "config": {"aumentar_escala": False, "daltonismo_tipo": None, "cegueira_total": False, "sensibilidade_luz": True, "hipersensibilidade_visual": True}
        },
        
        # --- PERFIL AUDITIVO (Condição: Som e Mídia) ---
        {
            "nome": "AUDITIVO_1_Transcricao_e_Autoplay", 
            "id": "auditivo", 
            "config": {"transcricao_surdez": True, "desativar_autoplay": True}
        },
        {
            "nome": "AUDITIVO_2_Apenas_Mudo_Total", 
            "id": "auditivo", 
            "config": {"transcricao_surdez": False, "desativar_autoplay": True}
        },

        # --- PERFIL COGNITIVO (Condição: Foco e Ordem) ---
        {
            "nome": "COGNITIVO_1_Simplificacao_e_Barra", 
            "id": "cognitivo", 
            "config": {"simplificar_texto": True, "barra_progresso": True, "destaque_botoes": True, "diminuir_espacamento": True}
        },
        {
            "nome": "COGNITIVO_2_Foco_Total_e_Botoes", 
            "id": "cognitivo", 
            "config": {"simplificar_texto": False, "barra_progresso": False, "destaque_botoes": True, "diminuir_espacamento": False}
        },
        
        # --- PERFIL MÍDIA AVANÇADA (Narração Visual) ---
        {
            "nome": "NARRACAO_1_Audiodescricao_IA", 
            "id": "narracao_cegos", 
            "config": {}
        },
    ]

    # Executa cada teste no dicionário
    for teste in TESTES:
        rodar_teste(teste["nome"], teste["id"], teste["config"])
        time.sleep(1) # Pequena pausa entre testes de configuração leve


if __name__ == "__main__":
    print("\n=========================================")
    print("INICIANDO SUITE DE TESTES MODULARES")
    print("=========================================")
    main()