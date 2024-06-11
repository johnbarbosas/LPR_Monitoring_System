# Remote Vehicle License Plate Monitoring (LPR)

## Motivation
The project began with a request from a company to record the entry and exit of all vehicles, with this information automatically available in PowerBI. The idea was to control how long each person stayed, and if necessary, cross-check with other data, such as an employee who clocked in but remained in the company for a long time, or a supplier who was "wandering" around the premises.

## Objectives
The main objective of the project is to receive the metadata from the LPR camera through some type of protocol, in this case, the most viable was TCP. Using a Python script, the data is processed, the vehicle's license plate is associated with the owner's name, and then stored in an SQLite database.

With the data stored in SQLite, it can be accessed in PowerBI via the [ODBC](https://en.wikipedia.org/wiki/Open_Database_Connectivity) (Open Database Connectivity) API.

## Architecture

![arquitetura](https://github.com/johnbarbosas/LPR_Monitoring_System/assets/89945583/e0243717-969d-4126-8f1f-a15a17836805)


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
After installation, it's necessary to configure MariaDB to enhance its security. To do this, use the command sudo mysql_secure_installation. With this command, you can edit settings for the root password, anonymous user, remote login, and the _test_ database.
  
1. _Root password:_Password required to perform administrator edits.

2. _Anonymous user:_ Enables or disables the option for non-registered users to view the data contained in the database.

3. _Remote login:_ Enables or disables the option to edit the database remotely.

4. _Database test:_ By default, MariaDB comes with a test database named test which can be deleted or kept.


It is recommended to disable anonymous users, remote login, and create a root password for enhanced data security. 

  ```
    sudo mysql_secure_installation
  ```

To access the MariaDB manager, use the code below where the user will be logged in as an administrator.
  ```
    sudo mysql -u root -p
  ```
If you want to create a new user, log in as an administrator and enter the command below, editing the _username_ and _password_ fields.

```
CREATE USER 'usuário'@'localhost' IDENTIFIED BY 'senha';
```
To grant permissions to this new user, you can use the code below, where all permissions are granted. It is necessary to have already created a database, as this user will be receiving permissions for a specific database.

```
GRANT ALL PRIVILEGES ON _nome_do_banco_.* TO 'usuário'@'localhost';';
```
- Creating the Database:

At this stage, the password created for MariaDB will be requested. After this step, to create the database, enter the command _CREATE DATABASE **nome_do_banco**;_.
  
  ```
    CREATE DATABASE _nome_do_banco_;
  ```

  
With the database created, it is necessary to direct the database manager to which database it should use. Use the command _USE *nome_do_banco*_:
  
```
    USE _nome_do_banco_;
```

Creation of the data table:
  ```
  CREATE TABLE _nome_do_banco_ (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    license_plate VARCHAR(255),
    name VARCHAR(255),
    confidence FLOAT,
    camera_id VARCHAR(255),
    duration VARCHAR(255)
);
```
To verify if the table was created correctly, you can use the command _DESCRIBE *nome_do_banco*;_.

```
    DESCRIBE dados_placas;
```
To receive data sent by the security camera, a code (_server.py_) has been created. It receives a standard message, compares it with a registered names CSV, processes the data, and sends it to the database.
