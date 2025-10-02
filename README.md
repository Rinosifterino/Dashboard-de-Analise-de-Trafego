Dashboard de Análise de Tráfego de Servidor em Tempo Real
Este projeto consiste em um sistema de monitoramento de rede que captura o tráfego de um servidor específico, processa esses dados em tempo real e os exibe em um dashboard web interativo.

O sistema é composto por duas partes principais:

Backend (Python): Um script que utiliza Scapy para capturar pacotes e Flask para servir uma API RESTful com os dados agregados.

Frontend (HTML/JS): Uma página web que consome a API e exibe os dados em um gráfico de barras dinâmico usando Chart.js, com funcionalidade de drill down.

Pré-requisitos
Antes de começar, garanta que você tenha os seguintes softwares instalados:

Python 3.x: Download Python

pip: (geralmente instalado com o Python)

Npcap ou WinPcap (para Windows): A biblioteca Scapy depende de um desses para funcionar. O instalador do Npcap pode ser encontrado em https://npcap.org/. Marque a opção "Install Npcap in WinPcap API-compatible Mode" durante a instalação.

libpcap (para Linux/macOS): Geralmente já vem instalado. Se não, instale com sudo apt-get install libpcap-dev (Debian/Ubuntu) ou brew install libpcap (macOS).

Instalação
Clone ou baixe este repositório para o seu computador.

Abra um terminal (Prompt de Comando, PowerShell ou Terminal) na pasta do projeto.

Instale as dependências Python executando o seguinte comando:

pip install flask flask-cors scapy

Como Executar
A execução do projeto é dividida em duas etapas: rodar o backend e abrir o frontend.

1. Configurar e Rodar o Backend
Descubra o seu Endereço IP Local:

Windows: Abra o Prompt de Comando e digite ipconfig. Procure por "Endereço IPv4" na sua conexão de rede ativa (Wi-Fi ou Ethernet).

Linux/macOS: Abra o terminal e digite ip addr ou ifconfig. Procure pelo seu endereço IP na interface de rede ativa (ex: eth0 ou wlan0).

Edite o arquivo app.py:

Abra o arquivo app.py em um editor de texto.

Na linha 24, altere o valor da variável SERVER_IP para o endereço IP que você encontrou no passo anterior.

# Exemplo:
SERVER_IP = "192.168.1.10" # <-- MUDE AQUI para o seu IP

Execute o script do backend:

No terminal, dentro da pasta do projeto, execute o seguinte comando. É crucial rodar este comando como administrador para permitir a captura de pacotes de rede.

Windows: Abra o Prompt de Comando ou PowerShell como Administrador e execute:

python app.py

Linux/macOS:

sudo python3 app.py

Se tudo der certo, você verá mensagens indicando que a captura foi iniciada e o servidor Flask está rodando.

2. Visualizar o Frontend
Abra o arquivo index.html:

Navegue até a pasta do projeto no seu explorador de arquivos.

Dê um duplo-clique no arquivo index.html. Ele será aberto no seu navegador padrão.

Gere tráfego de rede:

Para que o dashboard mostre algum dado, você precisa gerar tráfego para o seu computador. Você pode fazer isso de várias formas:

Peça para um colega na mesma rede acessar um serviço no seu computador.

Acesse um site a partir do seu próprio computador.

Execute um teste de velocidade de internet.

O dashboard irá atualizar automaticamente a cada 5 segundos com os novos dados de tráfego.

Interaja com o gráfico:

Clique em qualquer uma das barras (que representam um IP cliente) para ver a análise detalhada do tráfego por protocolo (TCP, UDP, etc.) para aquele cliente específico.

Clique no botão "Voltar" para retornar à visão geral.