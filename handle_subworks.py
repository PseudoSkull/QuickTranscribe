# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import page_exists, save_page, follow_redirect, remove_template_markup
from handle_wikidata import add_property, create_wikidata_item, add_description, handle_date, add_wikisource_page_to_item, add_version_to_base_work_item, handle_file
from handle_pages import get_marker_from_page_num, get_page_from_page_num
from handle_redirects import generate_variant_titles, create_redirects
from handle_disambig import add_to_disambiguation_page
from handle_commons import get_frontispiece_image
from parse_transcription import get_chapter_from_title, get_chapter_from_page_num
import pywikibot
import os
import json
import re

{
    "title": "In the Tall Grass",
    "work_item": "Qxxxxxxxxxx",
    "version_item": "Qxxxxxxxxxx",
    "image": None, # If the story has a main image in it that is NOT a vignette or drop initial image or back cover, then add its filename here
    "wikisource_link": "The Grey Story Book/In the Tall Grass",
    "work_link": "In the Tall Grass",
    "status": "proofread", # If full work is proofread/validated, then just copy its status
}

work_types = {
    "short story": "Q49084",
    "poem": "Q5185279",
    "essay": "Q35760",
}

folder_path = "projectfiles/json_data"
filename = "subwork_data.json"
file_path = os.path.join(folder_path, filename)

def get_frontispiece_linked_chapter(chapter_data, page_data, image_data):
    frontispiece_image = get_frontispiece_image(image_data)
    if not frontispiece_image:
        return None
    else:
        frontispiece_page_num = frontispiece_image["page_num"]
        frontispiece_page = get_page_from_page_num(frontispiece_page_num, page_data)
        frontispiece_page_content = get_page_from_page_num(frontispiece_page_num, page_data)
        frontispiece_chapter = get_chapter_from_page_num(chapter_data, frontispiece_page_marker)
        return frontispiece_chapter

def get_subwork_image(expected_title, page_data, chapter_data, image_data):
    return None
    unaccepted_image_types = [
        "vignette",
        "fleuron",
        "drop initial",
        "back cover",
        "front cover",
        "title illustration",
    ]

    # try and get frontispiece first
    # frontispiece_chapter = get_frontispiece_linked_chapter(chapter_data, page_data, image_data)
    # if frontispiece_chapter:
    #     frontispiece_chapter_title = frontispiece_chapter["title"]
    #     frontispiece = get_frontispiece_image(image_data)
    #     if frontispiece_chapter_title == expected_title:
    #         return frontispiece["title"] + "." + frontispiece["extension"]

    for image in image_data:
        image_type = image["type"]
        if image_type in unaccepted_image_types:
            continue
        overall_page_num = image["page_num"]
        page_num = get_marker_from_page_num(overall_page_num, page_data)
        try:
            page_num = int(page_num)
        except ValueError:
            continue
        chapter = get_chapter_from_page_num(chapter_data, page_num)
        chapter_title = chapter["title"]
        if expected_title == chapter_title:
            return image["title"] + "." + image["extension"]

def get_subwork_data(chapters, page_data, image_data, mainspace_work_title):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            subworks = json.load(file)
            file.close()
    else:
        subworks = []
        for chapter in chapters:
            title = chapter["title"]
            chapter_type = chapter["type"]
            subtitle = chapter["subtitle"]
            print(chapter)
            if chapter_type == "short story" or chapter_type == "poem" or chapter_type == "essay":
                image = get_subwork_image(title, page_data, chapters, image_data)
                status = "proofread" # for now
                wikisource_link = f"{mainspace_work_title}/{title}"
                first_line = None
                if chapter_type == "poem" or chapter_type == "po":
                    first_line = get_first_line_of_poem(title, page_data, chapters)

                subwork_data = {
                    "title": title,
                    "subtitle": subtitle,
                    "type": chapter_type,
                    "work_item": None,
                    "version_item": None,
                    "image": image,
                    "wikisource_link": wikisource_link,
                    "work_link": None,
                    "first_line": first_line,
                    "status": status,
                }

                subworks.append(subwork_data)
        
        with open(file_path, 'x') as file:
            json.dump(subworks, file, indent=4)
            file.close()
        
        if subworks:
            print(subworks)
            print_in_green("Subwork data created! Please review it.")
            exit()

    return subworks

def append_subwork_data(subwork, subworks):
    new_subworks = []

    title = subwork["title"]

    for old_subwork in subworks:
        if old_subwork["title"] == title:
            new_subworks.append(subwork)
        else:
            new_subworks.append(old_subwork)

    with open(file_path, 'w+') as file:
        json.dump(new_subworks, file, indent=4)
        file.close()
    
    return new_subworks

def get_work_type_item(work_type_name):
    return work_types[work_type_name]

def create_subwork_work_item(subwork, subworks, transcription_page_title, author_name, author, country, genre, original_pub_date, original_year, narrative_location):
    work_item = subwork["work_item"]
    work_type_name = subwork["type"]
    work_type = get_work_type_item(work_type_name)
    title = subwork["title"]
    item, repo, item_id = create_wikidata_item(work_item, title, transcription_page_title)
    subwork["work_item"] = item_id
    work_item = subwork["work_item"]
    main_image_filename = subwork["image"]
    subtitle = subwork["subtitle"]

    print(f"WORK ITEM IS {work_item} WHEN ITS CREATED")
    subworks = append_subwork_data(subwork, subworks)

    add_description(item, f'{original_year} {work_type_name} by {author_name}')

    literary_work = 'Q7725634'
    english = 'Q1860'
    image = 'P18'


    add_property(repo, item, 'P31', literary_work, 'instance of', transcription_page_title)
    if main_image_filename:
        add_property(repo, item, 'P18', handle_file(main_image_filename), 'base work main image', transcription_page_title)
    add_property(repo, item, 'P50', author, 'author', transcription_page_title)
    add_property(repo, item, 'P495', country, 'country of origin', transcription_page_title)
    add_property(repo, item, 'P7937', work_type, 'form of creative work', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(original_pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P136', genre, 'genre', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P840', narrative_location, 'narrative location (setting)', transcription_page_title)

    return subworks, work_item

def get_first_line_of_poem(poem_title, page_data, chapter_data):
    poem_punctuation = [
        ".",
        ",",
        ";",
        ":",
    ]
    for chapter in chapter_data:
        if chapter["title"] == poem_title and chapter["type"] == "poem":
            chapter_page_num = chapter["page_num"]
            print(poem_title)
            print(chapter_page_num)
            chapter_page = get_page_from_page_num(chapter_page_num, page_data)
            print(chapter_page)
            # chapter_page = page_data[12] # FOR NOW
            chapter_content = chapter_page["content"]
            print(chapter_content)
            first_line = re.search(r"\{\{ppoem\|.+?\n(.+?)\n", chapter_content).group(1)
            for punctuation in poem_punctuation:
                if first_line.endswith(punctuation):
                    first_line = first_line[:-1]
                    break

            while first_line.startswith(":"):
                first_line = first_line[1:]

            first_line = first_line.replace("{{fqm}}", "\"")
            first_line = first_line.replace("''", "")
            first_line = first_line.replace("{{\" '}}", "\"'")
            first_line = first_line.replace("{{' \"}}", "'\"")
            first_line = first_line.replace("{{fqm|", "")
            first_line = first_line.replace("}}", "")
            first_line = remove_template_markup(first_line)
            first_line = first_line.replace("\\u2014", "—")
            return first_line
    return None

def create_subwork_version_item(subwork, subworks, transcription_page_title, year, author_name, author, pub_date, collection_version_item, work_item):
    version_item = subwork["version_item"]
    title = subwork["title"]
    item, repo, item_id = create_wikidata_item(version_item, title, transcription_page_title)
    subwork["version_item"] = item_id
    version_item = subwork["version_item"]
    main_image_filename = subwork["image"]
    subtitle = subwork["subtitle"]

    subworks = append_subwork_data(subwork, subworks)

    work_type_name = subwork["type"]
    add_description(item, f'{year} edition of {work_type_name} by {author_name}')

    version_edition_or_translation = 'Q3331189'
    english = 'Q1860'
    # work_item = subwork["work_item"]
    printed_matter = 'Q1261026'
    wikisource_link = subwork["wikisource_link"]
    first_line_property = 'P1922'
    first_line = subwork["first_line"]

    add_property(repo, item, 'P31', version_edition_or_translation, 'instance of', transcription_page_title)
    if main_image_filename:
        add_property(repo, item, 'P18', handle_file(main_image_filename), 'version main image', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P50', author, 'author', transcription_page_title)
    add_property(repo, item, 'P629', work_item, 'edition of work', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    if first_line:
        add_property(repo, item, first_line_property, pywikibot.WbMonolingualText(text=first_line, language='en'), 'first line of poem', transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P1433', collection_version_item, 'published in (version item of collection)', transcription_page_title)
    add_property(repo, item, 'P437', printed_matter, 'distribution format (printed matter)', transcription_page_title)

    add_wikisource_page_to_item(item, wikisource_link)

    return subworks, version_item

def create_subwork_wikidata_items(subworks, collection_version_item, collection_work_item, collection_title, transcription_page_title, year, original_year, author_name, author, pub_date, country, genre, original_pub_date, narrative_location):
    site = pywikibot.Site("wikidata", "wikidata")
    for subwork in subworks:
        subwork_title = subwork["title"]


        print(f"Creating Wikidata items for {subwork_title}...")
        subworks, work_item = create_subwork_work_item(subwork, subworks, transcription_page_title, author_name, author, country, genre, original_pub_date, original_year, narrative_location)

        if subwork_title == collection_title:
            print("Collection title is the same as subwork title. Adding namesake property...")
            add_property(site, collection_work_item, 'P138', work_item, 'named after (collection is named after subwork contained in collection)', transcription_page_title)

        print(f"Work item is {work_item} AFTER SUBWORK ITEM IS CREATED")
        subworks, version_item = create_subwork_version_item(subwork, subworks, transcription_page_title, year, author_name, author, pub_date, collection_version_item, work_item)

        add_version_to_base_work_item(work_item, version_item)


    # get all subwork items
    subwork_version_items = [i["version_item"] for i in subworks if i["version_item"] is not None]

    add_property(site, collection_version_item, 'P527', subwork_version_items, 'has parts (subwork versions included in this version of the collection)', transcription_page_title)

    return subworks


def determine_if_disambiguation_page_exists(subwork_title, site):
    # LOGIC WILL NEED TO BE CREATED FOR IF THE PAGE YOU CAME ACROSS WAS A *WORK* OR A *VERSIONS PAGE* rather than a disambig page
    variant_titles = generate_variant_titles(subwork_title)
    redirect_titles = variant_titles + [subwork_title]
    disambiguation_template_possibilities = [
        "{{disambig}}",
        "{{dab}}",
        "{{disambiguation}}",
    ]
    for title in redirect_titles:
        if page_exists(title, site):
            title = follow_redirect(title)
            for template in disambiguation_template_possibilities:
                if template in pywikibot.Page(site, title).text.lower():
                    print_in_red(f"Uh oh! {title} already exists! Disambiguation is needed.")
                    return title
    return False

def redirect_and_disambiguate_subworks(subworks, author_surname, original_year, author_WS_name, collection_title):
    site = pywikibot.Site("en", "wikisource")
    for subwork in subworks:
        work_link = subwork["work_link"]
        wikisource_link = subwork["wikisource_link"]
        subwork_title = subwork["title"]
        if subwork_title == collection_title:
            continue # for now we're gonna do this manually
        subwork_subtitle = subwork["subtitle"]
        first_line = subwork["first_line"]
        work_type_name = subwork["type"]
        print(f"Creating redirects for {subwork_title} ({wikisource_link})")
        # disambiguation_page_title = follow_redirect(subwork_title)
        disambiguation_page_title = determine_if_disambiguation_page_exists(subwork_title, site)

        # print(variant_titles)
        if disambiguation_page_title:
            if work_link:
                print_in_yellow("This disambiguation has already been done. Skipping...")
                continue
            print_in_yellow(f"Disambiguation page exists for {subwork_title}!")
            work_link = f"{subwork_title} ({author_surname})"
            add_to_disambiguation_page(disambiguation_page_title, work_link, wikisource_link, work_type_name, original_year, work_type_name, author_WS_name, first_line)
        else:
            work_link = subwork_title

        subwork["work_link"] = work_link
        subworks = append_subwork_data(subwork, subworks)

        create_redirects(work_link, redirect_target=wikisource_link, subtitle=subwork_subtitle)

    print_in_green("All redirects and disambiguation done!")


"""
Proposed workflow:
* Create subwork_data.json, based on the above template
* Create work item and version item for each subwork, and as each is created, add the QIDs to subwork_data.json
** Create a new subwork_data.json for each new work THE INSTANT IT'S CREATED, and save file, just to ensure that the file exists
** If QID already exists for item, check that item accordingly

* (For now) Check all variants to see if their pages exist on Wikisource as disambiguation pages
** handle_disambig: If so, add to disambiguation page [["Tramp, Tramp, Tramp" (Yates)|"Tramp, Tramp, Tramp"]], a short story by [[Author:Katherine Merritte Yates|]]
** If not, create simple redirect
** Whichever is chosen for the redirect, add to subwork_data.json as "work_link"

* Create section "Individual short stories" on author page (handle_author.py)
** Rely on work_link for each entry
"""
