# WS_collection

import os
import requests
from handle_web_downloads import download_file
from bs4 import BeautifulSoup
from handle_wikisource_conf import get_year_from_date
import copy

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

def download_gutenberg_ebooks(gutenberg_id, base_folder):
    ebooks_url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}"
    response = requests.get(ebooks_url)
    ebooks_html_data = BeautifulSoup(response.content, "html.parser")

    for row in ebooks_html_data.find_all("tr"):
        file_url = row.get("about")
        if file_url:
            if "/ebooks/" in file_url:
                if file_url.endswith(".html.images"):
                    download_file(file_url, base_folder, "file_to_parse.html")
                else:
                    filename = file_url.split("/")[-1]
                    filename = filename.replace(".noimages", "")
                    filename = filename.replace(".images", "")
                    download_file(file_url, base_folder, filename)


def download_gutenberg_files(gutenberg_id, base_folder):
    other_files_url = f"https://www.gutenberg.org/files/{gutenberg_id}"
    download_gutenberg_ebooks(gutenberg_id, base_folder)
    download_gutenberg_directory(other_files_url, base_folder)

def find_gutenberg_html_file(base_folder):
    html_file_name = "file_to_parse.html"
    html_file_path = os.path.join(base_folder, html_file_name)
    with open(html_file_path, "r") as html_file:
        html_data = html_file.read()
    html_data = BeautifulSoup(html_data, "html.parser")
    return html_data


def remove_bad_elements(elements):
    while 1:
        bad_element_count = 0
        # new_elements = []
        for element in elements:
            extraction_conditions = [
                not element.get_text(strip=True),

                (len(element.contents) == 1 and element.contents[0].name == 'br'),

                'pg-boilerplate' in element.get('class', []),

                element.name == "head",

                element.name == "style",

                'toc' in element.get('class', []),
            ]

            if any(extraction_conditions):
                element.extract()
        # elements = new_elements
        if bad_element_count == 0:
            break

    return elements

def final_cleanup(html_data):
    html_data = str(html_data)

    html_data = html_data.replace("<!DOCTYPE html>", "")
    # get rid of too many newlines function

    # bad apostrophes/quotes
    html_data = html_data.replace("”", "\"")
    html_data = html_data.replace("“", "\"")
    html_data = html_data.replace("’", "'")
    html_data = html_data.replace("‘", "'")

    # trailing dots
    html_data = html_data.replace(".....", " . . . . . ")
    html_data = html_data.replace("....", " . . . . ")
    html_data = html_data.replace("...", " . . . ")
    html_data = html_data.replace("..", " . . ")

    # hyphen/apostrophe combinations, because we might as well go ahead and do it so we see it more quickly during transcription
    html_data = html_data.replace("\"'", "{{\" '}}")
    html_data = html_data.replace("'\"", "{{' \"}}")
    html_data = html_data.replace("''", "{{' '}}")
    html_data = html_data.replace("\"\"", "{{\" \"}}")
    html_data = html_data.replace("\"'\"", "{{\" ' \"}}")
    html_data = html_data.replace("'\"'", "{{' \" '}}")

    # tags
    html_data = html_data.replace("<br/>", "<br />")

    # bad formatting
    html_data = html_data.replace("\n ", "\n")

    return html_data

def remove_white_space(string):
    string = string.replace("\n", " ")
    while "  " in string:
        string = string.replace("  ", " ")
    return string

def handle_paragraphs(elements):
    for element in elements:
        if element.name == "p":
            # element_text = element.get_text(strip=True)
            # print("Original element text:", element_text)
            # element_text = remove_white_space(element_text)
            # print("Modified element text:", element_text)
            # Extract the text content from the "p" element
            element.unwrap()
            # print("Original paragraph text:", paragraph_text)

            # Update the content of the original BeautifulSoup element
            # element.string.replace_with(paragraph_text)

            # Create a new BeautifulSoup element with the modified text
            # new_element = BeautifulSoup(element_text, "html.parser")

            # Add the new element to the list of modified elements
            # new_elements.append(new_element)

        # else:
            # For elements other than "p", add them to the list as is
            # new_elements.append(element)

    # Replace the original elements list with the new modified elements list
    # elements.clear()
    # elements.extend(new_elements)
    return elements


    # return new_elements


# Example usa

def parse_gutenberg_text(gutenberg_id, base_folder):
    print("Parsing Gutenberg HTML file into QT markup...")
    html_data = find_gutenberg_html_file(base_folder)
    
    # take out empty elements
    # elements = html_data.find_all().copy()
    
    
    elements = html_data.find_all()
    
    elements = remove_bad_elements(elements)
    # print(html_data)
    # print(elements)
    elements = html_data.find_all()

    # print("THESE ARE ELEMENTS AFTER REMOVE BAD ELEMENTS")
    # exit()
    # print("DID I EVEN GET HERE?")
    # exit()
    elements = handle_paragraphs(elements)

    # elements = html_data.find_all()
    # exit()

    # html_data = BeautifulSoup("\n".join(list(elements)), "html.parser")

    html_data = final_cleanup(html_data)
    # print(html_data)

    # write new html to file

    with open("projectfiles/gutenberg/new.html", "w+") as html_file:
        # print(html_data)
        html_file.write(str(html_data))
        html_file.close()
    # print(html_data)
    

def get_date_from_gutenberg(gutenberg_id):
    gutenberg_url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}"
    print(f"Retrieving year and date from Gutenberg url {gutenberg_url}...")
    response = requests.get(gutenberg_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # <td itemprop="datePublished">Sep 1, 1997</td> find the element with "itemprop" value of datePublished, and get the text within it
    date = soup.find("td", {"itemprop": "datePublished"}).get_text()
    year = get_year_from_date(date)

    return year, date

# base_folder = "projectfiles/gutenberg"

# gutenberg_id = "5172"

# # download_gutenberg_files(gutenberg_id, base_folder)
# # download_gutenberg_ebooks(gutenberg_id, base_folder)
# parse_gutenberg_text(gutenberg_id, base_folder)