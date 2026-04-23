import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


def get_weather(city: str):
    url = "https://api.openweathermap.org/data/2.5/weather"

    if "," not in city:
        city = city + ",CA"

    params = {
        "q": city,
        "units": "metric",
        "APPID": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception:
        return None

    if str(data.get("cod")) != "200":
        return None

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "weather": data["weather"][0]["main"],
        "temp": round(data["main"]["temp"])
    }


def render_page(weather=None, city=""):
    weather_html = ""
    error_html = ""

    if weather:
        weather_html = f"""
        <div class="card">
            <h2>{weather['city']}, {weather['country']}</h2>
            <p>Weather: {weather['weather']}</p>
            <p>Temperature: {weather['temp']}°C</p>
        </div>
        """
    elif city:
        error_html = '<p class="error">City not found. Please try again.</p>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather App</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 500px;
                margin: 40px auto;
                padding: 20px;
                text-align: center;
                background: #f2f2f2;
                color: black;
            }}

            input, button {{
                padding: 10px;
                font-size: 16px;
                margin: 5px;
            }}

            .card {{
                margin-top: 20px;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 12px;
                background: white;
            }}

            .error {{
                color: red;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Weather App</h1>

        <form action="/search" method="get">
            <input type="text" name="city" placeholder="Enter city name (e.g. Kingston, CA)" required>
            <button type="submit">Search</button>
        </form>

        {weather_html}
        {error_html}
    </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def home():
    return render_page()


@app.get("/search", response_class=HTMLResponse)
def search(city: str):
    weather = get_weather(city)
    return render_page(weather=weather, city=city)