# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break
import os
import requests
import json
from ia import get_ia_id_from_url
from bs4 import BeautifulSoup


# AT COMMONS THIS IS WHAT IT SHOULD LOOK LIKE (or better)
# Category:{work_category}
# Category:LibriVox recordings in English
## Category:LibriVox - The 9/11 Commission Report
## Category:LibriVox - The Adventures of Sherlock Holmes, by Arthur Conan Doyle
# File:Mine and Thine librivox cover.jpg, File:Thy Soul Shall Bear Witness librivox cover.jpg - Album covers are released into the public domain, according to this file
## Category:LibriVox cover art
## Category:LibriVox CD case inserts


# https://librivox.org/api/feed/audiobooks/?id=7777&format=json - Aristopia book data
# https://librivox.org/api/feed/audiotracks/?project_id=7777&format=json - Aristopia chapter data


# Download the following files:
#: Book data (JSON)
#: Chapter data (JSON)
#: Audio files
#: Album cover
#: CD case insert

api_feed_url_prefix = "https://librivox.org/api/feed/"
api_url_json_suffix = "&format=json"

def get_librivox_work_link(librivox_id):
    pass

def download_json_data(url, file_prefix, folder):
    # track_data_url = f"{api_feed_url_prefix}?project_id={librivox_id}&format=json"
    print(f"Attempting to download JSON data from {url}...")
    filename = f"{file_prefix}_data.json"
    file_path = os.path.join(folder, filename)

    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the JSON data to a file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print_in_green(f"JSON file downloaded successfully to {file_path}.")
        data = json.loads(response.content)
        return data
    else:
        print_in_red(f"Error: Unable to download JSON file. Status code: {response.status_code}")
        return None

def append_book_data(book_data):
    book_data = book_data["books"][0]
    ia_zip_file_link = book_data["url_zip_file"]
    internet_archive_id = get_ia_id_from_url(ia_zip_file_link)

    book_data["internet_archive_id"] = internet_archive_id
    

def download_audio_files(librivox_id):
    pass

def download_librivox_data(librivox_id):
    librivox_folder = "projectfiles/librivox"

    book_data_url = f"{api_feed_url_prefix}audiobooks/?id={librivox_id}{api_url_json_suffix}"
    book_data_file_prefix = "book"
    book_data = download_json_data(book_data_url, book_data_file_prefix, librivox_folder)

    track_data_url = f"{api_feed_url_prefix}audiotracks/?project_id={librivox_id}{api_url_json_suffix}"
    track_data_file_prefix = "track"
    track_data = download_json_data(track_data_url, track_data_file_prefix, librivox_folder)

    book_data = append_book_data(book_data)


download_librivox_data("7777")