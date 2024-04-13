from flask import Flask, render_template, request, jsonify
import requests, matplotlib.pyplot as plt, numpy as np
from io import BytesIO
import base64, random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import to_rgba
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter, HourLocator
from apscheduler.schedulers.background import BackgroundScheduler
from keys import *



hours_of_forecast = 24
conditions = ['clear', 'cloud', 'rain', 'snow', 'storm']
currentdata = [0,0]
def find_word_in_string(word, sentence):
    
    word = word.lower()
    sentence = sentence.lower()

    if word in sentence:
        return 1
    else:
        return 0

def match(weatherCondition):
    for term in conditions:
        if(find_word_in_string(term, weatherCondition)):
            return term
        
    
    return 'clear'
        
openweathermap_api_key = open_weather_key
lat = '40.242402'
lon = '-111.652855'

def get_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = response.json()
    print(data)
    if response.status_code == 200:
        temperature = data['current']['temp']
        weather_description = data['current']['weather'][0]['description'].title()
        humidity = data['current']['humidity']

        temp_forecast = np.empty(hours_of_forecast)
        precipitation_forecast = np.empty(hours_of_forecast)
        for i in range(hours_of_forecast):
            temp_forecast[i] = data['hourly'][i]['temp']
            precipitation_forecast[i] = data['hourly'][i]['pop']


        return [temperature, weather_description, humidity,temp_forecast,precipitation_forecast]
    else:
        return [0,"",0,[0 for i in range(hours_of_forecast)],[0 for i in range(hours_of_forecast)]]



def generate_temperature_chart(temperatures):
    current_time = datetime.now()

    
    time_list = []

    
    current_hour = current_time.hour
    start_time = datetime(current_time.year, current_time.month, current_time.day, current_hour)

    
    for i in range(hours_of_forecast):
        time_list.append(start_time + timedelta(hours=i))

    fig, ax = plt.subplots()
    ax.plot(time_list, temperatures, marker='o', alpha=0.7, color='white')  # Adjust alpha value for transparency
    ax.xaxis.set_major_locator(HourLocator(interval=3))  # Display ticks every 2 hours
    ax.xaxis.set_major_formatter(DateFormatter('%I %p'))  # Format as hours and minutes

    fig.autofmt_xdate()
    
    ax.set_title('Hourly Temperature', color='white')
    
    ax.set_ylabel('Temperature (°F)', color='white')

    # Set transparent background
    ax.patch.set_facecolor(to_rgba('black', alpha=0))
    fig.patch.set_color(to_rgba('black', alpha=0.5))
    ax.tick_params(axis='both', colors='white')

    for spine in ax.spines.values():
        spine.set_edgecolor('none')
    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    FigureCanvas(fig).print_png(image_stream)
    plt.close(fig)

    # Convert the BytesIO object to base64 for embedding in HTML
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def generate_precipitation_chart(precipitation_chance):
    

    current_time = datetime.now()
    precipitation_chance = [x * 100 for x in precipitation_chance]
    
    time_list = []

    
    current_hour = current_time.hour
    start_time = datetime(current_time.year, current_time.month, current_time.day, current_hour)

    
    for i in range(hours_of_forecast):
        time_list.append(start_time + timedelta(hours=i))

    fig, ax = plt.subplots()
    print(time_list)
    print(precipitation_chance)

    ax.plot(time_list, precipitation_chance, marker='o', alpha=0.7, color='white')  # Adjust alpha value for transparency
    ax.xaxis.set_major_locator(HourLocator(interval=3))  # Display ticks every 2 hours
    ax.xaxis.set_major_formatter(DateFormatter('%I %p'))  # Format as hours and minutes

    fig.autofmt_xdate()
    ax.set_title('Chance of Precipitation', color='white')
    ax.set_ylabel('Chance of Precipitation (%)', color='white')
    ax.set_ylim(bottom=0)

    # Set transparent background
    ax.patch.set_facecolor(to_rgba('black', alpha=0))
    fig.patch.set_color(to_rgba('black', alpha=0.5))
    ax.tick_params(axis='both', colors='white')

    for spine in ax.spines.values():
        spine.set_edgecolor('none')
    image_stream = BytesIO()
    FigureCanvas(fig).print_png(image_stream)
    plt.close(fig)

    # Convert the BytesIO object to base64 for embedding in HTML
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

app = Flask(__name__)
scheduler = BackgroundScheduler()

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    # currentdata[0] = round(data.get('temperature')*(9.0/5.0) + 32,2)
    # currentdata[1] = data.get('humidity')
    
    print(f"Received temperature: {currentdata[0]}, humidity: {currentdata[1]}")
    return jsonify({'status': 'success'}), 200


@app.route('/')
def index():
    data = update_data()
    

    return render_template('weather.html', weather_data = data['weather_data'], temperature_chart=data['temperature_chart'],
                           precipitation_chart=data['precipitation_chart'], filepath = data['filepath'])

def update_data():
    
    
    api_data = get_weather(openweathermap_api_key,lat,lon)

    weather_data = {
        'description': api_data[1],
        'temperature': api_data[0],
        'humidity': api_data[2],
    }

    temperature_chart = generate_temperature_chart(api_data[3])
    precipitation_chart = generate_precipitation_chart(api_data[4])

    condition = match(api_data[1])
    filepath = "/static/pics/" + condition + "/" + str(random.randint(0, 40)) + ".png"

    data = {
        'weather_data': weather_data,
        'temperature_chart': temperature_chart,
        'precipitation_chart': precipitation_chart,
        'filepath': filepath,
    }
    return data

if __name__ == '__main__':
    scheduler.add_job(func=update_data, trigger="interval", hours=1)
    scheduler.start()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
    