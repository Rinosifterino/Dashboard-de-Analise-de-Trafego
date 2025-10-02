Relatório Técnico: Dashboard de Análise de Tráfego
Arquitetura do Sistema
A solução foi projetada com uma arquitetura cliente-servidor desacoplada, composta por um backend responsável pela coleta e processamento de dados e um frontend para visualização.

Backend (Python com Flask e Scapy):
O núcleo do backend opera com duas threads principais para garantir que a captura de pacotes não bloqueie a entrega de dados pela API.

Thread de Captura: Utiliza a biblioteca Scapy para inspecionar cada pacote de rede que entra ou sai da interface de rede do servidor monitorado (SERVER_IP). Para cada pacote, extrai informações cruciais como IPs de origem/destino, protocolo e tamanho.

Thread de Agregação: Funciona como um temporizador. A cada 5 segundos, ela move os dados coletados pela thread de captura para uma estrutura de dados final, que fica disponível para a API, e limpa a estrutura de coleta para iniciar uma nova janela de tempo.

Thread Principal (API Flask): O servidor web Flask expõe um único endpoint (/traffic) que serve os dados da última janela de tempo completa no formato JSON. O uso de CORS permite que o frontend, mesmo aberto como um arquivo local, possa consumir os dados sem restrições de segurança do navegador.

A sincronização entre as threads é gerenciada por um Lock para garantir a integridade dos dados e evitar condições de corrida (race conditions) ao acessar a estrutura de dados compartilhada.

Frontend (HTML, Tailwind CSS e Chart.js):
O frontend é uma aplicação de página única (Single Page Application) contida em um único arquivo index.html.

A interface busca os dados da API a cada 5 segundos usando a função fetch do JavaScript.

A biblioteca Chart.js é utilizada para renderizar os gráficos de barras. Ela é configurada para ser recriada dinamicamente com os novos dados, proporcionando uma visualização em tempo real.

Desafios na Implementação
Lógica de Agregação em Janelas de Tempo
O principal desafio na agregação foi processar um fluxo contínuo de pacotes em blocos discretos de 5 segundos de forma eficiente e segura. A abordagem de usar duas estruturas de dados separadas — uma para a coleta "ao vivo" e outra para a última janela "completa" — foi crucial. Isso, combinado com um Lock, permitiu que a API sempre servisse um conjunto de dados consistente, sem o risco de expor dados de uma janela de tempo que ainda estava sendo construída.

Criação da Visualização Interativa (Drill Down)
A implementação da funcionalidade de drill down no frontend apresentou desafios relacionados ao gerenciamento de estado. Foi necessário criar uma variável de controle (isDrillDownView) para saber qual visualização (geral por IP ou detalhada por protocolo) estava ativa. Ao clicar em uma barra, o estado era alterado, e o mesmo objeto de gráfico do Chart.js era atualizado com um novo conjunto de dados filtrado para o IP selecionado. O maior desafio foi garantir que, ao retornar para a visão geral, o gráfico voltasse ao seu estado original e que as atualizações automáticas a cada 5 segundos respeitassem a visualização atualmente ativa, atualizando ou a lista de IPs ou os protocolos do IP selecionado. A solução foi estruturar as funções de renderização (renderMainView e renderDrillDownView) para que pudessem ser chamadas a qualquer momento para reconstruir o gráfico de acordo com o estado atual.