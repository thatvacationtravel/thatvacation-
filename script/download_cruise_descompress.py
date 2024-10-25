import os
import shutil
import requests
from zipfile import ZipFile

DOWNLOAD_DIR = "/home/tvacation/thatvacation/json"

USERNAME = "flat_usa"
PASSWORD = "nj823r"

URLS = [
    "https://www.msconline.com/DownloadArea/ONDEMAND/usa/flatfile_usa_fares_csv.zip",
]

if os.path.exists(DOWNLOAD_DIR):
    shutil.rmtree(DOWNLOAD_DIR)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_file(url, directory, username, password):
    local_filename = os.path.join(directory, url.split('/')[-1])

    with requests.get(url, auth=(username, password), stream=True) as response:
        response.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def unzip_file(zip_path, extract_to):
    # Descomprimir el archivo ZIP
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Descargar y descomprimir cada archivo ZIP
for url in URLS:
    print(f"Descargando {url}")
    zip_file_path = download_file(url, DOWNLOAD_DIR, USERNAME, PASSWORD)
    print(f"Descomprimiendo {zip_file_path}")
    unzip_file(zip_file_path, DOWNLOAD_DIR)

print("Descarga y descompresión completadas.")
