# Aplicação em uma TV Box para receber metadados de uma câmera LPR e armazenar em um banco de dados SQLite

## Motivação
O projeto iniciou com o pedido de uma empresa para registrar a entrada e saída de todos os veículos, e essa informação estar disponível automaticamente no PowerBI. A ideia era ter o controle de quanto tempo cada pessoa ficou, e se necessário confrontar com outros dados, como por exemplo um colaborador que bateu o ponto porém permaneceu muito tempo na empresa. Ou um fornecedor que ficou "perambulando" pelo local.

## Objetivos

## Arquitetura

### Configuração da Tvbox
A Tvbox está operando com o sistema operacional Armbain, com arquitetura ARMv7l que é uma arquitetura de 32 bits. A distribuição do sistema Linux é a Debian versão 11, informação esta que pode ser obtida digitando o comando ***lsb_release -a***. 

A comunicação para uso da tvbox, que não possui interface gráfica, foi realizada utilizando o protocolo SSH por meio do software PuTTY que permite a comunicação SSH entre um dispositivo linux e um Windowns.


Devido a essas especificações foi escolhido o o SQLite para ser o gerenciador de banco de dados devido ser um sistema leve e de fácil configuração.


## Manual de Instalação e Configuração


## Manual de Instalação e Configuração

