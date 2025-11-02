import requests
import json
import os
import time

URL_SERVIDOR = "http://127.0.0.1:5000/adaptar"
ARQUIVO_QUEBRADO = 'antes.html'

def rodar_teste(perfil_nome, perfil_id, config_data):
    """Função principal para enviar requisições ao servidor."""
    print(f"\n--- INICIANDO TESTE: {perfil_nome} ({perfil_id}) ---")
    
    # 1. Carrega o site quebrado do disco
    try:
        if not os.path.exists(ARQUIVO_QUEBRADO):
            print(f"\nERRO: O arquivo '{ARQUIVO_QUEBRADO}' não foi encontrado.")
            return

        with open(ARQUIVO_QUEBRADO, 'r', encoding='utf-8') as f:
            html_quebrado = f.read()
    except Exception as e:
        print(f"ERRO ao carregar '{ARQUIVO_QUEBRADO}': {e}")
        return

    # 2. Prepara o "pedido" (payload JSON) para a API
    dados_para_enviar = {
        "html_content": html_quebrado,
        "profile": perfil_id,
        "config": config_data
    }

    # 3. Manda o pedido para o seu servidor Flask
    try:
        url_do_servidor = URL_SERVIDOR
        response = requests.post(url_do_servidor, json=dados_para_enviar)
        
        response.raise_for_status() # Garante que não deu erro 404 ou 500

        # 4. Pega a resposta (o HTML corrigido)
        dados_da_resposta = response.json()
        html_corrigido = dados_da_resposta.get("html_corrigido")

        # 5. Salva o resultado
        if html_corrigido:
            # Nomeia o arquivo de saída de forma mais descritiva
            output_filename = f"resultado_modular_{perfil_id}_{perfil_nome.replace(' ', '_')}.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_corrigido)
            print(f"SUCESSO! Servidor funcionando.")
            print(f"Arquivo gerado: '{output_filename}'")
        else:
            print("ERRO: O servidor retornou uma resposta vazia.")

    except requests.exceptions.ConnectionError:
        print("\n--- ERRO CRÍTICO: SERVIDOR OFF-LINE ---")
        print(f"Servidor Flask não encontrado em {URL_SERVIDOR}. Você rodou 'python3 app.py' no Terminal 1?")
    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---\n{e}")


def main():
    """Define e executa o teste de combinação solicitada."""
    
    TESTES = [
        # TESTE SOLICITADO: Combinação de Baixa Visão (Escala) e Hipersensibilidade (Cores Neutras/Brilho)
        {
            "nome": "VISUAL_Escala_e_Neutras_Severas", 
            "id": "visual", 
            "config": {
                "aumentar_escala": "moderada", # Aumento de fonte visível
                "daltonismo_tipo": None,
                "cegueira_total": False,
                "sensibilidade_luz": False,
                "hipersensibilidade_visual": True # Ativa o filtro monocromático/baixo brilho
            }
        },
        
        # TESTE DE CONTROLE: COGNITIVO (Para garantir que o módulo da barra não quebra)
        {
            "nome": "COGNITIVO_Foco_e_Barra_Estática", 
            "id": "cognitivo", 
            "config": {
                "simplificar_texto": True,
                "aumentar_escala": "moderada",
                "destaque_botoes": True,
                "diminuir_espacamento": True
            }
        },
    ]

    for teste in TESTES:
        rodar_teste(teste["nome"], teste["id"], teste["config"])
        time.sleep(2) # Pausa entre os testes


if __name__ == "__main__":
    print("\n=========================================")
    print("INICIANDO SUITE DE TESTES MODULARES (DEMO)")
    print("=========================================")
    main()
