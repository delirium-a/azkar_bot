import requests
from datetime import time

url = "https://api.aladhan.com/v1/timingsByCity"

params = {
    "city": "Moscow",
    "country": "Russia",
    "method": 2
}

response = requests.get(url, params=params)


data = response.json()

fajr_time = data["data"]["timings"]["Fajr"]



split_time = fajr_time.split(":")

print(data["data"]["timings"])

'''
hour, minute = map(int, fajr_time.split(":"))

print(f"Fajr time in Nazran: {hour}:{minute}")
'''
