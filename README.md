# Aplicação em uma TV Box para receber metadados de uma câmera LPR e armazenar em um banco de dados SQLite

## Motivação
O projeto iniciou com o pedido de uma empresa para registrar a entrada e saída de todos os veículos, e essa informação estar disponível automaticamente no PowerBI. A ideia era ter o controle de quanto tempo cada pessoa ficou, e se necessário confrontar com outros dados, como por exemplo um colaborador que bateu o ponto porém permaneceu muito tempo na empresa. Ou um fornecedor que ficou "perambulando" pelo local.

## Objetivos

O objetivo principal do projeto é receber os metadados da câmera LPR através de algum tipo de protocolo, que no caso, o mais viável foi o TCP. E através de um código python, tratar os dados, associar a placa do veículo ao nome do proprietário e então armazená-los em um banco de dados SQLite.

Com os dados armazenados no SQLite, é possível acessá-los no PowerBI pela API [ODBC](https://en.wikipedia.org/wiki/Open_Database_Connectivity) (Open Database Connectivity)

## Arquitetura

![arquitetura](https://github.com/johnbarbosas/LPR/assets/89945583/b82b8857-0f06-47ee-9559-cbfb570cfa07)

### Configurações câmera AXIS P1465-LE

O próprio software embarcado que faz o LPR embarcado na câmera é tem nativo um configuração que envia todos os metadados por algum protocolo disponível, dentre eles estão:
- TCP
- HTTP POST
- FTP

![image](https://github.com/johnbarbosas/LPR/assets/89945583/5a0809d6-2d7b-4578-b97f-b8166bdb56b4)

O melhor protocolo testado em conjunto com o python foi o TCP. Então foi colocado o IP do servidor seguido da porta utilizada: *172.16.5.119:5000*

### Código Python para tratar os dados

As bibliotecas de python utilizadas foram *socket*, *time*, *json*, *csv*, *os* e *datetime*.

Para teste, o servidor TCP está salvando todos os dados em .csv, posteriormente esses dados serão salvos diretamente no banco de dados SQLite.

A seguir temos a função para criar ou abrir o arquivo CSV correspondente ao dia atual (o código está criando um arquivo por dia).

```
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
```

A função a seguir é para abrir o arquivo CSV com as placas e o nome do proprietário respectivo, para poder salvar o nome junto com as placas capturadas.


```
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
```

```
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
```


### Configuração da Tvbox
A Tvbox está operando com o sistema operacional Armbian, com arquitetura ARMv7l que é uma arquitetura de 32 bits. A distribuição do sistema Linux é a Debian versão 11, informação esta que pode ser obtida digitando o comando ***lsb_release -a***. 

A comunicação para uso da tvbox, que não possui interface gráfica, foi realizada utilizando o protocolo SSH por meio do software PuTTY, figura 1, que permite a comunicação SSH entre um dispositivo linux e um Windowns. 


![image](https://github.com/johnbarbosas/LPR/assets/115493461/76bdb8a6-e793-4fc0-b32e-b43768e29498)

***Figura 1*** - *Janela de configuação do PuTTY.*

Nesta janela no campo *Host Name (or Ip address)* é colocado o ip da tvbox na rede local, após isso basta pressionar *Open* que a comunicação será realizada.

Devido a essas especificações foi escolhido o SQLite para ser o gerenciador de banco de dados devido ser um sistema leve, fácil configuração e por atender a especificação de suportar arquiteturas de 32bits.

#### Instalação do SQLite e criação do banco de dados
- Instalação do SQLite:
  ```
    sudo apt-get install sqlite3

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
  );
Para saber se a tabela foi criada corretamente utiliza o código .schema nome_do_banco_de_dados.
```
  .schema dados_placas
````
Após a intalaçãodo banco de dados, será precisa criar um scrip em python responsável por criar um servidor web e receber os dados a serem armazenados. Para isso crie uma pasta em um diretório diferente do banco de dados.

Dentro desse diretório será preciso adicionar uma permissão para o python, seguinte o seguinte código:

```
  chmod +x /opt/scripts/coletor_dados.py
  ```

Para a tvbox conseguir receber esses dados é preciso instalar o Flask que é responsável por criar o sevidor web. 
  ```
    pip install Flask
```
Dentro desta pasta que conterá o script crie um arquivo de texto com o seguinte código em python:
```
#!/usr/bin/env python3
from flask import Flask, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
Esse código recebe a os dados na porta 5000;
