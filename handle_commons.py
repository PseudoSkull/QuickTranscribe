# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break
from handle_wikidata import get_commons_category_from_wikidata
from edit_mw import linkify, edit_summary, save_page, remove_template_markup
from handle_projectfiles import find_scan_file_to_upload, get_json_data, write_to_json_file, get_images_to_upload
from handle_wikidata import get_value_from_property, add_property
import pywikibot
import re
import math
import time
import os
import io
from pywikibot.data.api import Request
# from pywikibot.upload import UploadRobot
# from pywikibot import upload


def get_image_filename(image):
    image_title = image["title"]
    image_extension = image["extension"]
    image_filename = f"{image_title}.{image_extension}"
    return image_filename

def convert_to_megabytes(size):
    return size * (1024 * 1024)


def is_file_size_greater_than_3mb(file_path):
    three_mb = convert_to_megabytes(3)
    try:
        size = os.path.getsize(file_path)
        return size > three_mb
    except FileNotFoundError:
        print_in_red(f"File not found at path: {file_path}")
    except Exception as e:
        print_in_red(f"Error occurred while checking file size: {e}")

def upload_file_to_commons(filename, file_text, file_path, transcription_page_title):
    # filename = "Test upload with batch upload.pdf"

    print(f"Uploading file {filename} to Wikimedia Commons from {file_path}...")
    
    summary = f"Uploading \"{filename}\"..."

    site = pywikibot.Site("commons", "commons")

    # Create an instance of the FilePage for the scan file
    file_page = pywikibot.FilePage(site, filename)

    # Set the file description text
    file_page.text = file_text

    # Upload the file
    if not file_page.exists():
        greater_than_3mb = is_file_size_greater_than_3mb(file_path)
        if greater_than_3mb:
            #  upload_file_chunks(file_path, filename, transcription_page_title)
            print("File size greater than 3 MB. Uploading in chunks...")
            chunk_size = convert_to_megabytes(3)
            file_page.upload(source=file_path, chunk_size=chunk_size, comment=edit_summary(summary, transcription_page_title), report_success=False)
        else:
            file_page.upload(source=file_path, comment=edit_summary(summary, transcription_page_title), report_success=False)
        print_in_green("File uploaded successfully!")
    else:
        print_in_yellow(f"File {filename} already exists on Wikimedia Commons! Not uploading.")
        process_break()

def add_country_prefix(country_name):
    irregular_countries = [
        "Bahamas",
        "Federated States of Micronesia",
        "Gambia",
        "Netherlands",
        "Philippines",
        "Seychelles",
        "Solomon Islands",
    ]

    irregular_country_prefixes = [
        "United",
        "Federated",
    ]

    for prefix in irregular_country_prefixes:
        if country_name.startswith(prefix):
            return f"the {country_name}"
    
    if country_name in irregular_countries:
        return f"the {country_name}"

    return country_name

def generate_type_category(category_namespace_prefix, work_type_name, country_name):
    work_type_name = work_type_name.capitalize() + "s"

    type_category = f"{category_namespace_prefix}{work_type_name} from {country_name}"
    type_category = linkify(type_category)

    return type_category

def generate_year_category(category_namespace_prefix, original_year, country_name):
    year_category = f"{category_namespace_prefix}{original_year} books from {country_name}"
    year_category = linkify(year_category)

    return year_category

def create_commons_category_subcategories(category_namespace_prefix, work_type_name, original_year, country_name, author_item):
    print("Generating subcategories...")
    country_name = add_country_prefix(country_name)

    author_category = linkify(get_commons_category_from_wikidata(author_item))
    type_category = generate_type_category(category_namespace_prefix, work_type_name, country_name)
    year_category = generate_year_category(category_namespace_prefix, original_year, country_name)

    categories = [author_category, type_category, year_category]

    categories.sort()

    categories = "\n".join(categories)

    return categories


def create_commons_category(title, category_namespace_prefix, author_item, work_type_name, original_year, country_name):
    category_page_title = category_namespace_prefix + title
    category_title_no_prefix = title
    print(f"Generating Commons category {category_page_title}...")

    # create subcategories
    categories = create_commons_category_subcategories(category_namespace_prefix, work_type_name, original_year, country_name, author_item)

    commons_category_text = f"{{{{Wikidata Infobox}}}}\n\n{categories}"

    print_in_green(f"Commons category text generated! Category name: {category_page_title}")
    return [category_page_title, category_title_no_prefix, commons_category_text]

"""
=={{{{int:filedesc}}}}==
{{{{Book
|source = {{{{{source_template}|{source_id}}}}}
|Wikidata = {version_item}
}}}}

=={{{{int:license-header}}}}==
{{{{PD-US-expired}}}}

[[{commons_category}]]"""


def generate_source_template(scan_source, IA_id, hathitrust_full_text_id):
    if scan_source == "ia":
        return f"{{{{Internet Archive link|{IA_id}}}}}"
    elif scan_source == "ht":
        return f"{{{{HathiTrust link|{hathitrust_full_text_id}}}}}"

def generate_scan_filename(title, year, scan_file_path):
    extension = scan_file_path.split(".")[-1]
    scan_filename = f"{title} ({year}).{extension}"
    return scan_filename

def generate_scan_file_text(version_item, scan_source, commons_category, IA_id, hathitrust_full_text_id):
    source_template = generate_source_template(scan_source, IA_id, hathitrust_full_text_id)
    copyright_template = f"{{{{PD-US-expired}}}}"

    commons_file_text = f"""=={{{{int:filedesc}}}}==
{{{{Book
|source = {source_template}
|Wikidata = {version_item}
}}}}

=={{{{int:license-header}}}}==
{copyright_template}

[[{commons_category}]]"""

    return commons_file_text


def upload_scan_file(title, year, version_item, scan_source, commons_category, IA_id, hathitrust_full_text_id, transcription_page_title):
    print("Generating scan file data...")
    scan_file_path = find_scan_file_to_upload(scan_source)
    scan_filename = generate_scan_filename(title, year, scan_file_path)
    scan_file_text = generate_scan_file_text(version_item, scan_source, commons_category, IA_id, hathitrust_full_text_id)

    # print(f"Uploading scan file to Wikimedia Commons as \"{scan_filename}\", from \"{scan_file_path}\"...")

    # upload_file_to_commons()

    upload_file_to_commons(scan_filename, scan_file_text, scan_file_path, transcription_page_title)

    return scan_filename

# def get_image_data_in_page(pattern, content):
#     images_with_pattern = re.findall(pattern, content)
#     if images_with_pattern:
#         print(f"Images with pattern {pattern} found!")
#         try:
#             image_data = images_with_pattern[0][0]
#         except IndexError:
#             image_data = images_with_pattern[0]
#         return image_data

def get_image_type_from_settings(settings):
    pattern = r"p=(.+)"
    image_data = re.findall(pattern, settings)
    if image_data:
        return image_data[0]
    else:
        return None

def determine_image_type(marker, settings):
    image_types = {
        "cov": "front cover",
        "fro": "frontispiece",
        "ti": "title illustration",
    }
    
    image_type = ""

    if settings:
        marker = get_image_type_from_settings(settings)

    # if not image_type:
    if marker in image_types:
        image_type = image_types[marker]
    else:
        image_type = "sequential"
    return image_type
        # image_type = image_types[marker]

def generate_image_title(image_type, seq_num, work_title, year):
    work_title_with_year = f"{work_title} ({year})"
    if image_type == "sequential":
        image_title = f"{work_title_with_year} {seq_num}"
    else:
        image_title = f"{work_title_with_year} {image_type}"
    return image_title

def get_image_size(image_type):
    if image_type == "title illustration":
        size = 75
    else:
        size = 300
    return size

{
    "seq_num": 0,
    # "img_num": 1,
    "page_num": 1,
    "type": "front cover",
    "title": "Master Frisky front cover",
    "caption": "",
    # "illustration": False,
    "extension": "jpg",
}

def generate_image_data(page_data, work_title, year):
    print("Checking for an existing image data json file...")
    image_data_json_file = "image_data.json"
    image_data = get_json_data(image_data_json_file)
    if image_data:
        print("Image data JSON found!")
        return image_data
    print("Generating image data from page data...")
    image_data = []
    seq_num = 0
    img_num = 0
    image_files_folder = "projectfiles/processed_files"
    for page in page_data:
        image_tag = "/img/"
        content = page["content"]
        marker = page["marker"]
        page_num = page["page_num"]
        if content != "" and image_tag in content:
            content_lines = content.split("\n")
            for line in content_lines:
                if image_tag in line:
                    image = {}
                    caption = ""
                    settings = ""
                    expected_image_tag_length = 5
                    if len(line) > expected_image_tag_length:
                        img_suffix = line[expected_image_tag_length:]
                        settings, caption = img_suffix.split("/")
                    # img_num += 1
                    image_type = determine_image_type(marker, settings)
                    if image_type == "sequential":
                        seq_num += 1
                    img_num += 1
                    image_title = generate_image_title(image_type, seq_num, work_title, year)
                    image_path, extension = get_file_path_and_extension(image_files_folder, str(img_num))
                    image_size = get_image_size(image_type)
                    # extension = "png" # for now!!!!


                    image["seq_num"] = seq_num
                    image["page_num"] = page_num
                    image["type"] = image_type
                    image["title"] = image_title
                    image["caption"] = caption
                    image["extension"] = extension
                    image["path"] = image_path
                    image["size"] = image_size
                    image["alignment"] = "center"

                    image_data.append(image)
    print_in_green("Image data generated!")
    write_to_json_file(image_data_json_file, image_data)
    return image_data






def create_creator_page(creator_page_property, author_item, author_name, transcription_page_title):
    print(f"Creating creator page for author item {author_item} ({author_name})...")
    creator_page_title = f"Creator:{author_name}"
    # creator_page = None
    creator_page_text = f"""{{{{Creator
 | Wikidata = {author_item}
 | Option   = {{{{{{1|}}}}}} <!-- Do not modify -->
}}}}"""
    site = pywikibot.Site("commons", "commons")
    creator_page = pywikibot.Page(site, creator_page_title)

    save_page(creator_page, site, creator_page_text, f"Creating creator page for {author_name} ({author_item})...", transcription_page_title)

    print_in_green("Successfully created creator page!")

    wikidata_site = pywikibot.Site("wikidata", "wikidata")

    add_property(wikidata_site, author_item, creator_page_property, author_name, 'Commons creator page', transcription_page_title)

    process_break()
    
    return creator_page_title

def get_creator_page(author_item, author, transcription_page_title):
    print(f"Retrieving creator page for author item {author_item}...")
    # if author == Anonymous etc. logic needs to be thrown in
    creator_page_property = "P1472"
    creator_page = get_value_from_property(author_item, creator_page_property)
    if not creator_page:
        print("Creator page not found! Creating one...")
        creator_page = create_creator_page(creator_page_property, author_item, author, transcription_page_title)
    else:
        creator_page = "Creator:" + creator_page
    
    return creator_page

def generate_file_description(caption, image_type, page_num, work_title, year):
    # caption = ""

    if caption:
        caption = remove_template_markup(caption)
        caption = f" Caption: \"{caption}\""
    else:
        caption = " No caption provided."
    
    if image_type == "sequential":
        file_description = f"An illustration in ''{work_title}'' ({year})"
    else:
        file_description = f"The {image_type} of ''{work_title}'' ({year})"
    
    file_description += f", found on page {page_num} of scan."
    file_description += caption

    return file_description

def generate_image_file_categories(image_type, country_name, main_commons_category):
    category_prefix = "Category:"
    categories = []
    country_name = add_country_prefix(country_name)
    if image_type == "front cover":
        categories.append(linkify(f"{category_prefix}Front cover of books"))
    elif image_type == "frontispiece":
        categories.append(linkify(f"{category_prefix}Frontispieces from {country_name}"))
    categories.append(linkify(main_commons_category)) # already has category prefix
    categories.sort()

    categories = "\n".join(categories)

    return categories

def generate_illustrator(author_item, author, transcription_page_title):
# {{Creator:Edmund Frederick}}
    creator_page = get_creator_page(author_item, author, transcription_page_title)

    if creator_page:
        return f"{{{{{creator_page}}}}}"
    else:
        return author

# {{Creator:Edmund Frederick}}

def generate_image_text(scan_filename, author_item, author, transcription_page_title, caption, image_type, page_num, work_title, year, pub_date, country_name, main_commons_category):
    print("Generating image text...")
    file_description = generate_file_description(caption, image_type, page_num, work_title, year)
    # commons_file_date = generate_commons_file_date()
    image_file_categories = generate_image_file_categories(image_type, country_name, main_commons_category)
    illustrator = generate_illustrator(author_item, author, transcription_page_title)
    copyright_template = f"{{{{PD-US-expired}}}}"

    commons_file_text = f"""=={{{{int:filedesc}}}}==
{{{{Information
|description={{{{en|1={file_description}}}}}
|date={pub_date}
|source={{{{extracted from|{scan_filename}}}}}
|author={illustrator}
}}}}


=={{{{int:license-header}}}}==
{copyright_template}

{image_file_categories}"""

    print_in_green("Image text generated!")

    return commons_file_text

def get_file_path_and_extension(path, expected_filename):
    accepted_extensions = [
        "jpg",
        "jpeg",
        "png",
        "svg",
        "pdf",
        "webm",
        "ogv",
    ]

    # image_name = "1"

    for extension in accepted_extensions:
        image_path = os.path.join(path, expected_filename + "." + extension)
        if os.path.isfile(image_path):
            return image_path, extension

def upload_images_to_commons(image_data, scan_filename, author_item, author, transcription_page_title, work_title, year, pub_date, country_name, main_commons_category):
    print("Uploading work images to Wikimedia Commons...")
    image_folder_path = "projectfiles/processed_files"
    for image_num, image in enumerate(image_data):
        image_num += 1
        
        extension = image["extension"]
        page_num = image["page_num"]
        image_file_path = image["path"]
        # image_file_path = f"{image_folder_path}/{image_num}.{extension}"
        image_filename = get_image_filename(image)
        print(f"Uploading image {image_num} to Wikimedia Commons as \"{image_filename}\", from \"{image_file_path}\"...")
        image_caption = image["caption"]
        image_type = image["type"]
        image_file_text = generate_image_text(scan_filename, author_item, author, transcription_page_title, image_caption, image_type, page_num, work_title, year, pub_date, country_name, main_commons_category)

        

        upload_file_to_commons(image_filename, image_file_text, image_file_path, transcription_page_title)
                               
                               
    print_in_green("All images uploaded.")

def get_cover_image_file(image_data):
    print("Retrieving cover image file...")
    for image in image_data:
        # image_title = image["title"]
        # image_extension = image["extension"]
        image_type = image["type"]
        if image_type == "front cover":
            cover_image = get_image_filename(image)
            print_in_green(f"Cover image file retrieved: {cover_image}")
            return cover_image
    print_in_yellow("No cover image found...")
    return None