# -*- coding: utf-8 -*-
import time
import threading
from collections import defaultdict
from flask import Flask, jsonify
from flask_cors import CORS
import sys

# --- Configuração ---
SERVER_IP = "SEU_IP_AQUI" # <-- MUDE AQUI

# --- Estruturas de Dados Globais ---
traffic_data = defaultdict(lambda: {"total_in": 0, "total_out": 0, "protocols": defaultdict(lambda: {"in": 0, "out": 0})})
last_completed_traffic_data = {}
data_lock = threading.Lock()

# --- Lógica de Captura (Scapy) ---
try:
    from scapy.all import sniff, IP, TCP, UDP
except ImportError:
    sys.exit("Erro: Scapy não instalado. Use: pip install scapy")

def get_protocol_name(packet):
    if packet.haslayer(TCP): return "TCP"
    if packet.haslayer(UDP): return "UDP"
    return "Outro"

def process_packet(packet):
    global traffic_data
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        packet_size = len(packet)
        protocol = get_protocol_name(packet)

        if SERVER_IP not in (src_ip, dst_ip): return

        client_ip = dst_ip if src_ip == SERVER_IP else src_ip
        direction = "out" if src_ip == SERVER_IP else "in"
        
        with data_lock:
            if direction == "in":
                traffic_data[client_ip]["total_in"] += packet_size
                traffic_data[client_ip]["protocols"][protocol]["in"] += packet_size
            else:
                traffic_data[client_ip]["total_out"] += packet_size
                traffic_data[client_ip]["protocols"][protocol]["out"] += packet_size

def start_sniffing():
    sniff(prn=process_packet, store=0)

def aggregate_in_windows():
    global traffic_data, last_completed_traffic_data
    while True:
        time.sleep(5)
        with data_lock:
            if traffic_data:
                last_completed_traffic_data = dict(traffic_data)
                traffic_data.clear()

# --- API (Flask) ---
app = Flask(__name__)
CORS(app)

@app.route('/traffic')
def get_traffic_data():
    with data_lock:
        return jsonify({"data": last_completed_traffic_data or {}})

# --- Inicialização ---
if __name__ == '__main__':
    sniffer_thread = threading.Thread(target=start_sniffing, daemon=True)
    aggregator_thread = threading.Thread(target=aggregate_in_windows, daemon=True)
    sniffer_thread.start()
    aggregator_thread.start()
    app.run(host='0.0.0.0', port=5000)
