# WS_collection

import os
import requests
from handle_web_downloads import download_file
from bs4 import BeautifulSoup

def download_gutenberg_directory(directory_url, base_folder, new_folder=None):
    response = requests.get(directory_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Create a local directory to save the files
    # directory_name = os.path.basename(os.path.normpath(directory_url))
    if new_folder:
        new_folder_path = os.path.join(base_folder, new_folder)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        base_folder += f"/{new_folder}"

    # Download each file in the directory
    for row in soup.find_all("tr")[2:]:  # Skip the first row containing table headers
        columns = row.find_all("td")
        if not columns:
            break
        file_type = columns[0].img["alt"]
        file_name = columns[1].a["href"]

        if "/files/" in file_name:
            continue

        file_url = f"{directory_url}/{file_name}"

        # If the file is a directory, recursively download files from that directory
        if file_type == "[DIR]":
            folder_name = file_name
            download_gutenberg_directory(file_url, base_folder, new_folder=folder_name)
        # Generate the file URL and download it
        else:
            download_file(file_url, base_folder, file_name)


def download_gutenberg_files(gutenberg_id):
    url = f"https://www.gutenberg.org/files/{gutenberg_id}"
    base_folder = "projectfiles/gutenberg"
    download_gutenberg_directory(url, base_folder)

download_gutenberg_files("5172")