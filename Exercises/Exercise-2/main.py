import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

URL = "https://www.ncei.noaa.gov/data/local-climatological-data/access/2024/"

session = requests.Session() # enable the ability to reuse session connection and close at end of code

def scrape_data():
    try:
        response = session.get(URL, timeout = 30)
        html_data = response.text
        print(response.status_code)
        response.raise_for_status() # raise exception for response.status != 200
        soup = BeautifulSoup(html_data, "html.parser")

        tbody = soup.find("tbody")

        if tbody:
            for row in tbody.find_all("tr"):
                row_data = []
                for cell in row.find_all("td"):
                    row_data.append(cell.get_text(strip=True))
                    if len(row_data) > 1 and row_data[1] == "2025-01-24 05:23":
                        print("Found file")
                        target_file = row_data[0]
                        return target_file

        return None

    except Exception as e:
        print(f"Failed to get data: {e}")
        return None
    
def download_target_file(target_url: str, saved_file_path: str):
    response = session.get(target_url, stream=True, timeout = 30)
    response.raise_for_status()

    with open(saved_file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def find_highest_record(saved_file_path):
    df = pd.read_csv(saved_file_path)
    highest_HourlyDryBulbTemperature = df.nlargest(1,"HourlyDryBulbTemperature").to_dict(orient="records")
    print(highest_HourlyDryBulbTemperature)

# https://www.ncei.noaa.gov/data/local-climatological-data/access/2024/01001099999.csv

def main():
    target_file = scrape_data()
    
    if target_file is not None:
        target_url = f"{URL}{target_file}"
        # Get the directory where THIS script file lives
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the downloads folder path next to the script
        download_dir = os.path.join(script_dir, "downloads")
        os.makedirs(download_dir, exist_ok=True)
        saved_file_path = os.path.join(download_dir, target_file)
        download_target_file(target_url, saved_file_path)

        # read file and get highest record
        find_highest_record(saved_file_path)

    else:
        return None
    pass
    # find_highest_record("/Users/hoadoan/Coding/data-engineerig-practice/Exercises/Exercise-2/downloads/01002099999.csv")



if __name__ == "__main__":
    main()

session.close()


# 1. Attempt to web scrap/pull down the contents of `https://www.ncei.noaa.gov/data/local-climatological-data/access/2024/`
# 2. Analyze it's structure, determine how to find the corresponding file to `2024-01-19 10:27	` using Python.
# 3. Build the `URL` required to download this file, and write the file locally.
# 4. Open the file with `Pandas` and find the records with the highest `HourlyDryBulbTemperature`.
# 5. Print this to stdout/command line/terminal.