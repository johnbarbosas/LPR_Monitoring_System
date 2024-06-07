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

    # Create the folder if it does not exist
    os.makedirs(data_folder_path, exist_ok=True)

    # If the file does not exist, create a new one with headers
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['timestamp', 'license_plate', 'name', 'confidence', 'ID'])

    return csv_file_path

def get_name_by_license_plate(license_plate):
    # Define the path to the CSV file
    csv_file_path = 'placas.csv'

    try:
        # Open the CSV file
        with open(csv_file_path, newline='') as csvfile:
            # Read the contents of the CSV file
            reader = csv.reader(csvfile)
            # Iterate over the rows in the file
            for row in reader:
                # Check if the license plate matches the current row
                if row[0] == license_plate:
                    # Return the corresponding name
                    return row[1]
    except FileNotFoundError:
        print(f"File '{csv_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while opening the CSV file: {e}")

    # Return None if the license plate is not found or an error occurs
    return None

# InfluxDB configuration
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "1kWhejX1FGCKDYPyerc26Pex2_xGbH_kxHLHgjxmC_1nt5reBsmfK4uaZ5muhjkSb5dm2qmKlUYrlWFx4ntIJw=="
INFLUXDB_ORG = "184fa17bc689338c"
INFLUXDB_BUCKET = "lpr"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# AF_INET => IPv4
# SOCK_STREAM => TCP

host = 'localhost'
port = 5000

s.bind((host, port))
s.listen(5)

print(f"Listening on {host}:{port}")

while True:
    clientsocket, address = s.accept()

    try:
        data = clientsocket.recv(4096)
        message = json.loads(data.decode('utf-8'))
    except UnicodeDecodeError as e:
        print(f"Decoding error: {e}")
        continue
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        continue

    timezone_adjustment = timedelta(hours=-3)

    timestamp = int(message["capture_timestamp"]) / 1000.0
    timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc) + timezone_adjustment
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

    # Get the CSV file path for the current day
    csv_file_path = get_csv_file()

    # Add the information to the CSV file
    with open(csv_file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp_str, license_plate, name, confidence, camera_id])
        print("Written to CSV!")

    # Write to InfluxDB
    point = Point("vehicle_log")\
        .tag("license_plate", license_plate)\
        .tag("name", name)\
        .field("confidence", confidence)\
        .field("ID", camera_id)\
        .time(timestamp, WritePrecision.NS)

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print("Written to InfluxDB!")

    # Check if the message is from an exit camera
    if "exit" in camera_id.lower():
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "vehicle_log" and r.license_plate == "{license_plate}" and r.ID =~ /entry/)
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
        '''
        tables = query_api.query(query, org=INFLUXDB_ORG)

        if tables:
            last_entry_time = None
            for table in tables:
                for record in table.records:
                    last_entry_time = record.get_time()

            if last_entry_time:
                duration = timestamp - last_entry_time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"Vehicle {license_plate} stayed for {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds.")
