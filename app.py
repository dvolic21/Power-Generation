from fastapi import FastAPI
import requests
import pandas as pd

app = FastAPI()

def fetch_ghi_data(lat, lon, start_year, end_year):
    url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?"
           f"parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}"
           f"&start={start_year}0101&end={end_year}1231&format=JSON")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        ghi_values = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        return ghi_values
    return None

def calculate_average_energy_output(lat, lon, start_year, end_year, panel_area, efficiency):
    ghi_values = fetch_ghi_data(lat, lon, start_year, end_year)
    if not ghi_values:
        return {"error": "Failed to fetch GHI data"}

    df = pd.DataFrame(list(ghi_values.items()), columns=["Date", "GHI"])
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    df["MMDD"] = df["Date"].dt.strftime("%m/%d")
    df = df[df["GHI"] >= 0]
    daily_avg_ghi = df.groupby("MMDD")["GHI"].mean()
    avg_energy_output = daily_avg_ghi * panel_area * efficiency

    return {day: round(value, 2) for day, value in avg_energy_output.items()}

@app.get("/")
def home():
    return {"message": "Solar Energy API is running!"}

@app.get("/energy_output/")
def get_energy_output(lat: float, lon: float, start_year: int, end_year: int, panel_area: float, efficiency: float):
    return calculate_average_energy_output(lat, lon, start_year, end_year, panel_area, efficiency)

