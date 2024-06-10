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
- Acessando o MariaDB:
  ```
    sudo mysql -u root -p
  ```

  
- Nesta etapa será solicitado a senha criada para o MariaDB. Após essa etapa pra criar o banco de dados insira o comando _CREATE DATABASE **nome_do_banco**;_.
  
  ```
    CREATE DATABASE dados_placas;
  ```

  
- Com o banco de dados criado é necessário direcionar ao gerenciado do banco de dados qual o banco ele deve usar. Utilize o comando _USE *nome_do_banco*_:
  
```
    USE dados_placas;
```

- Criação da tabela de dados:
  ```
  CREATE TABLE dados_placas (
    data TEXT,
    hora TEXT,
    placa TEXT,
    acuracia REAL,
    entrada_saida TEXT,
    permanencia TEXT
  ); 
Para saber se a tabela foi criada corretamente pode-se utiilizar o comando _DESCRIBE *nome_do_banco*;_.

```
  DESCRIBE dados_placas;
```


Após a intalaçãodo banco de dados, será precisa criar um scrip em python responsável por criar um servidor web e receber os dados a serem armazenados. Para isso crie uma pasta em um diretório diferente do banco de dados.

Dentro desse diretório será preciso adicionar uma permissão para o python, seguinte o seguinte código:
```
  chmod +x /opt/scripts/coletor_dados.py
  ```

Para a tvbox conseguir receber esses dados é preciso instalar o Flask que é responsável por criar o sevidor web. 
  
    pip install Flask
