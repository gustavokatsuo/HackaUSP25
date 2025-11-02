# A11y-Adapt - Adaptador de Acessibilidade por IA
### Hackathon USP 2025

**Tema:** Tecnologias inovadoras para acessibilidade e inclusão digital.

## 1. O Problema
A web moderna é inacessível por padrão. Sites com imagens sem descrição (`alt text`), formulários sem `labels`, navegação quebrada (`outline: none`) e conteúdo multimídia sem transcrição excluem milhões de usuários com deficiências visuais, auditivas, motoras e cognitivas.

As soluções atuais são genéricas (um botão de "Aumentar Fonte") e falham em prover uma experiência verdadeiramente **pessoal** e **completa**.

## 2. Nossa Solução: A Acessibilidade Personalizada
Apresentamos o **A11y-Adapt**, um serviço de IA que atua como um "adaptador" de acessibilidade universal.

Nossa solução é baseada em um **"Formulário de Perfil"** que entende a necessidade *específica* do usuário. O A11y-Adapt então consome o HTML de *qualquer* site "quebrado" e, usando um pipeline de IA (Google Gemini), gera uma *view* corrigida e totalmente acessível para aquele usuário.

Em vez de uma solução "tamanho único", nós entregamos acessibilidade sob demanda.

## 3. O Protótipo: Um Serviço de IA Funcional (Viabilidade Técnica - Peso 2)
Para provar a viabilidade da nossa solução, construímos o protótipo do nosso back-end: um **servidor Flask (`app.py`)** que expõe uma API RESTful.

Este servidor usa Python, BeautifulSoup e os modelos multimodais (Texto, Imagem e Áudio) do Google Gemini para:
1.  **Ler** um HTML inacessível (`antes.html`).
2.  **Processar** o conteúdo com base em um perfil.
3.  **Devolver** um HTML 100% corrigido.

### Perfis Implementados (A Prova do "Formulário"):
Demonstramos nosso **Impacto Social (Peso 2)** e **Inovação (Peso 1)** ao implementar 6 perfis distintos que geram 8 saídas únicas:

* **Perfil Cego (`cego`):** Usa IA de Visão para gerar `alt text` e corrige a navegação por teclado (`role`, `tabindex`).
* **Perfil Surdo (`surdo`):** Usa IA de Áudio/Vídeo para **transcrever** o conteúdo falado.
* **Perfil Narração (`narracao_cegos`):** Usa IA de Áudio/Vídeo para **descrever visualmente** as cenas (audiodescrição).
* **Perfil Dislexia (`dislexia`):** Usa IA de Texto (LLM) para **simplificar** jargões e otimiza a fonte.
* **Perfil Baixa Visão (`alto_contraste`):** Gera um modo de alto contraste (fundo preto, fontes brilhantes).
* **Perfil Visão Limitada (`visao_limitada`):**
    * `necessidade: "aumentar_texto"`: Aumenta o tamanho da fonte-raiz em 40%.
    * `necessidade: "protanopia"`: Corrige cores (Verde -> Laranja).
    * `necessidade: "deuteranopia"`: Corrige cores (Verde -> Amarelo).

## 4. Como Rodar a Demonstração (Protótipo - Peso 2)

**Pré-requisitos:**
* Python 3.x
* Uma Chave de API do Google AI Studio (Gemini).

**1. Clone o Repositório:**
git clone (url do seu repo) cd (nome da pasta)


**2. Crie e Ative a `venv`:**
python3 -m venv hacka_env source hacka_env/bin/activate


**3. Instale as Dependências:**
pip install -r requirements.txt


**4. Crie sua Chave de API:**
* Crie um arquivo chamado `.env`
* Adicione sua chave: `GOOGLE_API_KEY="SUA_CHAVE_AQUI"`
    *(O arquivo `.env` está no `.gitignore` para proteger sua chave)*

**5. Rode o Servidor (Terminal 1):**
* Este é o nosso "Cérebro de IA".
python3 app.py

*O terminal irá travar em `Running on http://127.0.0.1:5000`.*

**6. Rode o Cliente de Teste (Terminal 2):**
* Abra um **novo terminal** e ative a `venv` (passo 2).
* Este script simula a "Extensão do Navegador" fazendo um pedido à nossa API.
python3 test_client.py

* O script irá chamar o servidor e gerar um arquivo `resultado_do_servidor_cego.html`.
* Para testar outros perfis, edite a variável `PERFIL_PARA_TESTAR` no topo do `test_client.py` e rode-o novamente.

## 5. Próximos Passos (Modelo de Negócio)
* **Parte 1:** Construir a "Parte 1" (formulário) que consome esta API.
* **Modelo B2C:** Uma extensão Freemium (ex: 3 perfis grátis, todos por R$ 5/mês).
* **Modelo B2B:** Um serviço de assinatura para empresas (um "selo A11y-Adapt") que adapta o site da empresa *antes* de enviá-lo ao usuário, garantindo conformidade com a lei de acessibilidade.

## 6. Arquivos do Projeto
* `app.py`: O servidor Flask (O Cérebro de IA / Nosso Protótipo).
* `test_client.py`: O script que simula a extensão do navegador (Nosso Testador).
* `antes.html`: O site "quebrado" que usamos como alvo.
* `normal.html`: O site "correto", com acessibilidade manual.
* `captions.vtt`: O arquivo de legendas do `index.html`.
* `requirements.txt`: As dependências do Python.
* `.gitignore`: Protege nossa `venv` e chaves de API.