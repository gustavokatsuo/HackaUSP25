import requests
import json

# CONFIGURAÇÃO DO TESTE
PERFIL_PARA_TESTAR = "alto_contraste" # mude aqui! ex: "dislexia", "surdo", "alto_contraste"

def testar_servidor():
    print(f"--- Testando o Perfil: {PERFIL_PARA_TESTAR} ---")
    
    # 1. Carrega o site quebrado do disco
    try:
        with open('antes.html', 'r', encoding='utf-8') as f:
            html_quebrado = f.read()
    except FileNotFoundError:
        print("ERRO: 'antes.html' não encontrado. Cancele e rode o 'adaptador.py' primeiro.")
        return

    # 2. Prepara o "pedido" (payload JSON) para a API
    # Isso é o que a extensão do Chrome faria
    dados_para_enviar = {
        "html_content": html_quebrado,
        "profile": PERFIL_PARA_TESTAR
    }
    
    # (Caso especial para o perfil de visão limitada)
    if PERFIL_PARA_TESTAR == "visao_limitada":
        dados_para_enviar["necessidade"] = "aumentar_texto" # ou "protanopia"

    # 3. Manda o pedido para o seu servidor Flask (que está rodando no outro terminal)
    try:
        url_do_servidor = "http://127.0.0.1:5000/adaptar"
        response = requests.post(url_do_servidor, json=dados_para_enviar)
        
        response.raise_for_status() # Garante que não deu erro 404 ou 500

        # 4. Pega a resposta (o HTML corrigido)
        dados_da_resposta = response.json()
        html_corrigido = dados_da_resposta.get("html_corrigido")

        # 5. Salva o resultado
        if html_corrigido:
            output_filename = f"resultado_do_servidor_{PERFIL_PARA_TESTAR}.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_corrigido)
            print(f"\nSUCESSO! O servidor funcionou!")
            print(f"Abra o arquivo '{output_filename}' para ver o resultado.")
        else:
            print("ERRO: O servidor retornou uma resposta vazia.")

    except requests.exceptions.ConnectionError:
        print("\n--- ERRO DE CONEXÃO ---")
        print("Não consegui me conectar ao servidor.")
        print("Você se lembrou de rodar 'python3 app.py' no outro terminal PRIMEIRO?")
    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---")
        print(e)

if __name__ == "__main__":
    testar_servidor()