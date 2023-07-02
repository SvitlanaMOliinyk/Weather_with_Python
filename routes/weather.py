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

    print(f"Geolocation API Response: {data}")

    if 'locations' in data and len(data['locations']) > 0:
        coordinates = []
        for location in data['locations']:
            longitude = location['referencePosition']['longitude']
            latitude = location['referencePosition']['latitude']
            coordinates.append({'name': location['formattedAddress'], 'lat': latitude, 'lon': longitude})

        if len(coordinates) == 1:
            return coordinates[0]
        else:
            return coordinates
    else:
        return None


def get_weather(latitude, longitude):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
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
        # form submission with a single city name
        city = request.form.get('city')
        coordinates = geolocation(city)

        if isinstance(coordinates, list):
            # render HTML template for user selection in multiple variants
            variants = []

            for variant in coordinates:
                if 'name' in variant:
                    latitude, longitude = variant['lat'], variant['lon']
                    weather_data = get_weather(latitude, longitude)

                    if weather_data:
                        variant_data = {
                            'name': variant['name'],
                            'weather': weather_data['weather'][0]['main'],
                            'temperature': weather_data['main']['temp'],
                            'humidity': weather_data['main']['humidity'],
                        }
                        variants.append(variant_data)

            if variants:
                return render_template('city_selection.html', variants=variants)
            else:
                return 'Failed to retrieve weather data for any variant.'
        elif coordinates and 'name' in coordinates:
            # call weather function with the coordinates for one variant
            latitude, longitude = coordinates['lat'], coordinates['lon']
            weather_data = get_weather(latitude, longitude)
            # Process weather data and return the response
            if weather_data:
                return render_template('weather.html', city=city, weather_data=weather_data)
            else:
                return 'Failed to retrieve weather data.'
        else:
            return 'Unable to retrieve geolocation for the specified city.'
    else:
        # render city input form
        return render_template('city_input.html')
