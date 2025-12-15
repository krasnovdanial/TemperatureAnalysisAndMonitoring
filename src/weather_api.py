import aiohttp
import requests


def get_weather_sync(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['main']['temp']
    except Exception as e:
        print(f"Ошибка (Sync) {city}: {e}")
        return None


async def get_weather_async(session, city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {"temp": data['main']['temp'], "error": None}
            else:
                text = await response.text()
                return {"temp": None, "error": response.status, "message": text}
    except Exception as e:
        return {"temp": None, "error": 500, "message": str(e)}


if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv

    load_dotenv()
    test_api_key = os.getenv("OPENWEATHER_API_KEY")
    test_cities = ["Berlin", "Moscow"]

    print("Тест Sync ")
    for city in test_cities:
        print(f"{city}: {get_weather_sync(city, test_api_key)}")

    print("Тест Async")


    async def main_test():
        async with aiohttp.ClientSession() as session:
            tasks = [get_weather_async(session, city, test_api_key) for city in test_cities]
            results = await asyncio.gather(*tasks)
        for city, res in zip(test_cities, results):
            print(f"{city}: {res}")


    asyncio.run(main_test())
