# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break
from edit_mw import remove_all_instances
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

def append_book_data(book_data, catalog_html_data=None):
    if "books" in book_data:
        book_data = book_data["books"][0]

    if not catalog_html_data:
        return book_data

    ia_zip_file_link = book_data["url_zip_file"]
    internet_archive_id = get_ia_id_from_url(ia_zip_file_link)

    # Extract the HREF values
    reader_key = 'Read by:'
    book_coordinator_key = 'Book Coordinator:'
    meta_coordinator_key = 'Meta Coordinator:'
    proof_listener_key = 'Proof Listener:'

    reader = get_reader_data(catalog_html_data, reader_key)
    book_coordinator = get_reader_data(catalog_html_data, book_coordinator_key)
    meta_coordinator = get_reader_data(catalog_html_data, meta_coordinator_key)
    proof_listener = get_reader_data(catalog_html_data, proof_listener_key)

    cover_url, cd_case_insert_url = get_librivox_image_data(catalog_html_data)

    book_data["reader"] = reader
    book_data["book_coordinator"] = book_coordinator
    book_data["meta_coordinator"] = meta_coordinator
    book_data["proof_listener"] = proof_listener

    book_data["internet_archive_id"] = internet_archive_id

    book_data["cover_url"] = cover_url
    book_data["cd_case_insert_url"] = cd_case_insert_url

    return book_data
    # print(book_data)

def get_librivox_catalog_name_from_url(url):
    if "\/" in url:
        parameters = url.split("\/")
    else:
        parameters = url.split("/")

    parameters = remove_all_instances(parameters, "")

    catalog_name = parameters[2]

    return catalog_name

def get_reader_data(catalog_html_data, reader_key):
    reader_anchor = catalog_html_data.find('dt', string=reader_key).find_next('dd').find('a')
    if reader_anchor:
        reader_url = reader_anchor['href']
        reader_id = get_librivox_reader_id_from_url(reader_url)
    else:
        reader_id = None
    
    reader_name = catalog_html_data.find('dt', string=reader_key).find_next('dd').text

    reader_data = {
        "id": reader_id,
        "name": reader_name,
    }

    return reader_data

def get_librivox_image_data(catalog_html_data):
    download_links = catalog_html_data.find_all('a', class_='download-cover')

    # Loop through the results and print the HREF and text of each link
    for link in download_links:
        href = link['href']
        text = link.text
        if "cover" in text:
            cover_url = href
        if "CD case insert" in text:
            cd_case_insert_url = href
    
    return cover_url, cd_case_insert_url


def get_librivox_reader_id_from_url(url):
    if "\/" in url:
        parameters = url.split("\/")
    else:
        parameters = url.split("/")

    parameters = remove_all_instances(parameters, "")
    
    reader_id = parameters[-1]

    return reader_id

def download_audio_files(librivox_id):
    pass

def download_librivox_data(librivox_id):
    print("Downloading LibriVox data...")
    librivox_folder = "projectfiles/librivox"

    book_data_url = f"{api_feed_url_prefix}audiobooks/?id={librivox_id}{api_url_json_suffix}"
    book_data_filename = "book_data"
    book_data = download_json_data(book_data_url, book_data_filename, librivox_folder)

    track_data_url = f"{api_feed_url_prefix}audiotracks/?project_id={librivox_id}{api_url_json_suffix}"
    track_data_filename = "track_data"
    track_data = download_json_data(track_data_url, track_data_filename, librivox_folder)

    book_data = append_book_data(book_data)

    librivox_url = book_data["url_librivox"]
    html_filename = "catalog"
    catalog_html_data = download_page_html(librivox_url, html_filename, librivox_folder)

    book_data = append_book_data(book_data, catalog_html_data)
    print(book_data)


    "https://archive.org/compress/{internet_archive_id}/formats=128KBPS%20MP3&file=/{internet_archive_id}.zip"


download_librivox_data("7777")