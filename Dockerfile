# Imagem base
FROM python:3.8-slim

# Instalação do Chrome
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Instalação do ChromeDriver
RUN apt-get install -yqq unzip

# Instalação do Selenium
RUN pip install selenium

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install pyvirtualdisplay and other dependencies
RUN pip install pyvirtualdisplay

# Adicionando o código
WORKDIR /app
COPY . /app

# Instalando as dependências
RUN pip install -r requirements.txt

# Adicionando o volume da pasta /outputs
VOLUME /outputs

# Rodando o código
CMD ["python", "main.py"]
