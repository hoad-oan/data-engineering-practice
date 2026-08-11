import requests
import os
import urllib.request
import zipfile
import asyncio
import aiohttp
import aiofiles

# define downloads path
download_dir = "downloads"
# create downloads folder, ignore if exist
os.makedirs(download_dir, exist_ok=True)

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

async def check_uri_valid(session: aiohttp.ClientSession, uri: str):
    try:
        async with session.head(uri, timeout = 10, raise_for_status=True) as response: # establish session connection
            return response.status == 200
    except Exception as e:
        print(f"Skipping failed to reach url {uri}: {e}")
        return False

# create function to extract file to be conducted in separate thread while waiting for downloads
def extract_and_del_file(zip_path: str):
    print(f"Unzipping {zip_path} into {download_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(download_dir)
    
    os.remove(zip_path)
    print(f"Delete extracted file {zip_path}")

async def download_file(session: aiohttp.ClientSession, uri: str):
    filename = uri.split("/")[-1]
    zip_path = os.path.join(download_dir, filename)

    # check session validity
    print(f"Checking uri {uri} validity...")
    is_valid_url = await check_uri_valid(session, uri)
    if not is_valid_url:
        print(f"Skipping invalid url {uri}")
        return None

    # download each file in chunks
    print(f"Start downloading {filename}...")
    async with session.get(uri) as response: # estalbish session
        # response.raise_for_status() # get status
        async with aiofiles.open(zip_path, "wb") as f: # save the zip files as binary files
            async for chunk in response.content.iter_chunked(8192): # download files in 8kb pieces
                await f.write(chunk) # await pauses function for disk write operation to finish. CPU can do other things while saving to hard drive...
    print(f"Finished downloading {filename}...")

    # unzip the file in separate thread due to being CPU-heavy
    target_folder = os.path.join(download_dir, os.path.splitext(filename)[0])

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, extract_and_del_file, zip_path) # while different thread is extracting, CPU can do other things...

async def main():
    async with aiohttp.ClientSession() as session:
        # create list of async tasks, download all URls at the same time
        tasks = [download_file(session, uri) for uri in download_uris]
        # run all tasks concurrently
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
