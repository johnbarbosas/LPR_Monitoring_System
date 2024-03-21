from flask import Flask, request
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# Usuário e senha de exemplo (substitua com suas credenciais)
USUARIO_AUTORIZADO = 'seu_usuario'
SENHA_AUTORIZADA = 'sua_senha'

@auth.verify_password
def verifica_usuario(usuario, senha):
    return usuario == USUARIO_AUTORIZADO and senha == SENHA_AUTORIZADA

@app.route('/', methods=['POST'])
@auth.login_required
def receber_notificacao():
    try:
        dados = request.get_json()
        endereco_ip_cliente = request.remote_addr
        print(f"Notificação recebida de {endereco_ip_cliente}: {dados}")
        # Faça o que for necessário com os dados recebidos da câmera
        return "Notificação recebida com sucesso"
    except Exception as e:
        print("Erro ao processar notificação:", e)
        return "Erro ao processar notificação", 500

if __name__ == '__main__':
    app.run(port=5000)