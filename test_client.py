import requests
import json
import os
import time

# --- CONFIGURAÇÃO DO TESTE (MUDE APENAS ESTAS TRÊS LINHAS) ---

# PERFIL (profile): Deve ser 'visual', 'auditivo', 'cognitivo', ou 'narracao_cegos'
PERFIL_PARA_TESTAR = "visual" 

# CONFIG (config): Dicionário com as opções ativadas
# EX: Para aumentar a fonte E corrigir o daltonismo protanopia
CONFIG_PARA_TESTAR = {
    "aumentar_escala": "moderada",           # Baixa Visão, "leve", "moderada", "severa"
    "daltonismo_tipo": None,   # Daltonismo (opções: "protanopia" ou "deuteranopia")
    "cegueira_total": False,            # Cegueira Total (Alt-Text/Navegação)
    "sensibilidade_luz": False,        # Sensibilidade (Filtro Sépia)
    
    # Opções Auditivas/Cognitivas (devem ser False se o perfil for 'visual')
    "transcricao_surdez": False,
    "desativar_autoplay": False,
    "simplificar_texto": False,
    "barra_progresso": False,
    "destaque_botoes": False,
    "cores_neutras": True
}

# -------------------------------------------------------------

def testar_servidor():
    """Roda um único teste contra o servidor Flask."""
    print(f"--- Testando Perfil: {PERFIL_PARA_TESTAR} ---")
    
    # 1. Carrega o site quebrado do disco
    try:
        # Verifica se o arquivo existe no disco
        if not os.path.exists('antes.html'):
            print("\nERRO: O arquivo 'antes.html' não foi encontrado.")
            print("Certifique-se de que ele está na pasta correta.")
            return

        with open('antes.html', 'r', encoding='utf-8') as f:
            html_quebrado = f.read()
    except Exception as e:
        print(f"ERRO ao carregar 'antes.html': {e}")
        return

    # 2. Prepara o "pedido" (payload JSON) para a API
    dados_para_enviar = {
        "html_content": html_quebrado,
        "profile": PERFIL_PARA_TESTAR,
        "config": CONFIG_PARA_TESTAR # <-- NOVO: ENVIANDO O DICIONÁRIO DE CONFIGURAÇÃO
    }

    # 3. Manda o pedido para o seu servidor Flask
    try:
        url_do_servidor = "http://127.0.0.1:5000/adaptar"
        response = requests.post(url_do_servidor, json=dados_para_enviar)
        
        response.raise_for_status() # Garante que não deu erro 404 ou 500

        # 4. Pega a resposta (o HTML corrigido)
        dados_da_resposta = response.json()
        html_corrigido = dados_da_resposta.get("html_corrigido")

        # 5. Salva o resultado
        if html_corrigido:
            # Nomeia o arquivo de saída de forma mais descritiva
            output_filename = f"resultado_do_servidor_{PERFIL_PARA_TESTAR}_modular.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_corrigido)
            print(f"\nSUCESSO! Servidor funcionando.")
            print(f"Arquivo gerado: '{output_filename}'")
            print(f"Verifique o Terminal 1 para ver os logs de correção.")
        else:
            print("ERRO: O servidor retornou uma resposta vazia.")

    except requests.exceptions.ConnectionError:
        print("\n--- ERRO DE CONEXÃO ---")
        print("Servidor Flask não encontrado. Você rodou 'python3 app.py' no Terminal 1?")
    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---")
        print(e)

if __name__ == "__main__":
    testar_servidor()