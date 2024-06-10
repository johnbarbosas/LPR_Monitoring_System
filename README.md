# Remote Vehicle License Plate Monitoring (LPR)

## Motivation
The project began with a request from a company to record the entry and exit of all vehicles, with this information automatically available in PowerBI. The idea was to control how long each person stayed, and if necessary, cross-check with other data, such as an employee who clocked in but remained in the company for a long time, or a supplier who was "wandering" around the premises.

## Objectives
The main objective of the project is to receive the metadata from the LPR camera through some type of protocol, in this case, the most viable was TCP. Using a Python script, the data is processed, the vehicle's license plate is associated with the owner's name, and then stored in an SQLite database.

With the data stored in SQLite, it can be accessed in PowerBI via the [ODBC](https://en.wikipedia.org/wiki/Open_Database_Connectivity) (Open Database Connectivity) API.

## Architecture

![architecture](https://github.com/johnbarbosas/LPR/assets/89945583/b82b8857-0f06-47ee-9559-cbfb570cfa07)

### AXIS P1465-LE Camera Settings
The embedded software that performs the LPR on the camera natively has a configuration that sends all metadata via an available protocol, including:
- TCP
- HTTP POST
- FTP

![image](https://github.com/johnbarbosas/LPR/assets/89945583/5a0809d6-2d7b-4578-b97f-b8166bdb56b4)

The best protocol tested in conjunction with Python was TCP. Therefore, the server's IP followed by the used port was set: *172.16.5.119:5000*.

### Python Code for Data Processing
The Python libraries used were *socket*, *time*, *json*, *csv*, *os*, *datetime*, and *mysql.connector*.

For testing, the TCP server is saving all data in .csv; later, this data will be directly saved in the MariaDB database.

### TV Box Configuration
The TV box is operating with the Armbian operating system, with an ARMv7l architecture, which is a 32-bit architecture. The Linux system distribution is Debian version 11, which can be obtained by typing the command
```
lsb_release -a.
```

The communication for using the TV box, which does not have a graphical interface, was done using the SSH protocol through the PuTTY software, shown in figure 1, which allows SSH communication between a Linux device and a Windows machine.


![image](https://github.com/johnbarbosas/LPR/assets/115493461/76bdb8a6-e793-4fc0-b32e-b43768e29498)

**Figura 1** - PuTTY Configuration Window.

In this window, in the Host Name (or IP address) field, enter the IP of the TV box on the local network, then press Open to establish the connection.

Due to these specifications, SQLite was chosen as the database manager because it is a lightweight system, easy to configure, and supports 32-bit architectures.

#### Installing MariaDB and Creating the Database
- Instalattion of MariaDB:
  ```
    sudo apt install mariadb-server

- Criando um novo banco de dados: Caminho até o local de criação do banco de dados.
  ```
    cd /caminho/para/o/diretorio

- Criando o banco de dados: 
```
    sqlite3 nome_do_banco_de_dados.db
```

- Criação da tabela de dados:
  ```
  CREATE TABLE IF NOT EXISTS dados_placas (
    data TEXT,
    hora TEXT,
    placa TEXT,
    acuracia REAL,
    entrada_saida TEXT
    permanencia TEXT
  );
Para saber se a tabela foi criada corretamente utiliza o código .schema nome_do_banco_de_dados.
```
  .schema dados_placas
```
Após a intalaçãodo banco de dados, será precisa criar um scrip em python responsável por criar um servidor web e receber os dados a serem armazenados. Para isso crie uma pasta em um diretório diferente do banco de dados.

Dentro desse diretório será preciso adicionar uma permissão para o python, seguinte o seguinte código:
```
  chmod +x /opt/scripts/coletor_dados.py
  ```

Para a tvbox conseguir receber esses dados é preciso instalar o Flask que é responsável por criar o sevidor web. 
  
    pip install Flask

Dentro desta pasta que conterá o script crie um arquivo de texto com o seguinte código em python com a extensão .py:
```
#!/usr/bin/env python3
from flask import Flask, request
import sqlite3
from datetime import datetime

app = Flask(_name_)

@app.route('/', methods=['POST'])
def receber_dados():
    dados = request.json
    if dados:
        try:
            conn = sqlite3.connect('dados.db')
            cursor = conn.cursor()
            hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO dados_placas (placa, horario) VALUES (?, ?)",
                           (dados['plateASCII'], hora_atual))
            conn.commit()
            conn.close()
            return "Dados recebidos e salvos com sucesso!\n"
        except Exception as e:
            return f"Erro ao processar os dados: {str(e)}\n"
    else:
        return "Nenhum dado recebido.\n"

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000)
```
Esse código recebe a os dados na porta 5000;

Na máquina Windowns onde encontra-se o CSV na mesma pasta que ele foi criado um código em python que envia os dados do CSV via json para o servidor WEB Flasky, e esse por sua vez irá salvar no banco de dados.

Código python para o Windowns:
```
import csv
import os
import requests
import json
from datetime import datetime

# Obter o diretório atual do script
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Caminho para o arquivo CSV na mesma pasta que o script
caminho_csv = os.path.join(diretorio_atual, 'dados_2024_01_29.csv')

# URL do servidor
url = 'http://192.168.0.55:5000'  # Substitua "endereco_ip_da_tvbox" pelo endereço IP da TV box

# Função para ler os dados do CSV e retorná-los como uma lista de dicionários
def ler_csv(caminho):
    dados = []
    with open(caminho, newline='') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:
            # Converte o timestamp para formato datetime
            timestamp = datetime.strptime(linha['timestamp'], '%Y-%m-%d %H:%M:%S')
            # Monta o objeto JSON com os dados relevantes
            dados_linha = {
                'dia': timestamp.strftime('%Y-%m-%d'),
                'horario': timestamp.strftime('%H:%M:%S'),
                'placa': linha['placa'],
                'acuracia': float(linha['confiabilidade']),
                'entrada_saida': linha['ID']
            }
            dados.append(dados_linha)
    return dados

# Lê os dados do CSV
dados_csv = ler_csv(caminho_csv)

# Imprime os dados lidos do CSV
print("Dados do CSV:")
print(dados_csv)

# Envia cada linha do CSV como uma solicitação POST para o servidor
for dados_linha in dados_csv:
    try:
        # Envia os dados para o servidor
        response = requests.post(url, json=dados_linha)
        print("Resposta do servidor:", response.text)
    except requests.exceptions.RequestException as e:
        print("Erro ao conectar ao servidor:", e)
```

Com o banco criado, e os scripts prontos o servidor Flasky deve ser inicializado, para isso, a tvbox precisa estar no diretório do código Flasky.py. Dentro do diretório dê o seguinte comando:

```
sudo systemctl start flask_app
```
