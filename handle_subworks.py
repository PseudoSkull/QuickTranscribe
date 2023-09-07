# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import page_exists, save_page
from handle_wikidata import add_property, create_wikidata_item, add_description, handle_date, add_wikisource_page_to_item, add_version_to_base_work_item
from handle_redirects import generate_variant_titles, create_redirects
from handle_disambig import add_to_disambiguation_page
import pywikibot
import os
import json

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

def get_subwork_data(chapters, mainspace_work_title):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            subworks = json.load(file)
            file.close()
    else:
        subworks = []
        for chapter in chapters:
            title = chapter["title"]
            chapter_type = chapter["type"]
            if chapter_type == "short story" or chapter_type == "poem" or chapter_type == "essay":
                image = None # for now
                status = "proofread" # for now
                wikisource_link = f"{mainspace_work_title}/{title}"

                subwork_data = {
                    "title": title,
                    "type": chapter_type,
                    "work_item": None,
                    "version_item": None,
                    "image": image,
                    "wikisource_link": wikisource_link,
                    "work_link": None,
                    "status": status,
                }

                subworks.append(subwork_data)
        
        with open(file_path, 'x') as file:
            json.dump(subworks, file, indent=4)
            file.close()

    print(subworks)

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

def create_subwork_work_item(subwork, subworks, transcription_page_title, author_name, author, country, genre, original_pub_date, original_year):
    work_item = subwork["work_item"]
    work_type_name = subwork["type"]
    work_type = get_work_type_item(work_type_name)
    title = subwork["title"]
    item, repo, item_id = create_wikidata_item(work_item, title, transcription_page_title)
    subwork["work_item"] = item_id
    work_item = subwork["work_item"]

    print(f"WORK ITEM IS {work_item} WHEN ITS CREATED")
    subworks = append_subwork_data(subwork, subworks)

    add_description(item, f'{original_year} {work_type_name} by {author_name}')

    literary_work = 'Q7725634'
    english = 'Q1860'


    add_property(repo, item, 'P31', literary_work, 'instance of', transcription_page_title)
    add_property(repo, item, 'P50', author, 'author', transcription_page_title)
    add_property(repo, item, 'P495', country, 'country of origin', transcription_page_title)
    add_property(repo, item, 'P7937', work_type, 'form of creative work', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(original_pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P136', genre, 'genre', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)

    return subworks, work_item

def create_subwork_version_item(subwork, subworks, transcription_page_title, year, author_name, author, pub_date, collection_version_item, work_item):
    version_item = subwork["version_item"]
    title = subwork["title"]
    item, repo, item_id = create_wikidata_item(version_item, title, transcription_page_title)
    subwork["version_item"] = item_id
    version_item = subwork["version_item"]

    subworks = append_subwork_data(subwork, subworks)

    add_description(item, f'{year} edition of work by {author_name}')

    version_edition_or_translation = 'Q3331189'
    english = 'Q1860'
    # work_item = subwork["work_item"]
    wikisource_link = subwork["wikisource_link"]

    add_property(repo, item, 'P31', version_edition_or_translation, 'instance of', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P50', author, 'author', transcription_page_title)
    add_property(repo, item, 'P629', work_item, 'edition of work', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P1433', collection_version_item, 'published in (version item of collection)', transcription_page_title)

    add_wikisource_page_to_item(item, wikisource_link)

    return subworks, version_item

def create_subwork_wikidata_items(subworks, collection_version_item, transcription_page_title, year, original_year, author_name, author, pub_date, country, genre, original_pub_date):
    site = pywikibot.Site("wikidata", "wikidata")
    for subwork in subworks:
        subwork_title = subwork["title"]
        print(f"Creating Wikidata items for {subwork_title}...")
        subworks, work_item = create_subwork_work_item(subwork, subworks, transcription_page_title, author_name, author, country, genre, original_pub_date, original_year)
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
    for title in redirect_titles:
        if page_exists(title, site):
            print_in_red(f"Uh oh! {title} already exists! Disambiguation is needed.")
            return title
    return False

def redirect_and_disambiguate_subworks(subworks, author_surname, original_year, author_WS_name):
    site = pywikibot.Site("en", "wikisource")
    for subwork in subworks:
        work_link = subwork["work_link"]
        wikisource_link = subwork["wikisource_link"]
        subwork_title = subwork["title"]
        work_type_name = subwork["type"]
        print(f"Creating redirects for {subwork_title} ({wikisource_link})")
        disambiguation_page_title = determine_if_disambiguation_page_exists(subwork_title, site)

        # print(variant_titles)
        if disambiguation_page_title:
            if work_link:
                print_in_yellow("This disambiguation has already been done. Skipping...")
                continue
            print_in_yellow(f"Disambiguation page exists for {subwork_title}!")
            work_link = f"{subwork_title} ({author_surname})"
            add_to_disambiguation_page(disambiguation_page_title, work_link, wikisource_link, work_type_name, original_year, work_type_name, author_WS_name)
        else:
            work_link = subwork_title

        subwork["work_link"] = work_link
        subworks = append_subwork_data(subwork, subworks)

        create_redirects(work_link, redirect_target=wikisource_link)

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
