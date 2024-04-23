import socket
import json
import random
import time
import csv

def get_random_plate():
    with open('placas.csv', 'r') as file:
        reader = csv.reader(file)
        plates = [row[0] for row in reader]
        return random.choice(plates)

def generate_notification():
    notification = {
        'packetCounter': '126900804',
        'capture_timestamp': str(int(time.time() * 1000)),
        'frame_timestamp': str(int(time.time() * 1000000)),
        'capture_ts': str(int(time.time() * 1000000000)),
        'datetime': time.strftime('%Y%m%d %H%M%S') + str(random.randint(100, 999)),
        'plateText': get_random_plate(),
        'plateUnicode': '',
        'plateUTF8': '',
        'plateASCII': '',
        'plateCountry': 'BRA',
        'plateISO3166-2': '',
        'plateRegion': 'San Paulo',
        'plateRegionCode': '',
        'plateList': '',
        'plateListMode': '',
        'plateListDescription': '',
        'plateConfidence': str(random.uniform(0.5, 1)),
        'carState': 'new',
        'roiID': '1',
        'geotag': {'lat': 55.70421, 'lon': 13.19366},
        'imageType': 'plate',
        'plateImageType': 'jpeg',
        'plateImageSize': '0',
        'carMoveDirection': 'unknown',
        'timeProcessing': '0',
        'plateCoordinates': [168, 478, 190, 54],
        'plateCoordinatesRelative': [168, 478, 190, 54],
        'carID': '74462',
        'GEOtarget': 'Camera',
        'imagesURI': [
            '/local/fflprapp/tools.cgi?action=getImage&name=32/20240326075327_242385lp_FAJ7017_126900804.jpg',
            '/local/fflprapp/tools.cgi?action=getImage&name=33/20240326075327_243332roi_FAJ7017_126900804.jpg'
        ],
        'imageFile': 'localdata/images/33/20240326075327_243332roi_FAJ7017_126900804.jpg',
        'imageFile2': 'localdata/images/32/20240326075327_242385lp_FAJ7017_126900804.jpg',
        'profileID': '1',
        'vehicle_info': {'view': 'front'},
        'camera_info': {'SerialNumber': 'B8A44F73E2FD', 'ProdShortName': 'AXIS P1465-LE', 'IPAddress': '172.16.5.131', 'MACAddress': 'B8:A4:4F:73:E2:FD'},
        'sensorProviderID': 'saida'
    }

    notification['plateASCII'] = notification['plateText'][:7]  # obtendo os primeiros 7 caracteres da placa

    return notification

def send_notification(notification):
    HOST = 'localhost'  # Endereço do servidor TCP
    PORT = 5000  # Porta que o servidor está ouvindo

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print('1')
        s.sendall(json.dumps(notification).encode())
        print('2')
        #data = s.recv(1024)    
        print('3')

    print('Mensagem enviada:', json.dumps(notification))

if __name__ == "__main__":
    while True:
        notification = generate_notification()
        send_notification(notification)
        time.sleep(2)