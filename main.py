from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import random
import math
from models import Base, Usuario, Consulta
from database import engine, get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import joblib
import ml_pipeline
import intelligent_rules

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    rf_model = joblib.load('rf_model.pkl')
except FileNotFoundError:
    rf_model = None
    print("Aviso: Modelo 'rf_model.pkl' não encontrado. Para predições precisas, execute 'python train_model.py'.")

# Cria as tabelas na Versão 7
Base.metadata.create_all(bind=engine) 

app = FastAPI(title="BioVision AI - HealthTech ML")

is_vercel = os.getenv("VERCEL") == "1"
pasta_imagens = "/tmp/imagens_avaliacoes" if is_vercel else "imagens_avaliacoes"
os.makedirs(pasta_imagens, exist_ok=True)
app.mount("/app", StaticFiles(directory="static"), name="static")

@app.get("/")
def index_redirecionamento():
    return FileResponse("static/index.html")

@app.post("/api/registrar")
def registrar_usuario(
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    conta_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if conta_existente:
        return JSONResponse(status_code=400, content={"status": "erro", "mensagem": "E-mail já registrado"})
        
    hash_senha = pwd_context.hash(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha_hash=hash_senha)
    db.add(novo_usuario)
    db.commit()
    return {"status": "sincronizado", "mensagem": "Usuário blindado com bcrypt"}

@app.post("/api/login")
def login_usuario(
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not pwd_context.verify(senha, usuario.senha_hash):
        return JSONResponse(status_code=403, content={"status": "erro", "mensagem": "Métricas de validação incorretas"})
        
    consultas = db.query(Consulta).filter(Consulta.usuario_id == usuario.id).order_by(Consulta.id.desc()).all()
    historico = []
    for c in consultas:
        historico.append({
            "id": c.id, "data_avaliacao": c.data_avaliacao, "objetivo_sessao": c.objetivo_sessao,
            "imc": c.imc, "classificacao_imc": c.classificacao_imc,
            "iac": c.iac, "classificacao_iac": c.classificacao_iac,
            "dieta_pronta": bool(c.dieta_recomendada),
            "treino_pronto": bool(c.recomendacao_treino)
        })
        
    return {
        "status": "sucesso",
        "usuario": {"nome": usuario.nome, "email": usuario.email, "peso": usuario.peso, "altura": usuario.altura, "idade": usuario.idade},
        "historico": historico
    }

@app.get("/api/perfil/{email}")
def perfil_usuario(email: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"status": "erro", "mensagem": "Sessão inválida"})
        
    consultas = db.query(Consulta).filter(Consulta.usuario_id == usuario.id).order_by(Consulta.id.desc()).all()
    historico = []
    for c in consultas:
         historico.append({
            "id": c.id, "data_avaliacao": c.data_avaliacao, "objetivo_sessao": c.objetivo_sessao,
            "imc": c.imc, "classificacao_imc": c.classificacao_imc,
            "iac": c.iac, "classificacao_iac": c.classificacao_iac,
            "dieta_recomendada": c.dieta_recomendada,
            "recomendacao_treino": c.recomendacao_treino
        })
        
    return {
        "status": "sucesso",
        "usuario": {"nome": usuario.nome, "email": usuario.email, "peso": usuario.peso, "altura": usuario.altura, "idade": usuario.idade},
        "historico": historico
    }


# ROTA PRINCIPAL 1: Lança o Formulário e Retorna Cálculos Vitais (RFO4 e RF05)
@app.post("/api/avaliar_composicao")
async def avaliar_composicao(
    email: str = Form(...),
    objetivo: str = Form(...),
    idade: int = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    sexo: str = Form(...),
    nivel_atividade: str = Form(...),
    quadril_cm: float = Form(...),
    foto_corpo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"status":"erro", "mensagem": "Perfil Oculto"})

    # Atualiza Cache Rápido do Usuário
    usuario.idade = idade
    usuario.altura = altura
    usuario.peso = peso

    # Salvando Imagem "Fake" (Em MVP)
    extensao = foto_corpo.filename.split(".")[-1]
    caminho_salvo = f"{pasta_imagens}/snapshot_{usuario.id}_{random.randint(1000, 9999)}.{extensao}"
    with open(caminho_salvo, "wb") as buffer:
        shutil.copyfileobj(foto_corpo.file, buffer)

    # Lógica Biométrica - RF04: IMC
    imc = round(peso / (altura * altura), 2)
    classificacao_imc = "Normal"
    if imc < 18.5: classificacao_imc = "Abaixo do peso"
    elif imc >= 25.0 and imc < 30: classificacao_imc = "Sobrepeso"
    elif imc >= 30: classificacao_imc = "Obesidade"

    # Lógica Biométrica - RF05: IAC
    # Fórmula IAC (Índice de Adiposidade Corporal) = (Quadril / (Altura * √Altura)) - 18
    iac = round((quadril_cm / (altura * math.sqrt(altura))) - 18, 2)
    
    classificacao_iac = "Normal (Adequada)"
    if sexo.lower() == 'feminino':
        if iac < 21: classificacao_iac = "Abaixo (Déficit Adiposo)"
        elif iac >= 33: classificacao_iac = "Alta (Excesso Adiposo)"
    else: # Masculino
        if iac < 8: classificacao_iac = "Abaixo (Déficit Adiposo)"
        elif iac >= 21: classificacao_iac = "Alta (Excesso Adiposo)"

    nova_consulta = Consulta(
        usuario_id = usuario.id,
        objetivo_sessao = objetivo,
        sexo = sexo, atividade = nivel_atividade, quadril_cm = quadril_cm,
        imc = imc, classificacao_imc = classificacao_imc,
        iac = iac, classificacao_iac = classificacao_iac
    )

    # Chamada Real ao Pipeline de Visão Computacional
    features_cv = ml_pipeline.extract_features(caminho_salvo)
    
    if features_cv:
        nova_consulta.shoulder_width = features_cv["shoulder_width"]
        nova_consulta.hip_width = features_cv["hip_width"]
        nova_consulta.shoulder_hip_ratio = features_cv["shoulder_hip_ratio"]
        
        # Predição de Machine Learning (Random Forest)
        if rf_model is not None:
            # Features treinadas: idade, peso, altura, shoulder_hip_ratio
            fat_prediction = rf_model.predict([[idade, peso, altura, features_cv["shoulder_hip_ratio"]]])
            estimativa = round(fat_prediction[0], 2)
        else:
            # Fallback lógico se o .pkl não estiver pronto
            estimativa = round(iac, 2)
            
        nova_consulta.estimativa_gordura = estimativa
    else:
        # Fallback (Falha no MediaPipe)
        nova_consulta.estimativa_gordura = round(iac, 2)
        nova_consulta.shoulder_hip_ratio = 1.0
    db.add(nova_consulta)
    db.commit()
    db.refresh(nova_consulta)

    return {
        "status": "sucesso",
        "consulta_id": nova_consulta.id,
        "dados_biometricos": {
            "imc": imc,
            "classificacao_imc": classificacao_imc,
            "iac": iac,
            "classificacao_iac": classificacao_iac
        }
    }


# ROTA 4: Gerar Dieta Específica (Markdown)
@app.get("/api/gerar_dieta/{consulta_id}")
def gerar_dieta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    user = db.query(Usuario).filter(Usuario.id == consulta.usuario_id).first()
    # Mock do LMM: Se Emagrecimento, manda déficit calórico.
    if consulta.objetivo_sessao == "Emagrecimento":
        dieta = f"### Plano Alimentar: Déficit Calórico Sustentável\n\n*Café da manhã:* 2 ovos mexidos + 1 fatia de mamão com chia.\n*Almoço:* 120g Peito de frango + 150g Salada crua + 80g Arroz integral\n*Lanche:* Iogurte natural zero gordura\n*Jantar:* Omelete de 3 claras com espinafre e chá calmante.\n\n*Nota da Plataforma: Beba ao menos 3L de água por dia.*"
    else:
        dieta = f"### Plano Alimentar: Superávit Controlado (Hipertrofia)\n\n*Café da manhã:* Panqueca de aveia c/ whey e banana.\n*Almoço:* 150g Patinho moído + 200g Macarrão integral\n*Lanche pré-treino:* 3 fatias pão de forma + doce de leite\n*Jantar:* 150g Salmão/Frango + 150g Batata Salsão + Salada verde (azeite abundante).\n\n*Nota:* Foque na densidade calórica e no descanso!"
        
    consulta.dieta_recomendada = dieta
    db.commit()
    return {"status": "ok", "dieta": dieta}


# ROTA 5: Gerar Treino Específico (Markdown via IA)
@app.get("/api/gerar_treino/{consulta_id}")
def gerar_treino(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    
    # Reconstrói as features do CV
    features_cv = {
        "shoulder_width": consulta.shoulder_width,
        "hip_width": consulta.hip_width,
        "shoulder_hip_ratio": consulta.shoulder_hip_ratio
    }
    
    # Chama o módulo especialista da Etapa 6
    treino = intelligent_rules.generate_recommendations(
        objetivo=consulta.objetivo_sessao,
        imc=consulta.imc,
        percentual_gordura_estimado=consulta.estimativa_gordura,
        features_cv=features_cv
    )
    
    consulta.recomendacao_treino = treino
    db.commit()
    return {"status": "ok", "treino": treino}
