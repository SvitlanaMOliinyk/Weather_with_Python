from flask import Flask
from routes.hello import hello_bp
from routes.weather import weather_bp

app = Flask(__name__)
app.register_blueprint(hello_bp)
app.register_blueprint(weather_bp)

if __name__ == '__main__':
    app.run()
