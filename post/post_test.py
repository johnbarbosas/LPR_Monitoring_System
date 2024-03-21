import requests

url = 'http://127.0.0.1:5000'
dados_notificacao = {'campo1': 'valor1', 'campo2': 'valor2'}

try:
    response = requests.post(url, json=dados_notificacao, timeout=5)  # Adiciona timeout de 5 segundos
    print("Resposta do servidor:", response.text)
except requests.exceptions.RequestException as e:
    print("Erro ao conectar ao servidor:", e)
