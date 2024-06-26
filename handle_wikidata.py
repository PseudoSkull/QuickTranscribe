# WS_collection

import pywikibot
from dateutil import parser as date_parser
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import edit_summary
from pywikibot.page import ItemPage
from pywikibot import WbTime, SiteLink
from hathi import get_hathitrust_id_from_commons_page, get_hathitrust_catalog_id, get_oclc_from_hathi, get_ark_identifier_from_hathi
from handle_projectfiles import get_data_from_xml
from handle_gutenberg import get_date_from_gutenberg
from handle_wikisource_conf import update_conf_value
from edit_mw import save_page
from api_keys import google_books_api_key
import requests
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
        if type(value) == str and value.startswith(wikidata_item_prefix) and wikidata_item_suffix and " " not in value:
            return True
        return False

def add_property(repo, item, property, values, descriptor, transcription_page_title=None):
    print(f"Adding {descriptor} claim to item {item}...")

    if not item and descriptor != "author":
        print_in_yellow(f"No item found for {descriptor}. No action taken.")
        return

    if type(item) == str:
        item = item_page(repo, item)

    if type(values) != list:
        values = [values,]

    if not values and descriptor == "Author":
        existing_claims = item.claims.get(property)
        claim = pywikibot.Claim(repo, property)

        # claim.setSnakType('somevalue')
        claim.setTarget('somevalue')
        property_edit_summary = edit_summary(f'Adding anonymous author claim...', transcription_page_title)

        item.addClaim(claim, summary=property_edit_summary)
        print_in_green(f"{descriptor} claim added successfully.")

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


def get_value_from_property(item, property, get_last_item=False):
    print(f"Retrieving value {property} for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")

    # All of this is to handle properties being searched for from multiple values
    if type(item) == str or type(item) == ItemPage:
        items = [item,]
    else:
        items = item

    # filtered_items = []

    # united_states = False
    # for item in items:
    #     if item_page(site, item) == item_page(site, "Q2079909"):
    #         print("Found Q2079909")
    #         united_states = True
    #         continue
    #     filtered_items.append(item)

    # if united_states:
    #     filtered_items.append(item_page("Q30"))

    # items = filtered_items
        
    results = []
    for item in items:
        page = item_page(site, item)  # Create an ItemPage for the variable

        # Retrieve the author item (P50) from the base_work item
        page.get()
        claim = page.claims.get(property)
        # print(claim)
        # exit()
        # if get_last_item: # This is for when you want to get the last item in a list of items
        #     return item_page(site, claim)
        
        try:
            result = claim[0].target.id
            if get_last_item:
                result = claim[-1].target.id
                if result == "Q2079909":
                    result = "Q30"
                return result
        except AttributeError:
            try:
                result = claim[0].target.toTimestr()
            except AttributeError:
                result = claim[0].target
                if get_last_item:
                    result = claim[-1].target
                    return result
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

def get_alias(item):
    print(f"Retrieving (existing) alias for Wikidata item {item}.")
    site = pywikibot.Site("wikidata", "wikidata")
    page = item_page(site, item)  # Create an ItemPage for the author

    # Retrieve the label of the author item in English
    page.get()
    alias = page.aliases.get("en")

    if alias:
        print_in_green(f"Alias retrieved for {item}: {alias}.")
        return alias
    else:
        print_in_yellow(f"Alias not found for {item}.")
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

def add_alias(item, alternative_title):
    if alternative_title:
        print(f"Adding alias \"{alternative_title}\" to {item}...")
        
        # Check if the label already exists
        existing_alias = get_alias(item)
        if existing_alias == alternative_title:
            print_in_yellow("Alias already exists. No action taken.")
            return
        item.editAliases(aliases={'en': [alternative_title]})
        print_in_green("Alias added successfully.")
    else:
        print_in_yellow("No alternative title found. No action taken.")

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
    index_page_title_for_URL = index_page_title_for_URL.replace("\"", "%22")
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
        author_death_year = int(author_death_date[8:][:4])
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

    if not existing_item:
        item.get()
        item_id = extract_id_from_item_page(item)
    else:
        item_id = existing_item

    return [item, repo, item_id]

# Hey, looking forward to meeting you tomorrow! :D Let me know if anything comes up.
    


def create_base_work_item(base_work_item, title, work_type, work_type_name, genre, author, author_name, original_pub_date, original_year, country, transcription_page_title, alternative_title, subtitle, related_author_item, series, narrative_location, openlibrary_work_id, previous_item, derivative_work, variable_name=None):
    item, repo, item_id = create_wikidata_item(base_work_item, title, transcription_page_title, variable_name)

    if author_name == "Anonymous":
        author_display = "written anonymously"
    else:
        author_display = f"by {author_name}"
    
    add_description(item, f'{original_year} {work_type_name} {author_display}')
    add_alias(item, alternative_title)

    literary_work = 'Q7725634'
    english = 'Q1860'

    add_property(repo, item, 'P31', literary_work, 'instance of', transcription_page_title)
    add_property(repo, item, 'P50', author, 'author', transcription_page_title)
    add_property(repo, item, 'P495', country, 'country of origin', transcription_page_title)
    add_property(repo, item, 'P7937', work_type, 'form of creative work', transcription_page_title)
    add_title_to_item(repo, item, title, alternative_title, transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    handle_series(repo, item, series, transcription_page_title)
    handle_sequence(repo, item, previous_item, transcription_page_title)
    add_property(repo, item, 'P921', related_author_item, 'main subject (related author)', transcription_page_title)
    add_property(repo, item, 'P4969', derivative_work, 'derivative work (film based on the book)', transcription_page_title)
    if "collection" not in work_type_name:
        add_property(repo, item, 'P840', narrative_location, 'narrative location (setting)', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(original_pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P136', genre, 'genre', transcription_page_title)
    # UNLESS IT'S A TRANSLATION, IN WHICH CASE WE NEED TO ADD THE ORIGINAL LANGUAGE, add this functionality later
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P648', openlibrary_work_id, 'OpenLibrary work ID', transcription_page_title)
    derivative_work


    
    return item_id

# def fill_base_work_item():

def get_gutenberg_id_from_ia(gutenberg_ia_id):
    gutenberg_id = re.search(r'0(\d+)', gutenberg_ia_id).group(1)
    return gutenberg_id

def create_gutenberg_version_item(gutenberg_id, gutenberg_ia_id, gutenberg_version_item, title, subtitle, version_item, author_item, translator_item, base_work, transcription_page_title, variable_name=None):
    item, repo, item_id = create_wikidata_item(gutenberg_version_item, title, transcription_page_title, variable_name)
    if not gutenberg_id:
        gutenberg_id = get_gutenberg_id_from_ia(gutenberg_ia_id)
    
    gutenberg_year, gutenberg_date = get_date_from_gutenberg(gutenberg_id)
    add_description(item, f'{gutenberg_year} Gutenberg edition of work')
    
    version_edition_or_translation = 'Q3331189'
    english = 'Q1860'
    digital_edition = 'Q1224889'
    project_gutenberg = 'Q22673'

    add_property(repo, item, 'P31', version_edition_or_translation, 'instance of', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P437', digital_edition, 'distribution format (digital edition)', transcription_page_title)
    add_property(repo, item, 'P123', project_gutenberg, 'publisher (Project Gutenberg)', transcription_page_title)

    add_property(repo, item, 'P629', base_work, 'edition of work', transcription_page_title)
    add_property(repo, item, 'P50', author_item, 'author', transcription_page_title)
    add_property(repo, item, 'P655', translator_item, 'translator', transcription_page_title)
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(gutenberg_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P2034', gutenberg_id, 'Gutenberg ebook ID', transcription_page_title)
    add_property(repo, item, 'P724', gutenberg_ia_id, 'Gutenberg Internet Archive ID', transcription_page_title)

    
    return item_id



def add_title_to_item(repo, item, title, alternative_title, transcription_page_title):
    add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=title, language='en'), 'title', transcription_page_title)
    if alternative_title:
        add_property(repo, item, 'P1476', pywikibot.WbMonolingualText(text=alternative_title, language='en'), 'title', transcription_page_title)

def create_version_item(title, version_item, pub_date, year, author_item, author_name, base_work, publisher, location, filename, hathitrust_id, IA_id, transcription_page_title, GB_id, alternative_title, subtitle, illustrator_item, editor_item, translator_item, dedications, lccn, ark_identifier, oclc, edition_number, openlibrary_version_id, loc_classification, variable_name=None):
    item, repo, item_id = create_wikidata_item(version_item, title, transcription_page_title, variable_name)

    if author_name == "Anonymous":
        author_display = " written anonymously"
    else:
        author_display = f""
    
    add_description(item, f'{year} edition of work{author_display}')
    add_alias(item, alternative_title)

    # item names for readability
    version_edition_or_translation = 'Q3331189'
    english = 'Q1860'
    printed_matter = 'Q1261026'

    add_property(repo, item, 'P31', version_edition_or_translation, 'instance of', transcription_page_title)
    add_property(repo, item, 'P407', english, 'language', transcription_page_title)
    add_property(repo, item, 'P437', printed_matter, 'distribution format (printed matter)', transcription_page_title)
    add_property(repo, item, 'P50', author_item, 'author', transcription_page_title)
    add_property(repo, item, 'P110', illustrator_item, 'illustrator', transcription_page_title)
    add_property(repo, item, 'P655', translator_item, 'translator', transcription_page_title)
    add_property(repo, item, 'P98', editor_item, 'editor', transcription_page_title)
    add_property(repo, item, 'P629', base_work, 'edition of work', transcription_page_title)
    add_property(repo, item, 'P393', edition_number, 'edition number', transcription_page_title)
    add_title_to_item(repo, item, title, alternative_title, transcription_page_title)
    if subtitle:
        add_property(repo, item, 'P1680', pywikibot.WbMonolingualText(text=subtitle, language='en'), 'subtitle', transcription_page_title)
    add_property(repo, item, 'P577', handle_date(pub_date), 'publication date', transcription_page_title)
    add_property(repo, item, 'P123', publisher, 'publisher', transcription_page_title)
    add_property(repo, item, 'P291', location, 'location', transcription_page_title)
    add_property(repo, item, 'P825', dedications, 'dedications', transcription_page_title)
    
    add_property(repo, item, 'P1844', hathitrust_id, 'HathiTrust ID', transcription_page_title)
    add_property(repo, item, 'P724', IA_id, 'Internet Archive ID', transcription_page_title)
    add_property(repo, item, 'P675', GB_id, 'Google Books ID', transcription_page_title)
    add_property(repo, item, 'P1144', lccn, 'LCCN (Library of Congress Catalog Number) ID', transcription_page_title)
    add_property(repo, item, 'P243', oclc, 'OCLC (WorldCat) ID', transcription_page_title)
    add_property(repo, item, 'P8091', ark_identifier, 'ARK ID', transcription_page_title)
    add_property(repo, item, 'P648', openlibrary_version_id, 'OpenLibrary version ID', transcription_page_title)
    add_property(repo, item, 'P8360', loc_classification, 'Library of Congress Classification (call number)', transcription_page_title)

    if filename:
        add_scan_file_to_version_item(repo, item, filename, transcription_page_title)

        if not hathitrust_id: # if no hathitrust_id was found...
            # if there is a Hathi ID listed on the commons page for the file, add it to the item
            # hathitrust_id = get_hathitrust_id_from_commons_page(filename) # try and get it from commons
            # if hathitrust_id: # if it was found on commons...
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

def get_wikidata_item_from_page(page):
    return page.data_item().title()

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


def get_surname_from_author(author_item):
    print("Getting surname from author...")
    surname_property = "P734"
    author_surname_item = get_value_from_property(author_item, surname_property)

    if author_surname_item:
        author_surname = get_label(author_surname_item)
        print_in_green(f"Surname retrieved successfully from author! {author_surname}")
        return author_surname
    # else:
    author_label = get_label(author_item)
    author_surname = author_label.split(' ')[-1]
    print_in_yellow(f"Couldn't get surname from author using property. Using label instead: {author_surname}")
    return author_surname

def get_oclc_from_gb(gb_id):
    url = f"https://books.google.com/books?id={gb_id}"
    print("Attempting to get the OCLC link from:", url)
    response = requests.get(url)

    if response.status_code == 200:
        print_in_green("Response code 200. Parsing the HTML...")
        page_content = str(response.content)
        
        if "/oclc/" in page_content:
            oclc = re.findall(r'\/oclc\/([0-9]+?)&amp', page_content)[0]
            print_in_green(f"Success. OCLC: {oclc}")
            return oclc
        print_in_red("OCLC link not found.")
        return None

    print_in_red(f"Response code not 200. Was: {response.status_code}")
    return None

def get_google_books_id_from_oclc(oclc):
    import requests

def get_book_id_by_oclc(oclc):
    print("Attempting to retrieve the Google Books ID from the OCLC number...")
    # Construct the URL for the Google Books API
    if not oclc:
        print_in_yellow("No OCLC found.")
        return
    
    url = f"https://www.googleapis.com/books/v1/volumes?q=oclc:{oclc}&key={google_books_api_key}"

    # Make the request to the Google Books API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        
        # Check if any items were found
        if items:
            # Return the ID of the first book found
            books_id = items[0]['id']
            print_in_green(f"Success. Google Books ID: {books_id}")
            return books_id
        else:
            print_in_yellow("No books found with that OCLC number.")
    else:
        print_in_yellow(f"Error: {response.status_code}")


def get_oclc(hathitrust_id, gb_id):
    if hathitrust_id and hathitrust_id != "None":
        return get_oclc_from_hathi(hathitrust_id)
    else:
        oclc = get_data_from_xml("oclc-id")
        if oclc:
            return oclc
        else:
            external_identifier = get_data_from_xml("external-identifier")
            if external_identifier:
                # example: urn:oclc:record:1102109269
                # get everything after the last colon
                oclc = external_identifier.split(":")[-1]
                return oclc
    if gb_id:
        return get_oclc_from_gb(gb_id)

def get_ark_identifier(hathitrust_full_text_id):
    ark_identifier = None
    if hathitrust_full_text_id:
        ark_identifier = get_ark_identifier_from_hathi(hathitrust_full_text_id)
    if not ark_identifier:
        ark_identifier = get_data_from_xml("ark-identifier")
        if not ark_identifier:
            ark_identifier = get_data_from_xml("identifier-ark")
    return ark_identifier

def get_openlibrary_id():
    openlibrary_version_id = get_data_from_xml("openlibrary_edition")
    openlibrary_work_id = get_data_from_xml("openlibrary_work")
    return openlibrary_version_id, openlibrary_work_id


def add_qualifier(repo, item_with_qualifier_in_it, claim_to_add_qualifier_to, series_item, transcription_page_title, qualifier_property, qualifier_item):
    print(f"Adding qualifier {qualifier_property} to {claim_to_add_qualifier_to} in {item_with_qualifier_in_it}...")
    site = pywikibot.Site('wikidata', 'wikidata')

    qualifier_item = item_page(site, qualifier_item)
    
    # Retrieve the Wikidata item
    item = item_page(site, item_with_qualifier_in_it)
    item.get()

    # Retrieve the claim
    claim = item.claims.get(claim_to_add_qualifier_to)

    # Add the qualifier
    qualifier = pywikibot.Claim(repo, qualifier_property)
    qualifier.setTarget(qualifier_item)
    claim[0].addQualifier(qualifier)

    print_in_green(f"Qualifier {qualifier_property} added to {claim_to_add_qualifier_to} in {item_with_qualifier_in_it}.")


def handle_series(repo, base_work_item, series_item, transcription_page_title):
    part_of_the_series = 'P179'
    has_parts = "P527"
    follows = "P155"
    followed_by = "P156"

    if series_item:
        print("Handling series...")
        add_property(repo, base_work_item, part_of_the_series, series_item, 'part of the series', transcription_page_title)

        previous_item_in_series = get_previous_item_in_series(series_item)
        if previous_item_in_series:


            # add qualifier to the part of the series property of the previous item
            print("Adding follows qualifier to the current item in the series...")
            add_qualifier(repo, base_work_item, part_of_the_series, series_item, transcription_page_title, follows, previous_item_in_series)

            # add_property(repo, base_work_item, part_of_the_series, series_item, 'follows', transcription_page_title, qualifier=follows, qualifier_value=previous_item_in_series)

            print("Adding followed by qualifier to the previous item in the series...")
            add_qualifier(repo, previous_item_in_series, part_of_the_series, series_item, transcription_page_title, followed_by, base_work_item)
            # add_property(repo, previous_item_in_series, part_of_the_series, series_item, 'followed by', transcription_page_title, qualifier=followed_by, qualifier_value=base_work_item)

        print("Adding to the end of the series...")
        add_property(repo, series_item, has_parts, base_work_item, 'has parts (work currently transcribed)', transcription_page_title)
        # add_property(repo, series_item, has_parts, base_work_item, 'has parts', transcription_page_title)





def get_previous_item_in_series(series_item):
    print("Getting previous item in series...")
    previous_item_property = "P527"
    previous_item = get_value_from_property(series_item, previous_item_property, get_last_item=True)
    print(previous_item)
    return previous_item


def handle_sequence(repo, base_work_item, previous_item, transcription_page_title):
    follows = "P155"
    followed_by = "P156"
    if previous_item:
        print("Previous item in sequence of works found. Handling sequence...")
        
        # add previous work to base work item
        add_property(repo, base_work_item, follows, previous_item, 'follows (comes after previous work)', transcription_page_title)

        # add base work to previous work item
        add_property(repo, previous_item, followed_by, base_work_item, 'followed by (comes before next work)', transcription_page_title)