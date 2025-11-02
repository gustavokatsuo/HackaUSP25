// Limpa a flag da sessão atual
function clearFlagAndReload(tabId) {
    chrome.scripting.executeScript({
        target: { tabId: tabId },
        function: () => {
            sessionStorage.removeItem('a11yAdaptProcessed');
        }
    }, () => {
        // Recarrega a aba DEPOIS de limpar a flag
        chrome.tabs.reload(tabId);
    });
}

// Salva a escolha do usuário no "storage" do Chrome
function salvarPerfil() {
    const perfilSelecionado = document.querySelector('input[name="perfil"]:checked');
    if (perfilSelecionado) {
        chrome.storage.local.set({ "a11y_perfil": perfilSelecionado.value }, () => {
            console.log("Perfil salvo:", perfilSelecionado.value);
            // Recarrega a aba atual para o content_script rodar
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                clearFlagAndReload(tabs[0].id);
            });
        });
    }
}

// Limpa a escolha
function limparPerfil() {
    chrome.storage.local.remove("a11y_perfil", () => {
        console.log("Perfil removido.");
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            clearFlagAndReload(tabs[0].id);
        });
    });
}

// Carrega a escolha salva quando o popup abre
document.addEventListener("DOMContentLoaded", () => {
    chrome.storage.local.get("a11y_perfil", (data) => {
        if (data.a11y_perfil) {
            document.getElementById(data.a11y_perfil).checked = true;
        }
    });
});

document.getElementById("salvar").addEventListener("click", salvarPerfil);
document.getElementById("limpar").addEventListener("click", limparPerfil);