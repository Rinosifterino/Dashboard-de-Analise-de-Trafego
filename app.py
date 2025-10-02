# -*- coding: utf-8 -*-

# =============================================================================
# PASSO 1 e 2: BACKEND - Captura, Agregação e API com Flask e Scapy
# =============================================================================
# Este script realiza as seguintes tarefas:
# 1. Define um IP de servidor para monitoramento.
# 2. Captura pacotes de rede de/para esse IP em uma thread separada.
# 3. Agrega os dados de tráfego (bytes de entrada/saída) por IP de cliente e por protocolo.
# 4. Armazena esses dados em janelas de tempo de 5 segundos.
# 5. Para cada IP, tenta resolver o hostname correspondente (ex: google.com).
# 6. Fornece um servidor web Flask com um endpoint de API (`/traffic`) que retorna
#    os dados da última janela de tempo, incluindo os hostnames, em formato JSON.
# =============================================================================

import time
import threading
from collections import defaultdict
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import socket
from ipaddress import ip_address, AddressValueError

# --- Configuração ---
# IMPORTANTE: Altere esta variável para o endereço IP da máquina que você quer monitorar.
SERVER_IP = "192.168.1.10"  # <-- MUDE AQUI

# --- Estruturas de Dados Globais ---
traffic_data = defaultdict(lambda: {
    "total_in": 0, "total_out": 0,
    "protocols": defaultdict(lambda: {"in": 0, "out": 0})
})
last_completed_traffic_data = {}
hostname_cache = {}  # Cache para armazenar hostnames resolvidos
data_lock = threading.Lock()

# --- Lógica de Captura de Pacotes (Scapy) ---
try:
    from scapy.all import sniff, IP, TCP, UDP, get_if_list
except ImportError:
    print("Erro: A biblioteca Scapy não está instalada.")
    print("Por favor, instale-a com o comando: pip install scapy")
    sys.exit(1)

def get_protocol_name(packet):
    if packet.haslayer(TCP): return "TCP"
    if packet.haslayer(UDP): return "UDP"
    return "Outro"

def process_packet(packet):
    global traffic_data
    if not packet.haslayer(IP): return

    try:
        ip_layer = packet[IP]
        src_ip, dst_ip = ip_layer.src, ip_layer.dst
        if SERVER_IP not in (src_ip, dst_ip): return

        client_ip = dst_ip if src_ip == SERVER_IP else src_ip
        direction = "out" if src_ip == SERVER_IP else "in"
        
        try:
            if not ip_address(client_ip).is_private: return
        except AddressValueError: return

        with data_lock:
            packet_size = len(packet)
            protocol = get_protocol_name(packet)
            if direction == "in":
                traffic_data[client_ip]["total_in"] += packet_size
                traffic_data[client_ip]["protocols"][protocol]["in"] += packet_size
            else:
                traffic_data[client_ip]["total_out"] += packet_size
                traffic_data[client_ip]["protocols"][protocol]["out"] += packet_size
    except Exception: pass

def start_sniffing():
    print(f"\n[*] Iniciando captura de pacotes para o IP: {SERVER_IP}")
    try:
        sniff(prn=process_packet, store=0)
    except Exception as e:
        print(f"\n[ERRO FATAL NA CAPTURA]\nDetalhe: {e}")
        print("1. Verifique se você está executando com privilégios de administrador.")
        print("2. Verifique se Npcap (Windows) ou libpcap (Linux/macOS) está instalado.")
        sys.exit(1)

def aggregate_in_windows():
    global traffic_data, last_completed_traffic_data
    while True:
        time.sleep(5)
        with data_lock:
            if traffic_data:
                print(f"[Diagnóstico] Janela de 5s concluída. {len(traffic_data)} IPs com tráfego processados.")
                last_completed_traffic_data = dict(traffic_data)
                traffic_data.clear()

# --- API Web (Flask) ---
app = Flask(__name__)
CORS(app)

@app.route('/traffic', methods=['GET'])
def get_traffic_data():
    with data_lock:
        if not last_completed_traffic_data:
            return jsonify({"message": "Aguardando captura do primeiro tráfego...", "data": {}})
        
        # Cria uma cópia para adicionar os hostnames
        response_data = dict(last_completed_traffic_data)
        
        # NOVO: Resolve hostnames para cada IP, usando cache
        for ip in response_data:
            if ip not in hostname_cache:
                try:
                    # Tenta resolver o hostname
                    hostname = socket.gethostbyaddr(ip)[0]
                    hostname_cache[ip] = hostname
                except (socket.herror, socket.gaierror):
                    # Se falhar, usa o próprio IP como hostname para não tentar novamente
                    hostname_cache[ip] = ip
            
            response_data[ip]['hostname'] = hostname_cache[ip]
            
        return jsonify({"data": response_data})

# --- Inicialização ---
if __name__ == '__main__':
    print("=========================================================")
    print("        INICIANDO DASHBOARD DE TRÁFEGO DE REDE           ")
    print("=========================================================")
    
    # ... (bloco de diagnóstico inicial omitido por brevidade) ...

    try:
        sniffer_thread = threading.Thread(target=start_sniffing, daemon=True)
        aggregator_thread = threading.Thread(target=aggregate_in_windows, daemon=True)
        sniffer_thread.start()
        aggregator_thread.start()
        
        print("\n[*] Servidor Flask iniciado em http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

