console.log("A11y-Adapt: Script de Conteúdo Carregado.");

// --- CORREÇÃO DO RELOAD LOOP (INÍCIO) ---
// Verificamos se já processamos esta página nesta sessão.
// Se sim, não fazemos nada.
if (sessionStorage.getItem("a11yAdaptProcessed") === "true") {
    console.log("A11y-Adapt: Página já corrigida nesta sessão. Parando.");
} else {
    // Se não, marcamos como processada E RODAMOS O SCRIPT.
    // A flag é setada ANTES da chamada de API.
    sessionStorage.setItem("a11yAdaptProcessed", "true");
    runAdaptation();
}
// --- CORREÇÃO DO RELOAD LOOP (FIM) ---


function runAdaptation() {
    // 1. Pega o perfil que o usuário salvou no popup.js
    chrome.storage.local.get("a11y_perfil", (data) => {
        const perfil = data.a11y_perfil;
        
        if (perfil) {
            console.log("A11y-Adapt: Perfil encontrado:", perfil);
            adaptarPagina(perfil);
        } else {
            console.log("A11y-Adapt: Nenhum perfil ativo.");
            sessionStorage.removeItem("a11yAdaptProcessed"); // Limpa a flag se não há perfil
        }
    });
}

function adaptarPagina(perfil) {
    // 2. Pega o HTML "quebrado" da página atual
    const htmlQuebrado = document.documentElement.outerHTML;

    // 3. Prepara o payload para o servidor Flask
    const payload = {
        "html_content": htmlQuebrado,
        "profile": perfil
    };
    
    // (Caso especial para o perfil de visão limitada, se você adicionar)
    if (perfil === "visao_limitada") {
       payload.necessidade = "aumentar_texto"; // Mude aqui para testar
    }

    // 4. Chama o seu servidor Flask (app.py)
    console.log("A11y-Adapt: Enviando HTML para o servidor Flask...");
    fetch("http://127.0.0.1:5000/adaptar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Servidor Flask respondeu com erro: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // 5. Recebe o HTML corrigido e substitui a página
        if (data.html_corrigido) {
            console.log("A11y-Adapt: HTML corrigido recebido! Aplicando...");
            document.documentElement.innerHTML = data.html_corrigido;
            // A página vai recarregar/re-renderizar, mas a checagem 'sessionStorage' no topo
            // vai impedir um novo loop.
        } else {
            console.error("A11y-Adapt: Resposta do servidor não continha 'html_corrigido'.");
            sessionStorage.removeItem("a11yAdaptProcessed"); // Limpa a flag se deu erro
        }
    })
    .catch(err => {
        console.error("A11y-Adapt: Falha ao conectar com o servidor Flask.");
        console.error("Lembre-se de rodar 'pip install flask-cors' e adicionar 'CORS(app)' ao seu app.py");
        console.error(err);
        sessionStorage.removeItem("a11yAdaptProcessed"); // Limpa a flag se deu erro
    });
}