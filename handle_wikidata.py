# WS_collection

import pywikibot
from dateutil import parser as date_parser
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import edit_summary
from pywikibot.page import ItemPage
from pywikibot import WbTime, SiteLink
from hathi import get_hathitrust_id_from_commons_page, get_hathitrust_catalog_id
from handle_wikisource_conf import update_conf_value
from edit_mw import save_page
import re
    
def handle_date(pub_date_unparsed):
    print("Parsing date...")
    pub_date_length = len(pub_date_unparsed)
    pub_date = date_parser.parse(pub_date_unparsed, default=None)
    year = pub_date.year
    # month_match = re.search(r"[A-Za-z]", pub_date_unparsed)
    if pub_date_length >= 7:
        month = pub_date.month
    else:
        month = None
    # day_match = re.search(r"\b(0?[1-9]|[12][0-9]|3[01])\b", pub_date_unparsed)
    if pub_date_length >= 10:
        day = pub_date.day
    else:
        day = None
    print_in_green(f"Date processed. Unparsed: {pub_date_unparsed} Parsed: Year: {year} Month: {month} Day: {day}")

    if not month:
        return pywikibot.WbTime(year=year)
    elif not day:
        return pywikibot.WbTime(year=year, month=month)
    else:
        return pywikibot.WbTime(year=year, month=month, day=day)

def handle_file(filename):
    return pywikibot.FilePage(pywikibot.Site('commons', 'commons'), title=filename)

def item_page(repo, value):
    if type(value) == ItemPage:
        return value
    else:
        return pywikibot.ItemPage(repo, value)

def is_wikidata_item_string(value):
    if type(value) != str:
        return False
    else:
        wikidata_item_prefix = "Q"
        wikidata_item_suffix = value[1:]
        if type(value) == str and value.startswith(wikidata_item_prefix) and wikidata_item_suffix:
            return True
        return False

def add_property(repo, item, property, values, descriptor, transcription_page_title=None):
    print(f"Adding {descriptor} claim to item {item}...")

    if not item:
        print_in_yellow(f"No item found for {descriptor}. No action taken.")
        return

    if type(item) == str:
        item = item_page(repo, item)

    if type(values) != list:
        values = [values,]

    for value in values:
        existing_claims = item.claims.get(property)
        claim = pywikibot.Claim(repo, property)

        if not value or str(value) == "[[wikidata:-1]]":
            print_in_yellow(f"Value not found for {descriptor}. No action taken.")
            continue

        if is_wikidata_item_string(item):
            item = pywikibot.ItemPage(repo, item)

        if is_wikidata_item_string(value):
            value = pywikibot.ItemPage(repo, value)

        # Check if the property with the same value already exists
        if existing_claims:
            to_continue = False
            for existing_claim in existing_claims:
                if existing_claim.target_equals(value):
                    print_in_yellow(f"{descriptor} claim already exists with the same value. No action taken.")
                    to_continue = True
                    break
            if to_continue:
                continue

        claim.setTarget(value)

        if transcription_page_title:
            property_edit_summary = edit_summary(f'Adding {descriptor} claim...', transcription_page_title)
        else:
            property_edit_summary = edit_summary(f'Adding {descriptor} claim...')

        item.addClaim(claim, summary=property_edit_summary)
        print_in_green(f"{descriptor} claim added successfully.")


def get_value_from_property(item, property):
    print(f"Retrieving value {property} for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")

    # All of this is to handle properties being searched for from multiple values
    if type(item) == str or type(item) == ItemPage:
        items = [item,]
    else:
        items = item


    results = []
    for item in items:
        page = item_page(site, item)  # Create an ItemPage for the variable

        # Retrieve the author item (P50) from the base_work item
        page.get()
        claim = page.claims.get(property)
        try:
            result = claim[0].target.id
        except AttributeError:
            try:
                result = claim[0].target.toTimestr()
            except AttributeError:
                result = claim[0].target
        except TypeError:
            result = None
        if result:
            print_in_green(f"Value retrieved for {property} in {item}: {result}.")
            results.append(result)
        else:
            print_in_red(f"Value not found for {property} in {item}.")
            return None
    
    if len(results) == 1:
        return results[0]
    else:
        if len(set(results)) == 1:
            return results[0]
        else:
            print_in_yellow(f"Different values retrieved from the separate items: Items: {items} Results: {results}.")
            return results

def get_time_from_property(item, property):
    print(f"Retrieving value {property} for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")
    page = item_page(site, item)  # Create an ItemPage for the variable

    # Retrieve the author item (P50) from the base_work item
    page.get()
    claim = page.claims.get(property)
    
    result = claim[0].target.id
    if result:
        print_in_green(f"Value retrieved for {property} in {item}: {result}.")
        return result
    else:
        print_in_red(f"Value not found for {property} in {item}.")
        return None

def get_label(items):
    print(f"Retrieving (existing) label for Wikidata item {items}.")
    site = pywikibot.Site("wikidata", "wikidata")

    if type(items) != list:
        items = [items,]
    
    labels = []
    for item in items:
        page = item_page(site, item)

        # Retrieve the label of the author item in English
        page.get()
        label = page.labels.get("en")

        if label:
            print_in_green(f"Label retrieved for {item}: {label}.")
            labels.append(label)
        else:
            print_in_yellow(f"Label not found for {item}.")
            return None
    
    if len(labels) == 1:
        return labels[0]
    else:
        return labels

def get_description(item):
    print(f"Retrieving (existing) description for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")
    page = item_page(site, item)  # Create an ItemPage for the author

    # Retrieve the label of the author item in English
    page.get()
    description = page.descriptions.get("en")

    if description:
        print_in_green(f"Description retrieved for {item}: {description}.")
        return description
    else:
        print_in_yellow(f"Description not found for {item}.")
        return None

def add_description(item, description):
    print(f"Adding description \"{description}\" to {item}...")
    
    # Check if the label already exists
    existing_label = get_description(item)
    if existing_label == description:
        print_in_yellow("Description already exists. No action taken.")
        return
    item.editDescriptions(descriptions={'en': description})
    print_in_green("Description added successfully.")

def add_label(item, label):
    print(f"Adding label \"{label}\" to {item}...")
    
    # Check if the label already exists
    #################################### THE BELOW CODE SHOULD WORK, but it doesn't on nonexistent items because the item is not yet created without the label being there
    item_id = extract_id_from_item_page(item)
    if item_id != "-1":
        # print_in_yellow("Item does not exist. No action taken.")
        # return
        existing_label = get_label(item)
        if existing_label == label:
            print_in_yellow("Label already exists. No action taken.")
            return
    item.editLabels(labels={'en': label})
    print_in_green("Label added successfully.")

def extract_wikisource_page_title(link):
    namespaces = [
        "Author",
        "Portal",
        "Index",
        "Page",
        "Template",
        "Category",
        "Wikisource",
    ]
    if link.startswith("[[") and link.endswith("]]"):
        link = link[2:-2]  # Remove the double square brackets
        
        for namespace in namespaces:
            if link.startswith(namespace + ":"):
                page_title = link[len(namespace) + 1:].strip()  # Remove namespace and colon
                return page_title
    
    return link


def get_wikisource_page_from_wikidata(item):
    print(f"Retrieving (existing) Wikisource page for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")
    page = item_page(site, item)  # Create an ItemPage for the author

    # Retrieve the label of the author item in English
    page.get()
    sitelink = str(page.sitelinks.get("enwikisource"))

    if sitelink:
        link = extract_wikisource_page_title(sitelink)
        print_in_green(f"Wikisource page retrieved for {item}: {link}. Parsing...")
        return link
    else:
        print_in_yellow(f"Wikisource page not found for {item}.")
        return None

def get_commons_category_from_wikidata(item):
    print(f"Retrieving (existing) Commons category for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")
    page = item_page(site, item)  # Create an ItemPage for the author

    commons_category_property = "P373"
    commons_category_title = get_value_from_property(item, commons_category_property)
    if not commons_category_title:
        print_in_red(f"Commons category for {item} not found!")
        return None
    commons_category = "Category:" + commons_category_title

    return commons_category

def add_index_page_to_version_item(version_item, index_page_title):
    print(f"Adding index page \"{index_page_title}\" to {version_item}...")
    
    site = pywikibot.Site("wikidata", "wikidata")
    item = item_page(site, version_item)

    index_page_title_for_URL = index_page_title.replace(" ", "_")
    URL_prefix = "https://en.wikisource.org/wiki/"
    index_page_URL = URL_prefix + index_page_title_for_URL

    add_property(site, item, 'P1957', index_page_URL, 'Wikisource index page URL')

def get_author_death_year(author_item):
    print(f"Retrieving (existing) death year for Wikidata item {author_item}.")
    site = pywikibot.Site("wikidata", "wikidata")
    page = item_page(site, author_item)  # Create an ItemPage for the author

    author_death_date = get_value_from_property(page, 'P570')

    if author_death_date:
        # Extract the year from the specific part of the date string. Example: +00000001961-07-12T00:00:00Z
        author_death_year = author_death_date[8:][:4]
        print_in_green(f"Death year retrieved for {author_item}: {author_death_year}.")
    else:
        print_in_yellow(f"Death year not found for {author_item}.")
        author_death_year = None
    return author_death_year


def add_wikisource_page_to_item(item, wikisource_page_title):
    site = pywikibot.Site("wikidata", "wikidata")

    # # Retrieve the Wikidata item
    item = item_page(site, item)

    proofread_badge = ['Q20748092',]

    transcription_data = SiteLink(
        title=wikisource_page_title,
        site='enwikisource',
        badges=proofread_badge,
    )
    
    item.setSitelink(sitelink=transcription_data, summary=edit_summary('Adding enwikisource sitelink...'))
    print_in_green(f"Added enwikisource sitelink to {item}.")

def add_commons_category_to_item(item, commons_category, commons_category_title):
    print(f"Adding Commons category {commons_category} to Wikidata item {item}...")
    site = pywikibot.Site("wikidata", "wikidata")

    # # Retrieve the Wikidata item
    item = item_page(site, item)
    commons_category_property = "P373"
    add_property(site, item, commons_category_property, commons_category_title, 'Commons category')
    item.setSitelink(sitelink={'site': 'commonswiki', 'title': commons_category}, summary=edit_summary('Adding commons sitelink...'))
    print_in_green(f"Added commons sitelink to {item}.")


def extract_id_from_item_page(item_page):
    # Get the full URL of the item page
    item_url = item_page.full_url()

    # Extract the item ID from the URL
    item_id = item_url.split("/")[-1]
    
    return item_id

def create_wikidata_item(existing_item, title, transcription_page_title=None, variable_name=None):
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()

    if existing_item:
        print("Item already exists. Modifying item...")
        item = pywikibot.ItemPage(repo, existing_item)
    else:
        print("Creating new Wikidata item...")
        item = pywikibot.ItemPage(repo)
        print(item)

    add_label(item, title)


    if variable_name:
        item.get()
        item_id = extract_id_from_item_page(item)
        wikisource_site = pywikibot.Site('en', 'wikisource')
        transcription_page = pywikibot.Page(wikisource_site, transcription_page_title)
        transcription_text = transcription_page.text
        transcription_text = update_conf_value(transcription_text, variable_name, item_id)
        save_page(transcription_page, site, transcription_text, f"Noting that the Wikidata item for {variable_name} has been created...")
        return [item, repo, item_id]

    item_id = existing_item

    return [item, repo, item_id]

# Hey, looking forward to meeting you tomorrow! :D Let me know if anything comes up.
    


def create_base_work_item(base_work_item, title, work_type, work_type_name, genre, author, author_name, original_pub_date, original_year, country, transcription_page_title, subtitle, variable_name=None):
    item, repo, item_id = create_wikidata_item(base_work_item, title, transcription_page_title, variable_name)

    add_description(item, f'{original_year} {work_type_name} by {author_name}')

    literary_work = 'Q7725634'
    english = 'Q1860'

    add_property(repo, item, 'P31', literary_work, 'instance of', transcription_page_title)
    add_property(repo, item, 'P50', author, 'author', transcription_page_title)
    add_property(repo, item, 'P495', country, 'country of origin', transcription_page_title)
    add_property(repo, item, 'P7937', work_type, 'form of creative work', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(original_pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P136', genre, 'genre', transcription_page_title)
    # UNLESS IT'S A TRANSLATION, IN WHICH CASE WE NEED TO ADD THE ORIGINAL LANGUAGE, add this functionality later
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    
    return item_id

# def fill_base_work_item():



def create_version_item(title, version_item, pub_date, year, author_item, author_name, base_work, publisher, location, filename, hathitrust_id, IA_id, transcription_page_title, GB_id, subtitle, illustrator_item, variable_name=None):
    item, repo, item_id = create_wikidata_item(version_item, title, transcription_page_title, variable_name)
    add_description(item, f'{year} edition of work by {author_name}')

    # item names for readability
    version_edition_or_translation = 'Q3331189'
    english = 'Q1860'

    add_property(repo, item, 'P31', version_edition_or_translation, 'instance of', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P50', author_item, 'author', transcription_page_title)
    add_property(repo, item, 'P110', illustrator_item, 'illustrator', transcription_page_title)
    add_property(repo, item, 'P629', base_work, 'edition of work', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P123', publisher, 'publisher', transcription_page_title)
    add_property(repo, item, 'P291', location, 'location', transcription_page_title)
    
    add_property(repo, item, 'P1844', hathitrust_id, 'HathiTrust ID', transcription_page_title)
    add_property(repo, item, 'P724', IA_id, 'Internet Archive ID', transcription_page_title)
    add_property(repo, item, 'P675', GB_id, 'Google Books ID', transcription_page_title)

    if filename:
        add_scan_file_to_version_item(repo, item, filename, transcription_page_title)

        if not hathitrust_id: # if no hathitrust_id was found...
            # if there is a Hathi ID listed on the commons page for the file, add it to the item
            hathitrust_id = get_hathitrust_id_from_commons_page(filename) # try and get it from commons
            if hathitrust_id: # if it was found on commons...
                catalog_id = get_hathitrust_catalog_id(hathitrust_id)
                if catalog_id:
                    add_property(repo, item, 'P1844', catalog_id, f'HathiTrust ID (retrieved from Commons file page for {filename})', transcription_page_title)
    
    return item_id

    

    # item.get()
    # print(item.title())
    # return item.title()

def add_version_to_base_work_item(base_work, version_item):
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()

    base_work_item = pywikibot.ItemPage(repo, base_work)
    base_work_item.get()

    add_property(repo, base_work_item, 'P747', version_item, 'has edition or translation')

# add_to_works_item(base_work, version_item)

def get_wikidata_item_from_wikisource(page_title):
    print(f"Getting Wikidata item of Wikisource page \"{page_title}\"...")

    if not page_title:
        return None
    
    if type(page_title) != list:
        page_title = [page_title,]
    
    site = pywikibot.Site("en", "wikisource")

    page_titles = []
    for title in page_title:
        page = pywikibot.Page(site, title)
        item = page.data_item().title()
        page_titles.append(item)
    
    if len(page_titles) == 1:
        item = page_titles[0]
    else:
        item = page_titles

    print_in_green(f"Got Wikidata item of \"{page_title}\": \"{item}\"")
    return item

def get_country_name(country):
    country_name = get_label(country)
    if country_name == 'United States of America':
        country_name = 'United States'
    return country_name

def add_scan_file_to_version_item(repo, item, filename, transcription_page_title):
    add_property(repo, item, 'P996', handle_file(filename), 'filename', transcription_page_title)








def check_for_image_type(image_data, intended_image_type):
    for image in image_data:
        image_type = image['type']
        if image_type == intended_image_type:
            return image
    return None

def get_main_image(image_data):
    front_cover_image = check_for_image_type(image_data, 'front cover')
    if front_cover_image:
        return front_cover_image
    
    frontispiece_image = check_for_image_type(image_data, 'frontispiece')
    if frontispiece_image:
        return frontispiece_image
    
    title_illustration_image = check_for_image_type(image_data, 'title illustration')
    if title_illustration_image:
        return title_illustration_image
    
    return None


def add_main_image_to_wikidata_items(base_work, version_item, image_data, transcription_page_title):
    print("Adding main image to Wikidata items...")
    site = pywikibot.Site('wikidata', 'wikidata')


    main_image = get_main_image(image_data)
    if not main_image:
        print_in_yellow("No main image found. Skipping step...")
        return
    
    main_image_title = main_image['title']
    main_image_extension = main_image['extension']
    main_image_filename = f"{main_image_title}.{main_image_extension}"

    image_property = 'P18'

    # base_work_item = pywikibot.ItemPage(site, base_work)

    print_in_green(f"Adding image to base work item: {main_image_filename}")

    add_property(site, base_work, image_property, handle_file(main_image_filename), 'base work main image', transcription_page_title)
    
    version_image = get_value_from_property(version_item, image_property)

    if version_image:
        print_in_yellow(f"Version item already has image: {version_image}. Skipping this item...")
        return
    else:
        print_in_green(f"Adding image to version item: {main_image_filename}")
        add_property(site, version_item, image_property, handle_file(main_image_filename), 'version main image', transcription_page_title)