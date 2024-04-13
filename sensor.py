import requests
import time

# Setup for DHT11
SENSOR = Adafruit_DHT.DHT11
PIN = 4  # Adjust as per the GPIO pin connected

def get_sensor_data():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
    return {'temperature': temperature, 'humidity': humidity}

def send_data(url, data):
    try:
        response = requests.post(url, json=data)
        print('Data sent to server:', response.text)
    except requests.RequestException as e:
        print('Failed to send data:', e)

if __name__ == '__main__':
    server_url = 'http://<server-ip>:5001/data'
    while True:
        sensor_data = get_sensor_data()
        send_data(server_url, sensor_data)
        time.sleep(60)  # sends data every 60 seconds

