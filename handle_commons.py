# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break
from handle_wikidata import get_commons_category_from_wikidata
from edit_mw import linkify, edit_summary, save_page, remove_template_markup, filter_existing_pages, get_english_plural, page_exists, get_title_hierarchy
from handle_projectfiles import find_scan_file_to_upload, get_json_data, write_to_json_file, get_images_to_upload
from handle_wikidata import get_value_from_property, add_property, add_commons_category_to_item
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

def append_existing_file_text(file_text, original_file_text):
    category_prefix = "[[Category:"
    defaultsort_prefix = "{{DEFAULTSORT:"

    new_file_text_split_string = f"}}}}\n\n{category_prefix}" # PD-US-expired -> Categories
    new_file_text_split = file_text.split(new_file_text_split_string)
    new_file_text_end = category_prefix + new_file_text_split[1]
    new_file_text_end = new_file_text_end.replace("\n", "")

    if defaultsort_prefix in original_file_text and "Fæ" in original_file_text:
        original_defaultsort = re.findall(r"({{DEFAULTSORT:.+?}})", original_file_text)[0]

        original_file_text_split_string = f"}}}}\n{category_prefix}" # Defaultsort -> Categories

        original_file_text_split = original_file_text.split(original_file_text_split_string)



        original_file_text_end = category_prefix + original_file_text_split[1]
        original_file_text_end = original_file_text_end.replace("\n", "")


        print("New file text end:")
        print(new_file_text_end)
        print("Original file text end:")
        print(original_file_text_end)
        # exit()

        # categories = f"\n{category_prefix}".join(sorted(list(set(new_file_text_end.split(f"\n{category_prefix}") + original_file_text_end.split(f"\n{category_prefix}")))))
        sorted_categories = sorted(list(set(new_file_text_end.split(f"{category_prefix}") + original_file_text_end.split(f"{category_prefix}"))))

        categories = []
        
        for category in sorted_categories:
            if category != "":
                categories.append(category_prefix + category)

        categories = "\n".join(categories)
            

        print(categories)


        # print(categories)

        file_text = new_file_text_split[0] + f"}}}}\n\n{original_defaultsort}\n" + categories

    return file_text
        # file_text += "\n" + "{{DEFAULTSORT" + original_file_text_end

def upload_file_to_commons(filename, file_text, file_path, transcription_page_title):
    # filename = "Test upload with batch upload.pdf"

    print(f"Uploading file {filename} to Wikimedia Commons from {file_path}...")
    
    summary = f"Uploading \"{filename}\"..."

    site = pywikibot.Site("commons", "commons")

    # Create an instance of the FilePage for the scan file
    file_page = pywikibot.FilePage(site, filename)

    # Set the file description text

    # Upload the file
    if not file_page.exists():
        file_page.text = file_text
        greater_than_3mb = is_file_size_greater_than_3mb(file_path)
        if greater_than_3mb:
            #  upload_file_chunks(file_path, filename, transcription_page_title)
            print("File size greater than 3 MB. Uploading in chunks...")
            chunk_size = convert_to_megabytes(3)
            file_page.upload(source=file_path, chunk_size=chunk_size, comment=edit_summary(summary, transcription_page_title), report_success=False, ignore_warnings=True)
        else:
            file_page.upload(source=file_path, comment=edit_summary(summary, transcription_page_title), report_success=False, ignore_warnings=True)
        print_in_green("File uploaded successfully!")
    else:
        print_in_yellow(f"File {filename} already exists on Wikimedia Commons! Not uploading.")
        if "{{Book" in file_text: # ie if it's the scan that's being uploaded
            original_file_text = file_page.text

            file_text = append_existing_file_text(file_text, original_file_text) # CODE FOR THIS IS AN ABSOLUTE MESS! PLEASE CLEAN IT UP
            
            print(file_text)
        save_page(file_page, site, file_text, f"Updating file description for {filename}...", transcription_page_title)
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
    if work_type_name == "work":
        return None
    
    if work_type_name == "speech":
        preposition = "in"
    else:
        preposition = "from"

    work_type_name = get_english_plural(work_type_name.capitalize())

    type_category = f"{category_namespace_prefix}{work_type_name} {preposition} {country_name}"
    type_category = linkify(type_category)

    return type_category

def generate_year_category(category_namespace_prefix, original_year, country_name):
    year_category = f"{category_namespace_prefix}{original_year} books from {country_name}"
    year_category = linkify(year_category)

    return year_category

def create_author_category(author_item, author_WD_alias):
    print_in_yellow(f"No Commons category for the author {author_WD_alias} was found. Creating author category...")

    author_category_page_title = f"Category:{author_WD_alias}"
    site = pywikibot.Site("commons", "commons")
    author_category_page = pywikibot.Page(site, author_category_page_title)
    author_category_page_text = "{{Wikidata Infobox}}"

    save_page(author_category_page, site, author_category_page_text, "Creating author category...")

    add_commons_category_to_item(author_item, author_category_page_title, author_WD_alias)

    return author_category_page_title

def create_commons_category_subcategories(category_namespace_prefix, work_type_name, original_year, country_name, author_item, author_WD_alias, series_item):
    print("Generating subcategories...")
    country_name = add_country_prefix(country_name)

    author_category = get_commons_category_from_wikidata(author_item)
    if not author_category:
        author_category = create_author_category(author_item, author_WD_alias)
    author_category = linkify(author_category)
    type_category = generate_type_category(category_namespace_prefix, work_type_name, country_name)
    year_category = generate_year_category(category_namespace_prefix, original_year, country_name)
    if series_item:
        series_category = linkify(get_commons_category_from_wikidata(series_item))
    else:
        series_category = "NONEXISTENTCATEGORY"

    if type_category:
        categories = [author_category, type_category, year_category, series_category]
    else:
        categories = [author_category, year_category, series_category]

    categories.sort()
    commons_site = pywikibot.Site("commons", "commons")
    
    categories = filter_existing_pages(categories, commons_site)

    categories = "\n".join(categories)

    return categories

def generate_commons_category_title(category_namespace_prefix, title, mainspace_work_title, author_surname):
    title_hierarchy = get_title_hierarchy(mainspace_work_title)
    if title_hierarchy == "disambig":
        category_title = mainspace_work_title
    else:
        category_title = title
    commons_site = pywikibot.Site("commons", "commons")

    
    category_title_no_prefix = category_title

    category_title = category_namespace_prefix + category_title

    if page_exists(category_title, commons_site):
        # either title hierarchy is "work" or "version"
        print_in_yellow(f"Commons page for {category_title} already exists. Adding author surname to category title to disambiguate...")
        category_title += f" ({author_surname})"

    return category_title, category_title_no_prefix


def create_commons_category(title, category_namespace_prefix, author_item, work_type_name, original_year, country_name, author_WD_alias, series_item, mainspace_work_title, author_surname):
    category_page_title, category_title_no_prefix = generate_commons_category_title(category_namespace_prefix, title, mainspace_work_title, author_surname)
    print(f"Generating Commons category {category_page_title}...")

    # create subcategories
    categories = create_commons_category_subcategories(category_namespace_prefix, work_type_name, original_year, country_name, author_item, author_WD_alias, series_item)

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


def generate_source_template(scan_source, IA_id, hathitrust_full_text_id, GB_id):
    if scan_source == "ia":
        return f"{{{{Internet Archive link|{IA_id}}}}}"
    elif scan_source == "ht":
        if type(hathitrust_full_text_id) == list:
            hathitrust_full_text_id = "/".join(hathitrust_full_text_id)
        return f"{{{{HathiTrust link|{hathitrust_full_text_id}}}}}"
    elif scan_source == "gb":
        return f"{{{{Google Books link|{GB_id}}}}}"

def generate_scan_filename(title, year, scan_file_path):
    extension = scan_file_path.split(".")[-1]
    scan_filename = f"{title} ({year}).{extension}"
    return scan_filename

def generate_scan_file_text(version_item, scan_source, commons_category, IA_id, hathitrust_full_text_id, GB_id, year):
    source_template = generate_source_template(scan_source, IA_id, hathitrust_full_text_id, GB_id)
    copyright_template = generate_commons_copyright_template(year)

    commons_file_text = f"""=={{{{int:filedesc}}}}==
{{{{Book
|source = {source_template}
|Wikidata = {version_item}
}}}}

=={{{{int:license-header}}}}==
{copyright_template}

[[{commons_category}]]"""

    return commons_file_text


def upload_scan_file(title, year, version_item, scan_source, commons_category, IA_id, hathitrust_full_text_id, transcription_page_title, filename, GB_id):
    print("Generating scan file data...")
    if filename:
        scan_file_path = None
        scan_filename = filename
    else:
        scan_file_path = find_scan_file_to_upload(scan_source)
        scan_filename = generate_scan_filename(title, year, scan_file_path)

    scan_file_text = generate_scan_file_text(version_item, scan_source, commons_category, IA_id, hathitrust_full_text_id, GB_id, year)

    # print(f"Uploading scan file to Wikimedia Commons as \"{scan_filename}\", from \"{scan_file_path}\"...")

    # upload_file_to_commons()

    upload_file_to_commons(scan_filename, scan_file_text, scan_file_path, transcription_page_title)

    return scan_filename

def get_image_type_from_settings(settings):
    if type(settings) == str:
        settings = [settings,]
    for setting in settings:
        if setting.startswith("ty="):
            image_type = setting[3:]
            return image_type

def determine_image_type(marker, settings, overall_page_num):
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

    if image_type == "front cover" and overall_page_num != 0:
        image_type = "back cover"
    return image_type
        # image_type = image_types[marker]

def generate_image_title(image_type, seq_num, work_title, year, letter, vignette_num):
    work_title_with_year = f"{work_title} ({year})"
    if image_type == "sequential":
        image_title = f"{work_title_with_year} {seq_num}"
    elif image_type == "drop initial":
        image_title = f"{work_title_with_year} {image_type} letter {letter}"
    elif image_type == "vignette":
        image_title = f"{work_title_with_year} {image_type} {vignette_num}"
    else:
        image_title = f"{work_title_with_year} {image_type}"
    return image_title

def get_image_size(image_type, settings):
    if type(settings) == list:
        for setting in settings:
            if setting.startswith("s="):
                size = int(setting[2:])
    elif type(settings) == str and settings.isdigit():
        size = int(settings)
    elif image_type == "title illustration":
        size = 75
    else:
        size = 300
    return size

def get_letter_from_initial_image(line):
    drop_initial_image_pattern = r"\/dii\/(.+?)\/"

    letter = re.findall(drop_initial_image_pattern, line)[0]
    if len(letter) == 2:
        letter = letter[1]
    else:
        letter = letter[0]
    
    return letter

    # if "dii" in line:
    #     dii_tag = "/dii/"
    #     letter = line.split(dii_tag)[1][0]
    #     return letter

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

def generate_image_data(page_data, work_title, year, drop_initial_letter_data):
    print("Checking for an existing image data json file...")
    image_data_json_file = "image_data.json"
    image_data = get_json_data(image_data_json_file)
    try:
        if len(image_data) >= 0:
            print("Image data JSON found!")
            return image_data
    except TypeError:
        pass
    print("Generating image data from page data...")
    image_data = []
    seq_num = 0
    img_num = 0
    vignette_num = 0
    image_files_folder = "projectfiles/processed_files"

    for overall_page_num, page in enumerate(page_data):
        image_tag = "/img/"
        dii_tag = "/dii/"
        vign_tag = "/vign/"
        content = page["content"]
        marker = page["marker"]
        # print(f"Generating image data for page {overall_page_num}, {marker}...")
        page_num = page["page_num"]
        if content != "" and (image_tag in content or dii_tag in content or vign_tag in content):
            content_lines = content.split("\n")
            for line in content_lines:
                if image_tag in line or dii_tag in line or vign_tag in line:
                    if "/n=" in line:
                        continue
                    image = {}
                    caption = ""
                    settings = ""
                    image_type = ""
                    letter = None
                    expected_image_tag_length = 5
                    # img_num += 1
                    if dii_tag in line:
                        image_type = "drop initial"
                        letter = get_letter_from_initial_image(line)
                    else:
                        if vign_tag in line:
                            image_type = "vignette"
                            expected_image_tag_length = 6
                            vignette_num += 1
                        if len(line) > expected_image_tag_length:
                            print(line)
                            img_suffix = line[expected_image_tag_length:]
                            img_suffix_split = img_suffix.split("/")
                            settings = img_suffix_split[0]
                            caption = img_suffix_split[1]
                            if len(img_suffix_split) > 2:
                                 caption += "/" + "/".join(img_suffix_split[2:])
                                 if img_suffix.endswith("/"):
                                    caption += "/"
                            # settings, caption = "/" + "/".join(img_suffix.split("/")[:2])
                            if "," in settings:
                                settings = settings.split(",")
                        if not image_type == "vignette":
                            image_type = determine_image_type(marker, settings, overall_page_num)
                        if image_type == "sequential":
                            seq_num += 1
                        img_num += 1
                        print(img_num)
                        image_path, extension = get_file_path_and_extension(image_files_folder, str(img_num))
                    image_title = generate_image_title(image_type, seq_num, work_title, year, letter, vignette_num)
                    image_size = get_image_size(image_type, settings)
                    # extension = "png" # for now!!!!

                    if image_type == "vignette":
                        image["seq_num"] = vignette_num
                    else:
                        image["seq_num"] = seq_num
                    image["page_num"] = page_num
                    image["type"] = image_type
                    image["title"] = image_title
                    image["caption"] = caption
                    image["settings"] = settings
                    image["extension"] = extension
                    if image_type == "drop initial" and letter not in image_path:
                        image_path = f"{image_files_folder}/{letter}.{extension}"
                    image["path"] = image_path
                    image["size"] = image_size
                    image["alignment"] = "center"
                    image["letter"] = letter
                    print(image)
                    image_data.append(image)
    if drop_initial_letter_data:
        for drop_initial in drop_initial_letter_data:
            image = {}
            caption = ""
            settings = ""
            image_type = ""
            seq_num = 0
            letter = drop_initial["letter"]
            page_num = int(drop_initial["pages"][0])
            image_type = "drop initial"

            image_title = generate_image_title(image_type, seq_num, work_title, year, letter, vignette_num)
            image_path, extension = get_file_path_and_extension(image_files_folder, letter)
            image_size = 75

            image["seq_num"] = seq_num
            image["page_num"] = page_num
            image["type"] = image_type
            image["title"] = image_title
            image["caption"] = caption
            image["settings"] = settings
            image["extension"] = extension
            image["path"] = image_path
            image["size"] = image_size
            image["alignment"] = ""
            image["letter"] = letter
            image_data.append(image)
    
    print_in_green("Image data generated!")
    print(image_data)
    process_break()
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
    
    return "{{" + creator_page_title + "}}"

def get_creator_page(author_item, authors, transcription_page_title, illustrator_item, illustrators):
    # if author == Anonymous etc. logic needs to be thrown in
    creator_page_property = "P1472"
    print("illustrators")
    print(illustrators)
    print("illustrator item")
    print(illustrator_item)
    if not illustrator_item:
        # print("NO ILLUSTRATOR ITEM")
        # exit()
        illustrator_item = author_item
        illustrators = authors
    
    if type(illustrator_item) != list:
        illustrator_item = [illustrator_item,]

    if type(illustrators) != list:
        illustrators = [illustrators,]

    creator_pages = []

    for item_num, item in enumerate(illustrator_item):
        print(f"Retrieving creator page for author item {illustrator_item}...")
        illustrator = illustrators[item_num]
        creator_page = get_value_from_property(item, creator_page_property)
        if not creator_page:
            print("Creator page not found! Creating one...")
            creator_page = create_creator_page(creator_page_property, item, illustrator, transcription_page_title)
        else:
            creator_page = "{{Creator:" + creator_page + "}}"
        creator_pages.append(creator_page)
    
    creator_pages.sort()

    creator_page = "".join(creator_pages)

    return creator_page

def generate_file_description(caption, image_type, page_num, work_title, year, image_letter):
    # caption = ""

    work_title_with_year = f"''{work_title}'' ({year})"

    if caption:
        caption = remove_template_markup(caption)
        caption = f" Caption: \"{caption}\""
    else:
        caption = " No caption provided."
    
    if image_type == "sequential":
        file_description = f"An illustration in {work_title_with_year}"
    elif image_type == "drop initial":
        file_description = f"A {image_type} decoration of the letter {image_letter} in {work_title_with_year}"
    else:
        file_description = f"The {image_type} of {work_title_with_year}"
    
    file_description += f", first found on page {page_num} of scan."
    file_description += caption

    return file_description

def generate_image_file_categories(image_type, country_name, main_commons_category, image_letter):
    category_prefix = "Category:"
    categories = []
    country_name = add_country_prefix(country_name)
    if image_type == "front cover":
        categories.append(linkify(f"{category_prefix}Front cover of books"))
    if image_type == "back cover":
        categories.append(linkify(f"{category_prefix}Back covers of books"))
    elif image_type == "frontispiece":
        categories.append(linkify(f"{category_prefix}Frontispieces from {country_name}"))
    elif image_type == "drop initial":
        categories.append(linkify(f"{category_prefix}Decorative letters/{image_letter}"))
    elif image_type == "vignette":
        categories.append(linkify(f"{category_prefix}Vignette"))
    categories.append(linkify(main_commons_category)) # already has category prefix
    categories.sort()

    categories = "\n".join(categories)

    return categories

def generate_illustrator(author_item, author, transcription_page_title, illustrator_item, illustrator):
# {{Creator:Edmund Frederick}}{{Creator:Amédée de Noé}}
    creator_page = get_creator_page(author_item, author, transcription_page_title, illustrator_item, illustrator)

    if creator_page:
        return creator_page
    else:
        return author

def generate_commons_copyright_template(year):
    if year < 1928:
        return "{{PD-US-expired}}"
    else:
        return "{{PD-US-not renewed}}"

def generate_image_text(scan_filename, author_item, author, transcription_page_title, caption, image_type, page_num, work_title, year, pub_date, country_name, main_commons_category, image_letter, illustrator_item, illustrator):
    print("Generating image text...")
    file_description = generate_file_description(caption, image_type, page_num, work_title, year, image_letter)
    # commons_file_date = generate_commons_file_date()
    image_file_categories = generate_image_file_categories(image_type, country_name, main_commons_category, image_letter)
    illustrator = generate_illustrator(author_item, author, transcription_page_title, illustrator_item, illustrator)
    copyright_template = generate_commons_copyright_template(year)

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
    print("WELL WE GOT HERE SOMEHOW")

def upload_images_to_commons(image_data, scan_filename, author_item, author, transcription_page_title, work_title, year, pub_date, country_name, main_commons_category, illustrator_item, illustrator):
    print("Uploading work images to Wikimedia Commons...")
    image_folder_path = "projectfiles/processed_files"
    for image_num, image in enumerate(image_data):
        image_num += 1

        page_num = image["page_num"]
        image_file_path = image["path"]
        image_letter = image["letter"]
        image_filename = get_image_filename(image)
        print(f"Uploading image {image_num} to Wikimedia Commons as \"{image_filename}\", from \"{image_file_path}\"...")
        image_caption = image["caption"]
        image_type = image["type"]
        image_file_text = generate_image_text(scan_filename, author_item, author, transcription_page_title, image_caption, image_type, page_num, work_title, year, pub_date, country_name, main_commons_category, image_letter, illustrator_item, illustrator)

        

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