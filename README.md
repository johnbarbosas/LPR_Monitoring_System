# Aplicação em uma TV Box para receber metadados de uma câmera LPR e armazenar em um banco de dados SQLite

## Motivação
O projeto iniciou com o pedido de uma empresa para registrar a entrada e saída de todos os veículos, e essa informação estar disponível automaticamente no PowerBI. A ideia era ter o controle de quanto tempo cada pessoa ficou, e se necessário confrontar com outros dados, como por exemplo um colaborador que bateu o ponto porém permaneceu muito tempo na empresa. Ou um fornecedor que ficou "perambulando" pelo local.

## Objetivos

## Arquitetura

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
