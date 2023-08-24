# WS_collection

import pywikibot
import re
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import remove_all_instances
import os
import requests
from bs4 import BeautifulSoup

"""

<a class="format-summary download-pill" href="/stream/masterfrisky00hawk/masterfrisky00hawk_djvu.txt" title="" data-toggle="tooltip" data-placement="auto left" data-container="body" data-original-title="127.0K">
  FULL TEXT 
<span class="iconochive-download" aria-hidden="true"><span>
<span class="icon-label sr-only">download</span>
</a>
              
"""

def get_download_links(soup):
    # Find all <tr> elements
    trs = soup.find_all('tr')
    links = []

    # Iterate over each <tr> element
    for tr in trs:
        # Find the first <td> element
        first_td = tr.find('td')
        
        # Check if the first <td> element exists
        if first_td:
            # Find the <a> element within the <td> element
            a_element = first_td.find('a')
            
            # Check if the <a> element exists
            if a_element:
                # Get the value of the 'href' attribute
                href = a_element['href']
                
                # Print the href value
                links.append(href)
    return links

def filter_needed_files(links):

    accepted_suffixes = [
        '.txt',
        '.pdf',
        '.djvu',
        '_jp2.zip',
        '_tif.zip',
    ]

    needed_files = []
    for link in links:
        for suffix in accepted_suffixes:
            if link.endswith(suffix):
                needed_files.append(link)
    return needed_files

def get_IA_files(IA_id):
    url = f"https://archive.org/download/{IA_id}"
    print("Attempting to get the full text file from:", url)
    response = requests.get(url)

    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')

        links = get_download_links(soup)
        filenames = filter_needed_files(links)

        for filename in filenames:
            download_url = f"{url}/{filename}"
            print(f"Attempting to download {filename} from {download_url}...")

            # Extract the filename from the download URL
            # filename = link.split('/')[-1]
            
            # Set the path where the file will be saved
            file_path = os.path.join('projectfiles', filename)
            
            # Send a request to download the file
            response = requests.get(download_url)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Save the file
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print_in_green(f"Download successful for {filename}!")
            else:
                print_in_red(f"Failed to download {filename}!")
                # return None
        return filenames
        




        # catalog_link = soup.find('a', {'data-tracking-action': 'PT VuFind Catalog Record'})
        
        # if catalog_link:
        #     catalog_url = catalog_link['href']
        #     catalog_id = catalog_url.split('/')[-1]
        #     print_in_green(f"Success. HathiTrust catalog ID: {catalog_id}")
        #     return catalog_id
        # print_in_red("HathiTrust catalog ID not found.")
        # return None

    print_in_red(f"Response code not 200. Was: {response.status_code}")
    return None

# import os

def unzip_jp2_folder(IA_files):
    for file in IA_files:
        if file.endswith('_jp2.zip') or file.endswith("_tif.zip"):
            print_in_green(f"Attempting to unzip {file}...")
            
            # Specify the path of the "projectfiles" folder
            projectfiles_path = "projectfiles"
            
            # Specify the path where the unzipped folder will be created
            # unzipped_folder_path = os.path.join(projectfiles_path, "image_files_ia")
            
            # Create the unzipped folder if it doesn't exist
            # os.makedirs(unzipped_folder_path, exist_ok=True)
            
            # Specify the command to unzip the file into the target folder
            unzip_command = f"unzip {projectfiles_path}/{file} -d {projectfiles_path}"
            
            # Execute the unzip command
            os.system(unzip_command)
            
            print_in_green("Unzipped successfully.")
            return
    
    print_in_red("No accepted .zip file found.")

def get_ia_id_from_url(url):
    if "\/" in url:
        parameters = url.split("\/")
    else:
        parameters = url.split("/")

    parameters = remove_all_instances(parameters, "")

    acceptable_parameters = [
        "compress",
        "details",
        "download",
        "stream",
    ]

    internet_archive_id = None

    for parameter_num, parameter in enumerate(parameters):
        if parameter in acceptable_parameters:
            internet_archive_id = parameters[parameter_num + 1]
            internet_archive_id = internet_archive_id.split("?")[0]
            internet_archive_id = internet_archive_id.split("&")[0]
            break
    
    return internet_archive_id

def get_google_books_id_from_ia(IA_id):
    IA_url = f"https://archive.org/details/{IA_id}"

    response = requests.get(IA_url)

    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        # soup = BeautifulSoup(response.content, 'html.parser')
        IA_content = str(response.content)

        if "books.google.com" in IA_content:
            google_books_id = re.search(r"books\.google\.com\/books\?id=(.+?)\"", IA_content).group(1)[:12]

            return google_books_id
        else:
            print("No Google Books ID found. Skipping step...")

# get_IA_files("masterfrisky00hawk")