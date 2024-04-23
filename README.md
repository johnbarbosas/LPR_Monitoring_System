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

- Criando um novo banco de dados
- Criando o banco de dados
- Verificação de a tabela foi criada corretamente

## Manual de Instalação e Configuração


## Manual de Instalação e Configuração

