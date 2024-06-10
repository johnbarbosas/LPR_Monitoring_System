import socket
import json
import csv
import os
from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Function to create or open the CSV file for the current day
def get_csv_file():
    today = datetime.now().strftime("%Y_%m_%d")
    data_folder_path = 'data'
    csv_file_path = os.path.join(data_folder_path, f'data_{today}.csv')

    os.makedirs(data_folder_path, exist_ok=True)

    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['timestamp', 'license_plate', 'name', 'confidence', 'ID', 'duration'])

    return csv_file_path

def get_name_by_license_plate(license_plate):
    csv_file_path = 'placas.csv'

    try:
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == license_plate:
                    return row[1]
    except FileNotFoundError:
        print(f"File '{csv_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while opening the CSV file: {e}")

    return None

def find_last_entry(license_plate):
    csv_file_path = get_csv_file()
    last_entry = None

    try:
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[1] == license_plate and 'entry' in row[4].lower():
                    last_entry = row
    except FileNotFoundError:
        print(f"File '{csv_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while opening the CSV file: {e}")

    return last_entry

# InfluxDB configuration
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "1kWhejX1FGCKDYPyerc26Pex2_xGbH_kxHLHgjxmC_1nt5reBsmfK4uaZ5muhjkSb5dm2qmKlUYrlWFx4ntIJw=="
INFLUXDB_ORG = "184fa17bc689338c"
INFLUXDB_BUCKET = "lpr"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 5000

s.bind((host, port))
s.listen(5)

print(f"Listening on {host}:{port}")

while True:
    clientsocket, address = s.accept()

    try:
        data = clientsocket.recv(4096)
        message = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"Error decoding message: {e}")
        continue

    timezone_adjustment = timedelta(hours=-3)
    timestamp = datetime.fromtimestamp(int(message["capture_timestamp"]) / 1000.0, tz=timezone.utc) + timezone_adjustment
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    license_plate = message["plateASCII"]
    name = get_name_by_license_plate(license_plate)
    confidence = message["plateConfidence"]
    camera_id = message["sensorProviderID"]

    print(f"\nTimestamp: {timestamp_str}")
    print(f"License Plate: {license_plate}")
    print(f"Name: {name}")
    print(f"Confidence: {confidence}")
    print(f"ID: {camera_id}")

    csv_file_path = get_csv_file()
    duration = "00:00:00"

    if "exit" in camera_id.lower():
        last_entry = find_last_entry(license_plate)
        if last_entry:
            last_entry_time = datetime.strptime(last_entry[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            duration_timedelta = timestamp - last_entry_time
            duration_seconds = duration_timedelta.total_seconds()
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            print(f"Vehicle {license_plate} stayed for {duration}.")
        else:
            print("No entry records found.")

    with open(csv_file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp_str, license_plate, name, confidence, camera_id, duration])
        print("Written to CSV!")

    point = Point("vehicle_log")\
        .tag("license_plate", license_plate)\
        .tag("name", name)\
        .field("confidence", confidence)\
        .field("ID", camera_id)\
        .field("duration_hours", int(duration.split(':')[0]))\
        .field("duration_minutes", int(duration.split(':')[1]))\
        .field("duration_seconds", int(duration.split(':')[2]))\
        .time(timestamp, WritePrecision.NS)

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print("Written to InfluxDB!")
