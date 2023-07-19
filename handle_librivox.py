# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break
from edit_mw import remove_all_instances, remove_bad_symbols_from_filename
import os
import requests
import json
from handle_web_downloads import download_json_data, download_page_html, dump_json_data_into_file
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






def append_book_data(book_data, book_data_filename, librivox_folder, catalog_html_data=None):
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

    reader = get_book_reader_data(catalog_html_data, reader_key)
    book_coordinator = get_book_reader_data(catalog_html_data, book_coordinator_key)
    meta_coordinator = get_book_reader_data(catalog_html_data, meta_coordinator_key)
    proof_listener = get_book_reader_data(catalog_html_data, proof_listener_key)

    catalog_date = get_catalog_date(catalog_html_data)

    cover_url, cd_case_insert_url = get_librivox_image_data(catalog_html_data)

    book_data["reader"] = reader
    book_data["book_coordinator"] = book_coordinator
    book_data["meta_coordinator"] = meta_coordinator
    book_data["proof_listener"] = proof_listener

    book_data["internet_archive_id"] = internet_archive_id
    book_data["catalog_date"] = catalog_date

    book_data["cover_url"] = cover_url
    book_data["cd_case_insert_url"] = cd_case_insert_url

    book_data_filename = f"{book_data_filename}.json"
    dump_json_data_into_file(librivox_folder, book_data, book_data_filename)

    return book_data
    # print(book_data)

def generate_track_commons_filename(track, work_title):
    "File:Aristopia LibriVox track 00 - Introduction.mp3"

    section_number = track['section_number']
    section_title = track['title']

    track_title = f"{work_title} LibriVox track {section_number} - {section_title}.mp3"
    track_title = remove_bad_symbols_from_filename(track_title)
    return track_title

def get_catalog_date(catalog_html_data):
    catalog_key = "Catalog date:"
    catalog_date = catalog_html_data.find('dt', string=catalog_key).find_next('dd').text
    return catalog_date

def append_track_data(track_data, catalog_html_data, book_reader, work_title, track_data_filename, librivox_folder):
    if "sections" in track_data:
        track_data = track_data["sections"]

    "chapter-download"
    book_reader_id = book_reader["id"]
    if not book_reader_id:
        readers = get_track_reader_data(catalog_html_data)

    

    new_track_data = []
    for track_num, track in enumerate(track_data):

        if book_reader_id:
            track["reader"] = book_reader
        else:
            track["reader"] = readers[track_num]
        
        track_commons_filename = generate_track_commons_filename(track, work_title)

        track["commons_filename"] = track_commons_filename

        new_track_data.append(track)

    track_data_filename = f"{track_data_filename}.json"
    dump_json_data_into_file(librivox_folder, new_track_data, track_data_filename)
    return new_track_data


def get_librivox_catalog_name_from_url(url):
    if "\/" in url:
        parameters = url.split("\/")
    else:
        parameters = url.split("/")

    parameters = remove_all_instances(parameters, "")

    catalog_name = parameters[2]

    return catalog_name

def get_book_reader_data(catalog_html_data, reader_key):
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

def get_track_reader_data(catalog_html_data):
    download_anchors = catalog_html_data.find_all('a', class_='chapter-name')

    readers = []
    for anchor in download_anchors:
        link = anchor.find_next('a')
        reader_url = link['href']
        reader_name = link.text
        reader_id = get_librivox_reader_id_from_url(reader_url)

        reader = {
            "id": reader_id,
            "name": reader_name,
        }

        readers.append(reader)
    
    return readers

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

def download_audio_tracks(librivox_id):
    pass

def download_librivox_data(librivox_id, work_title):
    print("Downloading LibriVox data...")
    librivox_folder = "projectfiles/librivox"

    book_data_url = f"{api_feed_url_prefix}audiobooks/?id={librivox_id}{api_url_json_suffix}"
    book_data_filename = "book_data"
    book_data = download_json_data(book_data_url, book_data_filename, librivox_folder)

    track_data_url = f"{api_feed_url_prefix}audiotracks/?project_id={librivox_id}{api_url_json_suffix}"
    track_data_filename = "track_data"
    track_data = download_json_data(track_data_url, track_data_filename, librivox_folder)

    book_data = append_book_data(book_data, book_data_filename, librivox_folder)

    librivox_url = book_data["url_librivox"]
    html_filename = "catalog"
    catalog_html_data = download_page_html(librivox_url, html_filename, librivox_folder)

    book_data = append_book_data(book_data, book_data_filename, librivox_folder, catalog_html_data)
    print(book_data)

    reader = book_data["reader"]

    track_data = append_track_data(track_data, catalog_html_data, reader, work_title, track_data_filename, librivox_folder)

    print(track_data)


    "https://archive.org/compress/{internet_archive_id}/formats=128KBPS%20MP3&file=/{internet_archive_id}.zip"


download_librivox_data("7777", "Aristopia")