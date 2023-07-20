# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
import os
import requests
import json
from bs4 import BeautifulSoup
import time

def download_file(url, folder, filename, file_extension=None):
    if not file_extension:
        filename = filename
        file_extension = filename.split(".")[-1]
    else:
        filename = f"{filename}.{file_extension}"
    file_extension_for_string = file_extension.upper()
    print(f"Attempting to download {file_extension_for_string} data from {url}...")
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        # Open the file and read its contents based on the file type
        print_in_green(f"{file_extension} file already exists. Using data from existent file...")
        if file_extension == "json" or file_extension == "html":
            with open(file_path, 'r') as file:
                data = file.read()
                return data
        else:
            return


    start_time = time.time()
    response = requests.get(url, stream=True)  # Use stream=True for large files

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the data to a file
        with open(file_path, 'wb') as file:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_size = 1024  # Adjust this as needed

            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                downloaded_size += len(data)
                progress = downloaded_size / total_size * 100
                print(f"\rDownload progress: {progress:.2f}% ", end="")

        elapsed_time = time.time() - start_time
        print_in_green(f"\n{file_extension_for_string} file downloaded successfully to {file_path}.")
        print_in_green(f"Time taken: {elapsed_time:.2f} seconds.")
        if file_extension == "json" or file_extension == "html":
            with open(file_path, 'r') as file:
                data = file.read()
                return data
        # return data
    else:
        print_in_red(f"\nError: Unable to download {file_extension_for_string} file. Status code: {response.status_code}")
        return None


def download_json_data(url, filename, folder):
    # track_data_url = f"{api_feed_url_prefix}?project_id={librivox_id}&format=json"
    file_extension = "json"
    json_data = download_file(url, folder, filename, file_extension)

    if json_data:
        json_data = json.loads(json_data)
        return json_data

def download_page_html(url, filename, folder):
    file_extension = "html"
    html_data = download_file(url, folder, filename, file_extension)
    html_data = BeautifulSoup(html_data, 'html.parser')

    return html_data

def download_zip_file(url, filename, folder):
    file_extension = "zip"
    zip_file = download_file(url, folder, filename, file_extension)

    unzip_file(filename, folder)

def dump_json_data_into_file(folder, data, filename):
    # Dump the data into a JSON file
    json_data = json.dumps(data)
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w+') as file:
        file.write(json_data)

def unzip_file(filename, folder):
    # if file.endswith('_jp2.zip') or file.endswith("_tif.zip"):
    print_in_green(f"Attempting to unzip {filename}...")
    
    # Specify the path of the "projectfiles" folder
    # projectfiles_path = "projectfiles"
    
    # Specify the command to unzip the file into the target folder
    unzip_command = f"unzip {folder}/{filename} -d {folder}"
    
    # Execute the unzip command
    os.system(unzip_command)
    
    print_in_green("Unzipped successfully.")
    return

    # print_in_red("No accepted .zip file found.")