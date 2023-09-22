# WS_collection

import pywikibot
import re
from debug import print_in_red, print_in_green, print_in_yellow, print_in_blue, process_break
from wikidata_utils import get_common_wikidata_item

# work_data = {

# }
    
def wikidata_item_of(variable_description):
    return "Wikidata item of " + variable_description

variables_with_descriptions = {
        "ver": wikidata_item_of("version"),
        "base": wikidata_item_of("base work"),
        "y": "date of publication",
        "oy": "original date of publication",
        "loc": "location of publication",
        "pub": wikidata_item_of("publisher"),
        "f": "filename",
        "au": "author",
        "ty": "work type",
        "ia": "Internet Archive ID",
        "gb": "Google Books ID",
        "ht": "HathiTrust catalog ID",
        "htt": "HathiTrust full text ID",
        "dl": "site to download scan from",
        "dlt": "site to download text from",
        "beg": "chapter beginning formatting",
        "difl": "drop initials float quotes",
        "fqm": "convert fqms",
        "ch": "chapter type",
        "pre": "prefix for chapter names",
        "gen": "genre",
        "com": "Commons category",
        "aux": "toc is auxiliary",
        "sub": "subtitle",
        "ptsub": "chapters are subpages of parts",
        "sec": "section type",
        "secpre": "prefix for subsection names",
        "firstsec": "first section is automatically after chapter",
        "gut": "Gutenberg ID",
        "rel": "related author",
        "ill": "illustrator",
        "ed": "editor",
        "rel": "related author",
        "ser": "series",
        "edno": "edition number",
        "set": "narrative location",
        "progress": "QT progress flag",
    }

statuses = [
    "none",

    # prep
    "boilerplate_created",
    "projectfiles_folders_created",
    "proofreading_in_progress",
    "ia_files_downloaded",
    "hathi_files_downloaded",


    # transcription
    "initial_cleanup_done",
    "page_numbers_placed",
    "hyphenation_inconsistencies_fixed",
    "detected_scannos_fixed",
    "base_work_item_created",
    "version_item_created",
    "commons_category_created",
    "scan_file_uploaded",
    "page_counts_compared",
    "image_counts_compared",
    "images_uploaded",
    "transcription_parsed",
    "index_page_created",
    "pages_created",
    "pages_transcluded",
    "version_disambiguated",
    "work_disambiguated",
    "subpage_wikidata_items_created",
    "subpages_disambiguated",
    "added_to_new_texts",
    "archived",
    "removed_scan_links_from_backlinks",
    "subwork_data_items_created",
    "subworks_disambiguated",
    "subworks_listed_at_author",
    "done",
]

def create_boilerplate():
    boilerplate = """/conf//

progress=boilerplate_created
f=
y=
loc=
pub=
au=
ty=
gen=

ia=
htt=
dl=
dlt=

beg=sc
ch=rom

//conf/

/chform//
<nowiki>
{{ph|class=chapter num|/cpre/ /cnum/}}
{{ph|class=chapter title|/cnam/|level=2}}
</nowiki>
//chform/

/tocform//
<nowiki>
{{TOC row 1-1-1|/cnum/|/cnam/|/pnum/}}
</nowiki>
//tocform/

-cov

/img/

—cov"""
    return boilerplate

def get_conf_value_description(variable_name):
    return f"{variables_with_descriptions[variable_name]} variable"

def get_regex_match(text, regex_pattern, regex_name, dotall=False, important=False):
    print(f"Searching for {regex_name} using {regex_pattern}...")
    if text == None:
        return None

    if dotall:
        matches = re.search(regex_pattern, text, re.DOTALL)
    else:
        matches = re.search(regex_pattern, text)
    
    if matches:
        print_in_green(f"Found {regex_name}!")
        return matches.group(1)
    else:
        if important:
            print_in_red(f"ERROR: Could not find {regex_name}.")
            process_break()
            return None
        print_in_yellow(f"Could not find {regex_name}.")
        return None

def get_conf_variable_regex(variable_name):
    return rf'{variable_name}=(.*)\n'

def get_conf_value(conf_text, variable_name):
    variable_regex = get_conf_variable_regex(variable_name)
    variable_description = get_conf_value_description(variable_name)
    return get_regex_match(conf_text, variable_regex, variable_description)

def find_conf_section(page_text):
    if not page_text:
        return None
    else:
        conf_text = get_regex_match(page_text, r'/conf//(.*?)//conf/', "configuration text", dotall=True, important=True)
        return conf_text

def update_work_data(work_data, variable_name, variable_value):
    variable_description = variables_with_descriptions[variable_name]
    print(f"Updating {variable_name} ({variable_description}) in work data, with value \"{variable_value}\"...")
    work_data[variable_description] = variable_value
    return work_data

def get_conf_values(page_title):
    work_data = {}
    site = pywikibot.Site('en', 'wikisource')  # Set the site name and language code accordingly
    page = pywikibot.Page(site, page_title)
    page_text = page.text
    
    conf_text = find_conf_section(page_text)

    print(f"Getting all configuration variables from {page_title}...")

    for variable_name in variables_with_descriptions.keys():
        variable_value = get_conf_value(conf_text, variable_name)
        if variable_value:
            work_data = update_work_data(work_data, variable_name, variable_value)
        else:
            print_in_yellow(f"{variable_name} not found.")
    
    print_in_green("All configuration variables retrieved from transcription!")
    return work_data

# work_data = get_conf_values("User:PseudoSkull/P/Jalna (1927)")

def get_work_data(work_data, value, dictionary=None):
    print(f"Retrieving {value} from work data...")
    try:
        values_from_work_data = work_data[value]
        if "/" in values_from_work_data:
            values_from_work_data = values_from_work_data.split("/")
        else:
            values_from_work_data = [values_from_work_data,]
        
        wikidata_items = []
        for value in values_from_work_data:
            if dictionary:
                value = get_common_wikidata_item(value, dictionary)
            wikidata_items.append(value)
        
        values_from_work_data = wikidata_items

        if len(values_from_work_data) == 1:
            values_from_work_data = values_from_work_data[0]
        
        print_in_green(f"Retrieved {values_from_work_data} from work data.")
        return values_from_work_data
    except KeyError:
        print_in_yellow(f"Could not retrieve {value} from work data.")
        return None

# def append_work_data(work_data, variable_name, value):
#     key = variables_with_descriptions[variable_name]
#     work_data[key] = value
#     return work_data

def get_year_from_date(date_value):
    year = None
    match = re.search(r'\d{4}', date_value)
    if match:
        year = int(match.group(0))
    return year

def update_conf_value(page_text, variable_name, updated_value, work_data=None):
    conf_text = find_conf_section(page_text)
    current_conf_value = get_conf_value(conf_text, variable_name)
    variable_regex = get_conf_variable_regex(variable_name)
    variable_replacement = rf'{variable_name}={updated_value}\n'

    print(f"Updating \"{variable_name}\" to \"{updated_value}\"...")

    if current_conf_value:
        if current_conf_value == updated_value:
            print_in_yellow(f"Expected value is already \"{current_conf_value}\". Not updated.")
        else:
            page_text = re.sub(variable_regex, variable_replacement, page_text)
            print_in_green(f"Updated {variable_name} from \"{current_conf_value}\" to \"{updated_value}\".")
    else:
        conf_begin = '/conf//\n\n'
        page_text = re.sub(conf_begin, f'{conf_begin}{variable_replacement}', page_text)
        print_in_green(f"Variable {variable_name} created, with value \"{updated_value}\".")
    
    if work_data:
        work_data = update_work_data(work_data, variable_name, updated_value)
        return [page_text, work_data]
    else:
        return page_text


def update_QT_progress(transcription_text, expected_progress):
    progress_variable_name = "progress"
    return update_conf_value(transcription_text, progress_variable_name, expected_progress)

def check_QT_progress(page_text, expected_progress):
    print("Checking QT progress status...")

    if expected_progress not in statuses:
        print_in_red(f"ERROR: Expected progress value '{expected_progress}' is not in list of statuses.")
        exit()

    conf_text = find_conf_section(page_text)

    progress_variable_name = "progress"

    actual_progress = get_conf_value(conf_text, progress_variable_name)
    
    if actual_progress:
        if actual_progress in statuses:
            actual_progress_index = statuses.index(actual_progress)
            expected_progress_index = statuses.index(expected_progress)
            if actual_progress_index < expected_progress_index:
                print_in_yellow(f"Expected progress \"{expected_progress}\" has not yet been done. Ok to do this step.")
                return False
            else:
                print_in_green(f"Expected progress \"{expected_progress}\" has already been done. Skipping this step...")
                return True
        else:
            print_in_red(f"ERROR: Value '{actual_progress}' is not in list of statuses.")
            exit()
    else:
        print_in_yellow(f"QT progress flag not found. Assuming progress is at none. Ok to do this step.")
        return False
    # if actual_progress in statuses:
    #     # more logic here
    #     print_in_green(f"QT progress flag was set to {actual_progress}.")
    #     return actual_progress
    # pass

# def add_to_work_data(work_data, key, value):
#     work_data[key] = value


def find_form_section(page_text, tag):
    form = get_regex_match(page_text, rf"/{tag}form//\n<nowiki>\n(.*?)\n</nowiki>\n//{tag}form/", "form text", dotall=True)

    return form