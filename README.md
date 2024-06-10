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
- Installing MariaDB:
  
Instalattion of MariaDB:
  ```
    sudo apt install mariadb-server
```
Após a instalação é preciso configurar o MariaDB para melhorar a sua segunça, para isso use o comando _**sudo mysql_secure_installation**_. Com esse comando é possivél editar as configurações de senha root, usuário anônimo, login remoto e banco de dados _test_.
  
1. _Senha root:_ Senha necessária para poder realizar a edições de administrador.

2. _Usuários Anônimos:_ Habilita ou desabilita a opção de usuários não cadastrados possam visualizar os dados contidos no banco.

3. _Login remoto:_ Habilita ou desabilita a opção de poder editar o banco remotamente.

4. _Banco de dados teste:_ Por padrão o MariaDB possui um banco para teste denominado _test_ que pode ser excluido ou mantido.

Recomenda-se desabilitar os usuários anônimos, login remoto e criar uma senha root para maior seguraça dos dados. 

  ```
    sudo mysql_secure_installation
  ```

Para acessar o gerenciador do MariaDB utilize o código abaixo onde o usuário será logado como administrador. 
  ```
    sudo mysql -u root -p
  ```
Caso queira criar um novo usuário entre como administrador e insira o comando abaixo editando os campos _usuário_ e _senha_.

```
CREATE USER 'usuário'@'localhost' IDENTIFIED BY 'senha';
```
Para dar as permissões a este novo usuário pode-se utilizar o código abaixo onde é concedido todas as permissões. É necessário já ter criado um banco de dados, pois esse usuário estará recebendo as permissões de um banco de dados

```
GRANT ALL PRIVILEGES ON _nome_do_banco_.* TO 'usuário'@'localhost';';
```
- Creating the Database:

Nesta etapa será solicitado a senha criada para o MariaDB. Após essa etapa pra criar o banco de dados insira o comando _CREATE DATABASE **nome_do_banco**;_.
  
  ```
    CREATE DATABASE dados_placas;
  ```

  
Com o banco de dados criado é necessário direcionar ao gerenciado do banco de dados qual o banco ele deve usar. Utilize o comando _USE *nome_do_banco*_:
  
```
    USE dados_placas;
```

Criação da tabela de dados:
  ```
  CREATE TABLE dados_placas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    license_plate VARCHAR(255),
    name VARCHAR(255),
    confidence FLOAT,
    camera_id VARCHAR(255),
    duration VARCHAR(255)
);
```
Para saber se a tabela foi criada corretamente pode-se utiilizar o comando _DESCRIBE *nome_do_banco*;_.

```
    DESCRIBE dados_placas;
```

