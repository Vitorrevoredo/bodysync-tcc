from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    
    # Vamos manter alguns dados básicos no perfil
    idade = Column(Integer, nullable=True)
    peso = Column(Float, nullable=True)
    altura = Column(Float, nullable=True)

    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)

    # Relacionamento: Um usuário pode ter VÁRIAS consultas
    consultas = relationship("Consulta", back_populates="dono")


class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_avaliacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Requisitos da Calculadora Vitalize (RF03, RF04, RF05)
    sexo = Column(String, nullable=True)
    atividade = Column(String, nullable=True)
    quadril_cm = Column(Float, nullable=True)
    
    objetivo_sessao = Column(String, nullable=True) # Ex: Emagrecimento, Hipertrofia

    # Cálculos Físicos
    imc = Column(Float, nullable=True)
    classificacao_imc = Column(String, nullable=True)
    iac = Column(Float, nullable=True)
    classificacao_iac = Column(String, nullable=True)

    # Extração de Features Espaciais via MediaPipe (Visão Computacional)
    shoulder_width = Column(Float, nullable=True)
    hip_width = Column(Float, nullable=True)
    shoulder_hip_ratio = Column(Float, nullable=True)
    estimativa_gordura = Column(Float)

    # Resultados Finais Gerados pela IA (RF06 e RF07)
    dieta_recomendada = Column(String, nullable=True)
    recomendacao_treino = Column(String, nullable=True)

    # Relacionamento de volta para a Classe Usuário
    dono = relationship("Usuario", back_populates="consultas")
