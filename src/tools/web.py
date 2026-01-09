import webbrowser
import requests
import socket
from bs4 import BeautifulSoup
from ddgs import DDGS

class WebSearch:
    @staticmethod
    def search(query):
        try:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return True, f"Opening browser for: {query}"
        except Exception as e:
            return False, f"Failed to open browser: {str(e)}"

class DDGSearch:
    @staticmethod
    def text_search(query, max_results=3):
        try:
            results = DDGS().text(query, max_results=max_results)
            if not results: return "No results found."
            formatted = [f"- [{r.get('title')}]({r.get('href')}): {r.get('body')}" for r in results]
            return "\n".join(formatted)
        except Exception as e:
            return f"Search failed: {str(e)}"

class WeatherFetcher:
    @staticmethod
    def get_weather(location):
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url).json()
            if not geo_res.get("results"): return f"Location '{location}' not found."
            lat, lon, name = geo_res["results"][0]["latitude"], geo_res["results"][0]["longitude"], geo_res["results"][0]["name"]
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m"
            w_res = requests.get(weather_url).json()
            current = w_res.get("current", {})
            temp, wind, code = current.get("temperature_2m"), current.get("wind_speed_10m"), current.get("weather_code")
            conditions = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Rime fog", 51: "Drizzle: Light", 53: "Drizzle: Moderate", 55: "Drizzle: Dense", 61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy", 71: "Snow: Slight", 73: "Snow: Moderate", 75: "Snow: Heavy", 95: "Thunderstorm"}
            return f"Weather in {name}: {temp}°C, {conditions.get(code, 'Unknown')}, Wind: {wind} km/h."
        except Exception as e:
            return f"Weather fetch failed: {str(e)}"

class WebScraper:
    @staticmethod
    def scrape(url):
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            for s in soup(["script", "style"]): s.decompose()
            text = "\n".join([l.strip() for l in soup.get_text(separator='\n').splitlines() if l.strip()])
            return f"Scraped {url}:\n{text[:2000]}..."
        except Exception as e:
            return f"Scrape failed: {str(e)}"

class NetworkInfo:
    @staticmethod
    def get_ip_info():
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            public_ip = requests.get('https://api.ipify.org', timeout=3).text
            return f"Hostname: {hostname}\nLocal IP: {local_ip}\nPublic IP: {public_ip}"
        except Exception as e: return f"Network info error: {e}"
