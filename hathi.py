# WS_collection
import mwparserfromhell
import pywikibot
import re
import requests
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break, save_html_to_file
from bs4 import BeautifulSoup
import os


"""
Pywikibot: From the Commons page of the PDF file, get the HathiTrust ID from the Book template using mwparserfromhell to parse this template. The HathiTrust ID is in the second parameter: "uc1.b3834650":

=={{int:filedesc}}==
{{Book
|author = Mazo de la Roche
|illustrator = 
|title = Jalna 
|volume = 
|publisher = Macmillan
|source = {{HathiTrust|uc1.b3834650|book}}
|series title = 
|language = 
|description =
|permission = 
|OCLC = 
|publication date = 1927
|Wikidata = 
|Image page = 7
|notes = 
}}


"""

def get_hathitrust_id_from_commons_page(filename):
    site = pywikibot.Site('commons', 'commons')
    page_title = "File:" + filename
    print("Attempting to find HathiTrust ID from the Commons page:", page_title)
    page = pywikibot.Page(site, page_title)

    # Get the contents of the page
    text = page.text

    # Parse the wikitext
    wikicode = mwparserfromhell.parse(text)

    # Find the Book template
    templates = wikicode.filter_templates(matches='Book')
    if templates:
        template = templates[0]  # Assuming there's only one Book template
        source_param = template.get('source')
        if source_param:
            hathitrust_template = mwparserfromhell.parse(source_param.value.strip())
            hathitrust_id = hathitrust_template.filter_templates()[0].get(1).value.strip()
            print_in_green(f"HathiTrust ID found! ID: {hathitrust_id}")
            return hathitrust_id
        else:
            print_in_yellow("HathiTrust template not found in the source parameter.")
    else:
        print_in_red("Book template not found.")
    return None

# hathitrust_id = get_hathitrust_id_from_commons_page('Jalna.pdf')

# print(hathitrust_id)

"""
Get the HathiTrust catalog id (for example "006729930" as in https://catalog.hathitrust.org/Record/006729930) from the ID retrieved above (for example "uc1.b3834650"). First of all, how could we do that with just that information, and second of all, write Python function that does that.
"""

"""
HT.params.externalLinks = [{"href":"http://www.amazon.com/exec/obidos/ASIN/B006OKXAWA","type":"pod"}]

      HT.params.download_progress_base = '/cache/progress';
      HT.params.RecordURL = 'https://catalog.hathitrust.org/Record/000762802';
    </script>
"""

def get_hathitrust_catalog_id(hathitrust_id):
    if type(hathitrust_id) == list:
        hathitrust_id = "/".join(hathitrust_id)
    # hathitrust_id = hathitrust_id.replace(":", "%3A")
    url = f"https://babel.hathitrust.org/cgi/pt?id={hathitrust_id}"
    print("Attempting to get the HathiTrust catalog ID from:", url)
    response = requests.get(url)

    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        # soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup)
        # exit()
        # catalog_link = soup.find('a', {'data-tracking-action': 'PT VuFind Catalog Record'})
        catalog_id = re.findall(r"'https:\//catalog.hathitrust.org\/Record\/([0-9]+?)'", response.text)
        
        if catalog_id:
            catalog_id = catalog_id[0]
            print_in_green(f"Success. HathiTrust catalog ID: {catalog_id}")
            return catalog_id
        print_in_red("HathiTrust catalog ID not found.")
        return None

    print_in_red(f"Response code not 200. Was: {response.status_code}")
    return None

def extract_full_text_id_from_link(link):
    """ link example: https://hdl.handle.net/2027/nyp.33433082345145 """
    print("Attempting to extract the full text ID from:", link)
    full_text_id = link.split('/')[-1]
    return full_text_id

def get_hathitrust_full_text_id(catalog_id):
    url = f"https://catalog.hathitrust.org/Record/{catalog_id}"
    print("Attempting to get the HathiTrust scan link from:", url)
    response = requests.get(url)

    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')
        fulltext_links = soup.find_all('a', class_='fulltext')
        

        if len(fulltext_links) > 0:
            # scan_url = scan_link['href']
            scan_link = fulltext_links[0].get('href')
            print_in_green(f"Success. HathiTrust scan link: {scan_link}")
            full_text_id = extract_full_text_id_from_link(scan_link)
            print_in_green(f"Success. HathiTrust full text ID: {full_text_id}")
            return full_text_id
        print_in_red("HathiTrust scan link not found.")
        return None

    print_in_red(f"Response code not 200. Was: {response.status_code}")
    return None

def get_number_of_pages(full_text_id):
    print("Retrieving number of pages in scan...")
    url = f"https://babel.hathitrust.org/cgi/pt?id={full_text_id}"
    response = requests.get(url)
    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')
        output_group = soup.find('div', class_='bg-dark')
        script_tag = soup.find('script')

        # Get the JavaScript code within the script tag
        js_code = script_tag.string

        # Now, extract the value of "HT.params.totalSeq" from the JavaScript code
        total_seq_value = None
        lines = js_code.splitlines()
        for line in lines:
            if 'HT.params.totalSeq' in line:
                total_seq_value = line.split('=')[-1].strip().rstrip(';')
                break

        number_of_pages = int(total_seq_value)
        print_in_green(f"Number of pages found! Number of pages in scan: {number_of_pages}")
        return number_of_pages
    print_in_red(f"Response code not 200. Was: {response.status_code}")
    return None

def get_hathitrust_images(full_text_id, folder_path=None):
    # page_source = get_full_text_page_source(url)
    if type(full_text_id) == list:
        full_text_id = "/".join(full_text_id)
    number_of_pages = get_number_of_pages(full_text_id)
    print(f"Attempting to download the {number_of_pages} HathiTrust images from {full_text_id}...")
    
    if not folder_path:
        folder_path = "projectfiles/hathi_images"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print_in_green(f"Created folder path {folder_path} as it did not exist.")
    
    for page_num in range(1, number_of_pages+1):
        print(f"Attempting to download {page_num} of {number_of_pages}...")
        page_url = f"https://babel.hathitrust.org/cgi/imgsrv/image?id={full_text_id};seq={page_num};size=200;rotation=0"

        while 1: # make SURE the image downloads.
            response = requests.get(page_url)
            if response.status_code == 200:
                # Save the image to the specified path
                image_path = os.path.join(folder_path, f"{page_num}.jpg")
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                    print_in_green(f"Image for page #{page_num} saved successfully!")
                    break

            print_in_red(f"Failed to download the image file for page #{page_num}! Trying again...")

    print_in_green(f"All images downloaded from Hathi scan {full_text_id} successfully!")

    return folder_path
    # return img_tags

def get_oclc_from_hathi(hathitrust_id):
    url = f"https://catalog.hathitrust.org/Record/{hathitrust_id}"
    print("Attempting to get the OCLC link from:", url)
    response = requests.get(url)

    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        page_content = str(response.content)
        
        if "/oclc/" in page_content:
            oclc = re.findall(r'\/oclc\/([0-9]+?)\"', page_content)[0]
            print_in_green(f"Success. OCLC: {oclc}")
            return oclc
        print_in_red("OCLC link not found.")
        return None

    print_in_red(f"Response code not 200. Was: {response.status_code}")
    return None

def get_ark_identifier_from_hathi(hathitrust_full_text_id):
    if type(hathitrust_full_text_id) == list:
        hathitrust_full_text_id = "/".join(hathitrust_full_text_id)
        if "uc2.ark" in hathitrust_full_text_id:
            ark_identifier = hathitrust_full_text_id[4:]
            return ark_identifier

    return None