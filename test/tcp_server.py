import socket
import time
import json
import csv
import os
from datetime import datetime, timedelta

# Função para criar ou abrir o arquivo CSV para o dia atual
def obter_arquivo_csv():
    hoje = datetime.now().strftime("%Y_%m_%d")
    caminho_pasta_dados = 'dados'
    caminho_arquivo_csv = os.path.join(caminho_pasta_dados, f'dados_{hoje}.csv')

    # Cria a pasta se não existir
    os.makedirs(caminho_pasta_dados, exist_ok=True)

    # Se o arquivo não existir, cria um novo com cabeçalho
    if not os.path.isfile(caminho_arquivo_csv):
        with open(caminho_arquivo_csv, 'w', newline='') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerow(['timestamp', 'placa', 'nome', 'confiabilidade', 'ID'])

    return caminho_arquivo_csv

def nome_pela_placa(placa):
    # Define o caminho do arquivo CSV
    csv_file_path = 'test/placas.csv'

    try:
        # Abre o arquivo CSV
        with open(csv_file_path, newline='') as csvfile:
            # Lê o conteúdo do arquivo CSV
            reader = csv.reader(csvfile)
            # Itera sobre as linhas do arquivo
            for row in reader:
                # Verifica se a placa corresponde à placa da linha atual
                if row[0] == placa:
                    # Retorna o nome correspondente
                    return row[1]
    except FileNotFoundError:
        print(f"Arquivo '{csv_file_path}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao abrir o arquivo CSV: {e}")

    # Retorna None se a placa não for encontrada ou ocorrer um erro
    return None

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# AF_INET => IPv4
# SOCK_STREAM => TCP

host = 'localhost'
port = 5000

s.bind((host,port))
s.listen(5)

print(f"Listening on {host}:{port}")

while True:
    clientsocket, address = s.accept()
    #print(f"Connection from {address} has been established!")
    #msg = "Welcome to the server!"

    try:
        dados = clientsocket.recv(4096)
        data = json.loads(dados.decode('utf-8'))
        #print(data)
    except UnicodeDecodeError as e:
        print(f"Erro de decodificação: {e}")
        continue
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        continue

    
    #print(f"Dados recebidos: {data}")

    print(f"\n")

    ajuste_fuso_horario = timedelta(hours=-3)

    hora = int(data["capture_timestamp"]) / 1000.0
    hora = datetime.utcfromtimestamp(hora) + ajuste_fuso_horario
    hora = hora.strftime('%Y-%m-%d %H:%M:%S')

    nome = nome_pela_placa(data["plateASCII"])

    print("Timestamp:", hora)
    print("Placa:", data["plateASCII"])
    print("Nome:", nome)
    print("Confiabilidade:", data["plateConfidence"])
    print("ID:", data["sensorProviderID"])

    # Obtem o caminho do arquivo CSV para o dia atual
    caminho_csv = obter_arquivo_csv()

    # Adiciona as informações ao arquivo CSV
    with open(caminho_csv, 'a', newline='') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerow([hora, data["plateASCII"], nome, data["plateConfidence"], data["sensorProviderID"]])
        print("Escrito no CSV!")
