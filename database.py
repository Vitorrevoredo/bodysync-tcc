import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração Cloud-Ready para SQLite no Vercel (Filesystem Somente Leitura fora de /tmp)
is_vercel = os.getenv("VERCEL") == "1"
if is_vercel:
    db_path = "/tmp/sql_app_v7.db"
    # Se ainda não estiver na tmp do lambda atual, copia o banco base do repositório para habilitar a escrita na sessão
    if not os.path.exists(db_path):
        shutil.copyfile("sql_app_v7.db", db_path)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app_v7.db"

# engine é o ponto de entrada principal do banco
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # SQLite only: disables multi-thread lock limitation for FastAPI
)

# Cria a Sessão que vamos alocar para cada rota do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para que as tabelas do SQLAlchemy consigam herdar para criar estrutura
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
