from flask import Blueprint, request, render_template
import requests
import os
from dotenv import load_dotenv

weather_bp = Blueprint('weather', __name__)
load_dotenv()
api_key = os.environ.get("API_KEY")
geo_api_key = os.environ.get("GEO_API_KEY")


def geolocation(city):
    url = f"https://api.myptv.com/geocoding/v1/locations/by-text?searchText={city}"
    headers = {
        'apiKey': geo_api_key
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'locations' in data and len(data['locations']) > 0:
        locations = data['locations']
        if len(locations) == 1:
            location = locations[0]
            longitude = location['referencePosition']['longitude']
            latitude = location['referencePosition']['latitude']
            return {'name': location['formattedAddress'], 'lat': latitude, 'lon': longitude}
        else:
            coordinates = []
            for location in locations:
                longitude = location['referencePosition']['longitude']
                latitude = location['referencePosition']['latitude']
                coordinates.append({'name': location['formattedAddress'], 'lat': latitude, 'lon': longitude})
            return coordinates
    else:
        return None



def get_weather(latitude, longitude):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)

    print(f"Weather API Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


@weather_bp.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city = request.form.get('city')
        coordinates = geolocation(city)

        if isinstance(coordinates, list) and len(coordinates) > 0:
            return render_template('city_selection.html', city=city, variants=coordinates)
        elif coordinates and 'name' in coordinates:
            latitude, longitude = coordinates['lat'], coordinates['lon']
            weather_data = get_weather(latitude, longitude)

            if weather_data:
                temperature = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                main = weather_data['weather'][0]['main']
                return render_template('weather.html', city=city, temperature=temperature, description=description, main=main)
            else:
                return 'Failed to retrieve weather data.'
        else:
            return render_template('city_not_found.html', city=city)
    else:
        # render city input form
        return render_template('city_input.html')


@weather_bp.route('/select-variant', methods=['POST'])
def select_variant():
    city = request.form.get('city')
    variant_index = int(request.form.get('variant_index'))
    coordinates = geolocation(city)

    if isinstance(coordinates, list):
        if 0 <= variant_index < len(coordinates):
            variant = coordinates[variant_index]
            latitude, longitude = variant['lat'], variant['lon']
            weather_data = get_weather(latitude, longitude)

            if weather_data:
                temperature = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                main = weather_data['weather'][0]['main']
                return render_template('weather.html', city=city, temperature=temperature, description=description, main=main)
            else:
                return 'Failed to retrieve weather data.'
        else:
            return 'Invalid variant selection.'
    elif isinstance(coordinates, dict):
        latitude, longitude = coordinates['lat'], coordinates['lon']
        weather_data = get_weather(latitude, longitude)

        if weather_data:
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            main = weather_data['weather'][0]['main']
            return render_template('weather.html', city=city, temperature=temperature, description=description, main=main)
        else:
            return 'Failed to retrieve weather data.'
    else:
        return 'Invalid variant selection.'
