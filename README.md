# Guia de Execução do Projeto

## Preparação do Ambiente

Certifique-se de que você possui instalados ambos Docker e Docker Compose. Caso não tenha, segue abaixo os comandos para instalação em uma distro Ubuntu/Debian:

Docker:
- sudo apt update
- sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
- curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-- archive-keyring.gpg
- echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
- sudo apt update
- sudo apt install -y docker-ce docker-ce-cli containerd.io
Docker Compose:
- sudo apt update
- sudo apt install -y docker-compose-plugin

Além disto, será necessário realizar a instalação de algumas bibliotecas python (localizadas em dependencias.txt , o arquivo requirements.txt será utilizado pelo Docker)

Dependencias:

- pip install -r dependencias.txt

## Execução do Crawler e do Extractor
 
 Para executar o processo de raspagem dos dados, execute o seguinte comando (Os arquivos de saída serão encontrados na pasta outputs/) :

- docker compose up --build

> **Aviso:** O tempo de execução da raspagem pode demorar aproximadamente 1 hora, para adiantar já deixamos os dados dentro do arquivo **outputs/channel_urls.json**

## Execução dos Gráficos

Para processar as métricas e exibi-las nos gráficos, após ter instalado as dependências dentro do arquivo **dependencias.txt**, execute no terminal o seguinte comando:

- python3 metrics.py

> **Nota:** Se estiver utilizando outra versão do python, certifique-se de utilizar o prefixo correto.