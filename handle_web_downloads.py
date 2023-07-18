# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
import os
import requests
import json
from bs4 import BeautifulSoup

def download_file(url, filename, file_extension, folder):
    file_extension_for_string = file_extension.upper()
    print(f"Attempting to download {file_extension_for_string} data from {url}...")
    filename = f"{filename}.{file_extension}"
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        # Open the file and read its contents based on the file type
        print_in_green(f"{file_extension} file already exists. Using data from existent file...")
        with open(file_path, 'r') as file:
            data = file.read()
            return data

    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the data to a file
        data = response.content
        with open(file_path, 'wb') as file:
            file.write(data)
        print_in_green(f"{file_extension_for_string} file downloaded successfully to {file_path}.")
        return data
        # data = json.loads(response.content)
        # return data
    else:
        print_in_red(f"Error: Unable to download {file_extension_for_string} file. Status code: {response.status_code}")
        return None

def download_json_data(url, filename, folder):
    # track_data_url = f"{api_feed_url_prefix}?project_id={librivox_id}&format=json"
    file_extension = "json"
    json_data = download_file(url, filename, file_extension, folder)

    if json_data:
        json_data = json.loads(json_data)
        return json_data

def download_page_html(url, filename, folder):
    file_extension = "html"
    html_data = download_file(url, filename, file_extension, folder)
    html_data = BeautifulSoup(html_data, 'html.parser')

    return html_data