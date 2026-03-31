# Usar uma imagem oficial do Python mais leve (A 3.11 é a mais estável para Machine Learning)
FROM python:3.11-slim

# Instalar as bibliotecas de sistema C++ e OpenGL exigidas pelo MediaPipe e OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgles2 \
    && rm -rf /var/lib/apt/lists/*

# Definir um diretório de trabalho na máquina virtual
WORKDIR /app

# Copiar os requisitos antes para otimizar o tempo de build do Docker
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o resto do projeto para dentro da máquina virtual
COPY . .

# Expor a porta que o Render utiliza
EXPOSE 10000

# Comando obrigatório para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
