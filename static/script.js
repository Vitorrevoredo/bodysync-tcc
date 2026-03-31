document.addEventListener("DOMContentLoaded", () => {
    // ---- Telas ----
    const stepLogin = document.getElementById("step-login");
    const stepDashboard = document.getElementById("step-dashboard");
    const stepForm = document.getElementById("step-form");
    const stepResult = document.getElementById("step-result");

    // ---- Elementos Mapeados ----
    const loginForm = document.getElementById("login-form");
    const metricsForm = document.getElementById("metrics-form");
    const toggleRegBtn = document.getElementById("toggle-reg-btn");
    const groupNome = document.getElementById("group-nome");
    const loginBadge = document.getElementById("login-badge");
    const loginBtnText = document.querySelector("#login-btn span");
    const loginLoader = document.getElementById("login-loader");
    const logoutBtn = document.getElementById("logout-btn");
    
    let isRegisterMode = false;

    // --- Persistência de Sessão ---
    const localSession = localStorage.getItem("bioVisionEmail");
    if(localSession) {
        resgatarSessao(localSession);
    }

    async function resgatarSessao(emailSalvo) {
        try {
            const resp = await fetch(`/api/perfil/${emailSalvo}`);
            const data = await resp.json();
            
            if(resp.ok) {
                document.getElementById("sessao-email").value = emailSalvo;
                document.getElementById("dash-nome").innerText = data.usuario.nome;
                popularDashboard(data.usuario, data.historico);
                
                stepLogin.classList.add("hidden");
                stepDashboard.classList.remove("hidden");
            } else {
                localStorage.removeItem("bioVisionEmail");
            }
        } catch(e) {
            console.log("Offline / erro API");
        }
    }

    // Ações de Logout
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("bioVisionEmail");
        window.location.reload(); 
    });


    // ---- Interação Formulário Login ----
    toggleRegBtn.addEventListener("click", () => {
        isRegisterMode = !isRegisterMode;
        if(isRegisterMode) {
            groupNome.classList.remove("hidden");
            document.getElementById("reg-nome").setAttribute("required", "true");
            toggleRegBtn.innerText = "Já possui paciente cadastrado? Login";
            loginBadge.innerText = "Criar Prontuário";
            loginBtnText.innerText = "Registrar-se no Sistema";
        } else {
            groupNome.classList.add("hidden");
            document.getElementById("reg-nome").removeAttribute("required");
            toggleRegBtn.innerText = "Não possui cadastro? Criar Conta";
            loginBadge.innerText = "Login Seguro";
            loginBtnText.innerText = "Acessar Prontuário";
        }
    });

    // Submissão do Registro / Login
    loginForm.addEventListener("submit", async(e)=>{
         e.preventDefault();
         const email = document.getElementById("login-email").value;
         const senha = document.getElementById("login-senha").value;
         
         loginBtnText.style.display = 'none';
         loginLoader.classList.remove("hidden");

         const formData = new FormData();
         formData.append("email", email);
         formData.append("senha", senha);

         if(isRegisterMode) {
             formData.append("nome", document.getElementById("reg-nome").value);
             try {
                const resp = await fetch(`/api/registrar`, { method: "POST", body: formData });
                const result = await resp.json();
                if(resp.ok) {
                    alert("✅ Conta criada! Verifique suas credenciais de acesso.");
                    toggleRegBtn.click(); // Volta pro modo Login
                } else {
                    alert("Erro do Sistema: " + result.mensagem);
                }
             } catch(e) { alert("Erro de rede."); }
             
             loginBtnText.style.display = 'block';
             loginLoader.classList.add("hidden");
             return;
         }

         // Acesso Login
         try{
             const resp = await fetch(`/api/login`, { method: "POST", body: formData });
             const data = await resp.json();
             
             if(resp.ok){
                 localStorage.setItem("bioVisionEmail", email);
                 document.getElementById("sessao-email").value = email;
                 document.getElementById("dash-nome").innerText = data.usuario.nome;
                 popularDashboard(data.usuario, data.historico);
                 
                 setTimeout(() => {
                     stepLogin.classList.add("hidden");
                     stepDashboard.classList.remove("hidden");
                 }, 400);
             } else {
                 alert("🔒 Acesso Negado: " + data.mensagem);
             }
         } catch (error){
            alert("Erro de servidor: " + error);
         } finally {
            loginBtnText.style.display = 'block';
            loginLoader.classList.add("hidden");
         }
    });

    // Popular os cards de histórico
    function popularDashboard(usuario, historico) {
        document.getElementById("idade").value = usuario.idade > 0 ? usuario.idade : "";
        document.getElementById("peso").value = usuario.peso > 0 ? usuario.peso : "";
        // Manter placeholders se = 0
        if(usuario.altura > 0) document.getElementById("altura").value = usuario.altura;

        const histList = document.getElementById("history-list");
        histList.innerHTML = "";

        if (historico.length === 0){
             histList.innerHTML = '<div class="empty-state">Sem avaliações. Sua linha do tempo de saúde está vazia.</div>';
             return;
        }

        historico.forEach(c => {
             const div = document.createElement("div");
             div.className = "history-card";
             div.innerHTML = `
                 <div class="hist-date">${c.data_avaliacao.split("T")[0]} | Escopo: ${c.objetivo_sessao}</div>
                 <div class="hist-details" style="display:flex; justify-content:space-between; margin-bottom:10px">
                     <span><strong>IMC:</strong> ${c.imc} (${c.classificacao_imc})</span>
                     <span><strong>IAC:</strong> ${c.iac}% (${c.classificacao_iac})</span>
                 </div>
                 <div class="hist-treino" style="border-top:1px dashed #444; padding-top:10px">
                    STATUS: ${c.dieta_recomendada ? "Dieta Gerada ✓" : "Dieta Não Gerada"} | ${c.recomendacao_treino ? "Treino Gerado ✓" : "Treino Não Gerado"}
                 </div>
             `;
             histList.appendChild(div);
        });
    }

    // Ações de Navegação Dashboard -> Calculadora (RF03)
    document.getElementById("nova-avaliacao-btn").addEventListener("click", () => {
         stepDashboard.classList.add("hidden");
         stepForm.classList.remove("hidden");
    });
    
    document.getElementById("cancel-eval-btn").addEventListener("click", () => {
         stepForm.classList.add("hidden");
         stepDashboard.classList.remove("hidden");
    });

    // Módulo de Câmera (Opcional)
    const fileInput = document.getElementById("foto");
    const dropZone = document.getElementById("drop-zone");
    const previewArea = document.getElementById("preview-area");
    const imagePreview = document.getElementById("image-preview");
    const removeImgBtn = document.getElementById("remove-img");
    const submitBtnEval = document.getElementById("submit-btn");

    fileInput.addEventListener("change", function(e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                dropZone.classList.add("hidden");
                previewArea.classList.remove("hidden");
            }
            reader.readAsDataURL(this.files[0]);
        }
    });
    removeImgBtn.addEventListener("click", () => {
        fileInput.value = "";
        imagePreview.src = "#";
        previewArea.classList.add("hidden");
        dropZone.classList.remove("hidden");
    });

    // Rota 3: Submit do Formulário Principal (Calcula IMC e IAC e abre os Modulos Genéricos)
    metricsForm.addEventListener("submit", async(e) => {
        e.preventDefault();
        
        const btnText = submitBtnEval.querySelector("span");
        const loader = document.getElementById("btn-loader");
        btnText.style.display = 'none';
        loader.classList.remove('hidden');
        submitBtnEval.disabled = true;

        const formData = new FormData();
        formData.append("email", document.getElementById("sessao-email").value);
        formData.append("objetivo", document.getElementById("objetivo").value);
        formData.append("idade", document.getElementById("idade").value);
        formData.append("peso", document.getElementById("peso").value);
        formData.append("altura", document.getElementById("altura").value);
        formData.append("quadril_cm", document.getElementById("quadril").value);
        formData.append("sexo", document.getElementById("sexo").value);
        formData.append("nivel_atividade", document.getElementById("atividade").value);
        
        // Se houver foto, envia.
        if(fileInput.files[0]) {
            formData.append("foto_corpo", fileInput.files[0]);
        } else {
            // Emula um blank blob para não quebrar a API FastAPI que exige foto na base do Python
            const fakeblob = new Blob([""], { type: "image/png" });
            formData.append("foto_corpo", fakeblob, "fake.png");
        }

        try {
            const response = await fetch("/api/avaliar_composicao", {
                method: "POST",
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                // Preenche o Step Final
                document.getElementById("res-imc").innerText = data.dados_biometricos.imc;
                document.getElementById("class-imc").innerText = data.dados_biometricos.classificacao_imc;
                
                document.getElementById("res-iac").innerText = data.dados_biometricos.iac;
                document.getElementById("class-iac").innerText = data.dados_biometricos.classificacao_iac;
                
                document.getElementById("sessao-consulta-id").value = data.consulta_id;

                setTimeout(() => {
                    stepForm.classList.add("hidden");
                    stepResult.classList.remove("hidden");
                    window.scrollTo(0,0);
                }, 800); 
            } else {
                alert("Erro ao Processar as Tabelas: " + data.mensagem);
            }
        } catch(error) {
            alert("Erro de Conexão: " + error);
        } finally {
            btnText.style.display = 'block';
            loader.classList.add('hidden');
            submitBtnEval.disabled = false;
        }
    });

    // -------- RNF08: BOTÕES INTERATIVOS DE DELAY E API AI ---------

    const btnDieta = document.getElementById("btn-gerar-dieta");
    const loaderDieta = document.getElementById("loader-dieta");
    const boxDieta = document.getElementById("box-dieta");
    const textDieta = document.getElementById("res-dieta");

    btnDieta.addEventListener("click", () => {
        btnDieta.querySelector("span").style.display = "none";
        loaderDieta.classList.remove("hidden");
        btnDieta.disabled = true;

        const consult_id = document.getElementById("sessao-consulta-id").value;
        const simulandoTimeoutRNF08 = 3000; // 3 segundos reais de feeling

        setTimeout(async () => {
            const result = await fetch(`/api/gerar_dieta/${consult_id}`);
            const payload = await result.json();

            btnDieta.classList.add("hidden"); // Remove botão
            loaderDieta.classList.add("hidden");
            boxDieta.classList.remove("hidden"); // Exibe Plaqueta Final
            textDieta.innerHTML = parseMarkdownBasico(payload.dieta);

        }, simulandoTimeoutRNF08);

    });

    const btnTreino = document.getElementById("btn-gerar-treino");
    const loaderTreino = document.getElementById("loader-treino");
    const boxTreino = document.getElementById("box-treino");
    const textTreino = document.getElementById("res-treino");

    btnTreino.addEventListener("click", () => {
        btnTreino.querySelector("span").style.display = "none";
        loaderTreino.classList.remove("hidden");
        btnTreino.disabled = true;

        const consult_id = document.getElementById("sessao-consulta-id").value;
        const simulandoTimeoutRNF08 = 4000; // 4 segs para API OpenAi mock

        setTimeout(async () => {
            const result = await fetch(`/api/gerar_treino/${consult_id}`);
            const payload = await result.json();

            btnTreino.classList.add("hidden"); 
            loaderTreino.classList.add("hidden");
            boxTreino.classList.remove("hidden"); 
            textTreino.innerHTML = parseMarkdownBasico(payload.treino);

        }, simulandoTimeoutRNF08);
    });

    // Helpers Práticos
    function parseMarkdownBasico(text) {
        let res = text.replace(/### (.*?)\n/g, "<h3 style='color:var(--highlight); margin-bottom:10px'>$1</h3>");
        res = res.replace(/## (.*?)\n/g, "<h4 style='margin-bottom:5px; margin-top:10px'>$1</h4>");
        res = res.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        res = res.replace(/\*(.*?)\*/g, "<em>$1</em>");
        res = res.replace(/- (.*?)\n/g, "<li>$1</li>");
        return res;
    }

});
