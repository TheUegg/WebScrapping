# Imagem base
FROM python:3.8-slim

# Instalação do Chrome
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
# RUN apt-get update && apt-get install -y google-chrome-stable

# Instalação do ChromeDriver
RUN apt-get install -yqq unzip

# Instalação do Selenium
RUN pip install selenium

# RUN rm -f /usr/local/bin/chromedriver
# RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/131.0.6778.85/chromedriver_linux64.zip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


# Adicionando o código
WORKDIR /app
COPY . /app

# Instalando as dependências
RUN pip install -r requirements.txt

# Adicionando o volume da pasta /outputs
VOLUME /outputs

# Rodando o código
CMD ["python", "main.py"]
