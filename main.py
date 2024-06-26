# WS_collection

# VERSION ITEM IS NOT UPDATING!!!!!

# https://www.wikidata.org/w/index.php?title=Q118876318&curid=113382411&diff=1912734568&oldid=1912670071

import sys
import os

# Path to the pywikibot package within core_stable_2
pywikibot_path = os.path.join("/Users/bobbybumps/Downloads/code_folder/core_stable_2", "pywikibot")

# Prepend the pywikibot path to sys.path to force the import
sys.path.insert(0, pywikibot_path)


import pywikibot
from debug import print_in_red, print_in_green, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page, get_author_page_title, remove_esl_and_ssl_from_backlinks
from hathi import get_hathitrust_catalog_id, get_hathitrust_full_text_id
from handle_repeat_images import handle_repeat_images
from handle_wikidata import get_label, get_wikisource_page_from_wikidata, get_value_from_property, add_index_page_to_version_item, get_author_death_year, add_wikisource_page_to_item, create_version_item, add_version_to_base_work_item, get_wikidata_item_from_wikisource, create_base_work_item, get_commons_category_from_wikidata, get_country_name, add_commons_category_to_item, add_scan_file_to_version_item, add_main_image_to_wikidata_items, get_surname_from_author, get_oclc, get_ark_identifier, get_openlibrary_id, create_gutenberg_version_item, get_book_id_by_oclc
from handle_wikisource_conf import get_work_data, get_conf_values, wikidata_item_of, get_year_from_date, check_QT_progress, update_QT_progress, update_conf_value, find_form_section, get_editor
from parse_transcription import get_chapter_data, get_section_data, generate_toc, parse_transcription_pages, get_bare_title, insert_parsed_pages, generate_illustrations
from handle_index import extract_file_extension, create_index_page, create_index_styles, change_proofread_progress, create_index_pagelist, get_first_page, change_transclusion_progress
from handle_pages import get_page_data, create_pages
from handle_transclusion import transclude_pages, check_if_advertising_transcluded, check_if_parts_exist
from handle_commons import create_commons_category, upload_scan_file, generate_image_data, upload_images_to_commons, get_cover_image_file, get_user_who_scanned_file
from handle_projectfiles import compare_image_counts, get_data_from_xml, archive_projectfiles_folders
from handle_new_texts import add_to_new_texts
from handle_redirects import create_redirects
from config import username, mainspace_work_title, transcription_page_title
from cleanup import initial_text_cleanup, find_hyphenation_inconsistencies, place_page_numbers, find_probable_scannos, compare_page_counts, find_paragraphs_without_ending_punctuation, find_irregular_single_symbols, find_possible_bad_quotation_spacing, find_repeated_characters, find_uneven_quotations, use_spellchecker, find_long_substrings, find_consonant_combos, find_drop_initial_letters, find_entire_words_of_consonants
from handle_dedications import get_dedications
from handle_subworks import get_subwork_data, create_subwork_wikidata_items, redirect_and_disambiguate_subworks
from handle_author import add_individual_works_to_author_page, add_works_to_related_authors
from handle_wikisource_export import test_pdf_export
from handle_openlibrary import get_openlibrary_data
from handle_loc import get_loc_classification
import datetime


# HUGE BUGS TO FIX IMMEDIATELY:
## Transclusion has trouble parsing the first and last pages for some reason... Look into that
## https://en.wikisource.org/w/index.php?title=Page:John_Brown_(1899).pdf/22&action=history - Always blank header and footer in a 0 page PLEASE

# GET OCR DIRECTLY FROM TESSERACT, NOT JUST IA!!!!!!!!!
# modify ia.py and hathi.py logic to use handle_web_downloads
# WAYLAID:
## Self>Self-
## Loose>Loose-






# THE CAROLINA MOUNTAINS
# Parse: Handle dimg elements
# Parse: Make the TOC logic deal with "Index" chapter.
# MAKE SURE IMAGE DATA GOES THRU PROPERLY
# Parse: Handle illustrations
# Parse: Handle index (appendix) pages.
#: Parse page numbers into links
#: <div class="index-chapter"></div>, formatting_continuations
#: Make the lines hang indent?
# IN A SIMILAR VEIN, do the /pl// (pagelink) tags.





# THE STORY OF THE EARTH
# Parse: /fig/ tag, /figform/
# Parse: /plt/ tag
# Parse: /dt/7/






# GRAVESTONES OF EARLY NEW ENGLAND
# Parse: /ix4/ tag
# Parse: Section linking within chapter?
# Parse: \ symbol to escape the / symbol
# /cr/ - cross symbol
# /ast/ - * symbol
# Parse: fine block continuation across pages
# Parse: /sec/n=y/ -> numbered section
# Parse: /sec/f=sc/





# PUTTING ON THE SCREWS
# Waylaid: regex "[any consonant]j " -> "$1, "





# NATHAN HALE (JOHNSTON)
# Parse: dii - automatically
# Parse: If dii and /di/ is arbitrary, do not count that as a dii. Just convert it.
# Parse: /cap// - image caption of previous or next image
# Parse: /bc/ is automatically styled as fine block and width 20em
# Parse: /cap/ty=2/ Type = num settings -> add class of what the normal class is + "2". And add that to the CSS as well.
# Parse: /cap// //cap/ vs. \n/cap//
# Parse: /lri/ - 2 images left and right
# Parse: /Appendix/ should link to the actual appendix
# Parse: /r/ and /rt// (rt doesn't have to end because EVERYTHING IS IN THE REFERENCES)
#: Deal with smallrefs in page and transclusion.



# Music After the Great War, and Other Studies
# Igor Strawinsky: A New Composer - Get subtitle from title
# Related author FOR subwork
# Music After the Great War, disambiguation page for collection and essay



# WORDS FOR THE CHISEL
# Parse: /ri/ in a poem does something with ppoem, what?



# ONE OF THE PILGRIMS
# After pages: Check on earlier instance of Morning Trumpeter for iinc
# Commons: CHANGE TO FLEURON rather than vignette
# Commons: Figure out a way to throw in image filenames that already exist, and then go through these and categorize them in Commons
# Parse: MAKE SURE {{nop}} in POEMS IS MAKING IT BECOME STANZA



# WHEN THE SLEEPER WAKES
# Wikidata: gutia




# https://onlinebooks.library.upenn.edu/webbin/gutbook/lookup?num=63342




# JOYOUS THINGS
# ol: Open Library ID in Wikidata
# Get OCLC from Open
# ol=OL5235359M
# If subtitle has "or", then get alternative title also




# MAKE SURE -399 GOT SECTIONED RIGHT



# So we've got several HUGE PROBLEMS that need to be fixed upon working on the next few works:
# Conf: Conf variables saving without \n
# Transclusion: Prologue/Preface/etc. are being transcluded as "Chapter None" still...
# Transclusion: ../ is only going one level down for parts
# 

# Parse: NEW WORKFLOW: Multiple images in a chapter with page # "img" get iterated per chapter. img2, img3 etc.
# Make it so that filename is checked specifically for the mentioned IA source
# OpenLibrary work often has Library Thing ID and Goodreads ID
# For example: https://openlibrary.org/works/OL144822W for goodreads
# Index chapters of work and elsewhere: /ibid/ tag
# Figure out what to do about film transcriptions
# Ready for export functionality after transclusion
# Try and work on short story collections by multiple authors
# WATCH OUT FOR TWO BLOCK CONTINUATIONS on the same page
# For poems, FIRST LINE IN WIKIDATA ITEMS (version only because different versions might have different first lines)
# For signature images, /sign/ and default name to author of work
# /dedic/i=Q121811188/
# Gutenberg: " 'll" -> "'ll", " 've" -> "'ve", etc.
# Transclusion: Do not add pages if page_quality == "i"
# Parse: /li/ -> link hyphenated words {{lps|hws=Ala|hwe=ddin}}
# "The Flora" -> fix in formatting chapter beginnings to sc
# Cleanup: Might there be a package for finding likely typos in the same manner as an autocorrect tool? What do they use? Can this be implemented in Python?
# Cleanup: Find words/phrases italicized more than once, but not italicized some other times.
# Cleanup: Find periods with lowercase letters after them, or on next page.
# Transclusion: If biography: Category:Biographies of people from the United States
# DETERMINE ITALICIZATION BASED ON WORK TYPE
# PREP: GET IA/HT ID FROM COMMONS FILE MENTIONED
# PREP: MAKE HATHI IMAGES IN PDF ALL SAME SIZE
# PREP: PREPARE INDEX PAGE OCR FOR TRANSCRIPTION through /ind/ tags




# PREP BUG: https://catalog.hathitrust.org/Record/009562668
"""Expected progress "hathi_files_downloaded" has not yet been done. Ok to do this step.
Attempting to get the HathiTrust scan link from: https://catalog.hathitrust.org/Record/009562668
Response code 200. Parsing the HTML...
Success. HathiTrust scan link: https://hdl.handle.net/2027/loc.ark:/13960/t5v69kx6f
Attempting to extract the full text ID from: https://hdl.handle.net/2027/loc.ark:/13960/t5v69kx6f
Success. HathiTrust full text ID: t5v69kx6f
Retrieving number of pages in scan...
Response code not 200. Was: 500
Attempting to download the None HathiTrust images from t5v69kx6f...
Created folder path projectfiles/hathi_images as it did not exist.
Traceback (most recent call last):
  File "/Users/bobbybumps/Downloads/code_folder/core_stable_2/prep.py", line 72, in <module>
    hathi_folder = get_hathitrust_images(hathitrust_full_text_id)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/bobbybumps/Downloads/code_folder/core_stable_2/hathi.py", line 153, in get_hathitrust_images
    for page_num in range(1, number_of_pages+1):
                             ~~~~~~~~~~~~~~~^~
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
CRITICAL: Exiting due to uncaught exception <class 'TypeError'>"""

# CLEANUP: LOOK FOR CONTENT PAGES WITH NO MARKER AFTER PAGE NUMBERS ADDED
# CREATE COMMONS CATEGORY FOR AUTHOR IF AUTHOR COMMONS CATEGORY DOES NOT EXIST
# TITLE CASE LOGIC CAPITALIZES "MR." COMPLETELY
# PROGRAM IN SETTINGS FOR IMAGE SIZES
# PUT IN SOME KIND OF LOGIC FOR THE DIFFERENT TOC BEGINNINGS AND ENDINGS


# not so important:
# FIGURE OUT WHY AN EXTRA {{ }} IS BEING ADDED TO THE GENERATED TOC AND STOP THAT FROM HAPPENING - kinda done?
# TRY TO GET SECTIONS OF FRONT MATTER IN SECTION DATA
# ITALICIZE NUMBERS WITH /I/ TAG


# Index: handle double location
# Index styles: IF NO STYLE IS SPECIFIED, USE THIS
    # """	text-align: center;
	# margin-bottom: 0.75em;""",

# Transclusion: handle double genre


# handle redirects after transclusion
#: for now should only handle "!" -> "" and "O" -> "Oh"

page_break_string = "<!-- page break after this page -->"

chapter_prefixes = { # MAKE FUNCTION THAT DOES THIS
    # There should be functionality for both LINK PREFIXES, and HEADING PREFIXES, because they're different
    "n": None, # no prefix
    "ch": "chapter", # never used, default
    "bk": "book",
    "let": "letter",
}

common_genres = {
    "alternate": "Q224989", # alternate history
    "autobiography": "Q4184",
    "biography": "Q36279",
    "captivity": "Q1035168", # captivity narrative
    "children": "Q56451354",
    "children's": "Q56451354",
    "Christian": "Q1084059",
    "dystopian": "Q15062348",
    "gen": "Q47307",
    "genealogy": "Q47307",
    "fiction": "Q306614",
    "historical": "Q1196408",
    "mystery": "Q6585139",
    "nature": "Q3337126",
    "nonfiction": "Q213051",
    "satire": "Q128758",
    "science fiction": "Q24925",
    "scifi": "Q24925",
    "thriller": "Q182015",
    "utopian": "Q112075077",
    "western": "Q367591",
}

common_work_types = {
    "diary": "Q185598",
    "novel": "Q8261",
    "play": "Q25379",
    "ec": "Q16324495",
    "essay collection": "Q16324495",
    "ic": "Q125659500",
    "illustration album": "Q125659500",
    "poetry collection": "Q12106333",
    "pc": "Q12106333",
    "short story anthology": "Q125544547",
    "short story collection": "Q1279564",
    "ssc": "Q1279564",
    "speech": "Q861911",

    # types that are normally subworks
    "short story": "Q49084",
    "poem": "Q5185279",
    "essay": "Q35760",
}

common_locations = {
    "Atlanta": "Q23556",
    "Boston": "Q100",
    "Champaign": "Q577964",
    "Chattanooga": "Q186702",
    "Chicago": "Q1297",
    "Garden City": "Q739452",
    "Honolulu": "Q18094",
    "Indianapolis": "Q6346",
    "London": "Q84",
    "New York": "Q60",
    "New York City": "Q60",
    "NY": "Q60",
    "Paris": "Q90",
    "Philadelphia": "Q1345",
    "San Francisco": "Q62",
    "Toronto": "Q172",
    "USA": "Q30",
}

common_publishers = {
    "Appleton": "Q3011053",
    "Atlantic": "Q84848622",
    "Burt": "Q24204324",
    "Century": "Q7721960",
    "Dodd": "Q5287721",
    "Doran": "Q5540027",
    "Doubleday": "Q1251563",
    "Duffield": "Q60220388",
    "Grosset": "Q3117078",
    "Harcourt": "Q5654997",
    "Harper": "Q3127696",
    "Houghton": "Q390074",
    "Jacobs": "Q63986176",
    "Knopf": "Q1431868",
    "Little": "Q552959",
    "Lothrop": "Q106389035",
    "Macmillan": "Q2108217",
    "McClurg": "Q4647618",
    "Putnam": "Q3093062",
    "Scribner": "Q845617",
    # "self": "",
    "Small": "Q7542583",
    "Stokes": "Q19443780",
}

# get and define the necessary data

pywikibot.config.base_dir = ('/Users/bobbybumps/Downloads/code_folder/core_stable_2/pywikibot')


site = pywikibot.Site('en', 'wikisource')

for attr, value in site.__dict__.items():
    print(f"{attr}: {value}")
# exit()

commons_site = pywikibot.Site('commons', 'commons')

wikidata_site = pywikibot.Site('wikidata', 'wikidata')

transcription_page = pywikibot.Page(site, transcription_page_title)
current_year = int(datetime.datetime.now().year)
title = get_bare_title(mainspace_work_title)
# title = get_title(mainspace_work_title)

transcription_text = transcription_page.text





# transcription_text = transcription_page.text

work_data = get_conf_values(transcription_page_title)



work_type = get_work_data(work_data, "work type", common_work_types)
work_type_name = get_work_data(work_data, "work type")
genre = get_work_data(work_data, "genre", common_genres)
if work_type_name == "ssa":
    work_type_name = "short story anthology"
if work_type_name == "ssc":
    work_type_name = "short story collection"
elif work_type_name == "pa":
    work_type_name = "poetry anthology"
elif work_type_name == "pc":
    work_type_name = "poetry collection"
elif work_type_name == "ic":
    work_type_name = "illustration album"
elif work_type_name == "ea":
    work_type_name = "essay anthology"
elif work_type_name == "ec":
    work_type_name = "essay collection"
if not work_type_name:
    work_type_name = "work"
genre_name = get_work_data(work_data, "genre")


expected_progress = "initial_cleanup_done"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    transcription_text = initial_text_cleanup(transcription_text, work_type_name)
    save_page(transcription_page, site, transcription_text, "Performing initial text cleanup...")

    process_break()


    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that initial cleanup has been done...")



transcription_text = transcription_page.text
expected_progress = "page_numbers_placed"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    transcription_text = place_page_numbers(transcription_text)
    save_page(transcription_page, site, transcription_text, "Placing page numbers...")

    process_break()


    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that page numbers have been placed...")




transcription_text = transcription_page.text
expected_progress = "hyphenation_inconsistencies_fixed"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    find_hyphenation_inconsistencies(transcription_text)
    process_break()

    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that hyphenation inconsistencies have been fixed...")


page_data = get_page_data(transcription_text)
chapter_type = get_work_data(work_data, "chapter type")
section_type = get_work_data(work_data, "section type")
chapter_beginning_formatting = get_work_data(work_data, "chapter beginning formatting")
drop_initial_letter_data = find_drop_initial_letters(page_data, chapter_beginning_formatting)

# exit()

transcription_text = transcription_page.text
expected_progress = "detected_scannos_fixed"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    print(drop_initial_letter_data)
    find_probable_scannos(transcription_text)
    process_break()
    find_paragraphs_without_ending_punctuation(transcription_text)
    process_break()
    find_irregular_single_symbols(transcription_text)
    process_break()
    find_possible_bad_quotation_spacing(transcription_text)
    process_break()
    find_repeated_characters(transcription_text)
    process_break()
    find_uneven_quotations(transcription_text)
    process_break()
    find_entire_words_of_consonants(transcription_text)
    process_break()
    find_long_substrings(transcription_text)
    process_break()
    find_consonant_combos(transcription_text)
    process_break()
    # FIGURE OUT A BETTER SPELLCHECKER SITUATION
    # use_spellchecker(transcription_text)
    # process_break()
    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that detected scannos have been fixed...")



# create base work item

author = get_work_data(work_data, "author")
if author == "anon":
    author = "Anonymous"

author_namespace_prefix = "Author:"
# this will break later if there are multiple authors
author_page_title = get_author_page_title(author)

illustrator = get_work_data(work_data, "illustrator")
illustrator_page_title = get_author_page_title(illustrator)

editor = get_editor(work_data, transcription_text)
editor_page_title = get_author_page_title(editor)

translator = get_work_data(work_data, "translator")
translator_page_title = get_author_page_title(translator)

related_author = get_work_data(work_data, "related author")
related_author_page_title = get_author_page_title(related_author)

series = get_work_data(work_data, "series")
if series:
    series_name = get_wikisource_page_from_wikidata(series)
else:
    series_name = None

previous_work = get_work_data(work_data, "previous work")

location = get_work_data(work_data, "location of publication", common_locations)
original_location = get_work_data(work_data, "original location", common_locations)
if not original_location:
    original_location = location
if location == "Q30":
    country = "Q30"
else:
    country = get_value_from_property(original_location, "P17", get_last_item=True)

country_name = get_country_name(country)


alternative_title = get_work_data(work_data, "alternative title")
subtitle = get_work_data(work_data, "subtitle")
second_subtitle = get_work_data(work_data, "second subtitle")

subtitle_for_data_items = subtitle

if second_subtitle:
    subtitle_for_data_items = f"{subtitle}: {second_subtitle}"

pub_date = get_work_data(work_data, "date of publication")
year = get_year_from_date(pub_date)
original_pub_date = get_work_data(work_data, "original date of publication")
if not original_pub_date:
    original_pub_date = pub_date
original_year = get_year_from_date(original_pub_date)
commons_category = get_work_data(work_data, "Commons category")

derivative_work = get_work_data(work_data, "derivative work")

base_work = get_work_data(work_data, wikidata_item_of("base work"))

base_work_conf_variable = "base"
author_item = None
author_surname = None
author_death_year = None
author_WD_alias = "Anonymous"
dedications = None

if author != "Anonymous":
    if base_work:
        author_item = get_value_from_property(base_work, "P50")

    if base_work and author_item:
        if not author:
            author = get_wikisource_page_from_wikidata(author_item)
    else:
        author_item = get_wikidata_item_from_wikisource(author_page_title)

    author_WD_alias = get_label(author_item)
    author_death_year = get_author_death_year(author_item)

    author_surname = get_surname_from_author(author_item)

    dedications = get_dedications(page_data, author_item)


illustrator_item = get_wikidata_item_from_wikisource(illustrator_page_title)
editor_item = get_wikidata_item_from_wikisource(editor_page_title)
translator_item = get_wikidata_item_from_wikisource(translator_page_title)
related_author_item = get_wikidata_item_from_wikisource(related_author_page_title)

if not dedications:
    dedications = []

dedications_from_variable = get_work_data(work_data, "dedication")
if dedications_from_variable:
    dedications += [dedications_from_variable,]


narrative_location = get_work_data(work_data, "narrative location")

openlibrary_version_id, openlibrary_work_id = get_openlibrary_id()


hathitrust_id = get_work_data(work_data, "HathiTrust catalog ID")
hathitrust_full_text_id = get_work_data(work_data, "HathiTrust full text ID")

transcription_text = transcription_page.text
if hathitrust_full_text_id and not hathitrust_id:
    hathitrust_id = get_hathitrust_catalog_id(hathitrust_full_text_id)
    transcription_text = update_conf_value(transcription_text, "ht", hathitrust_id)
    save_page(transcription_page, site, transcription_text, "Adding HathiTrust catalog ID value...")
elif hathitrust_id and not hathitrust_full_text_id:
    hathitrust_full_text_id = get_hathitrust_full_text_id(hathitrust_id)
    transcription_text = update_conf_value(transcription_text, "htt", hathitrust_full_text_id)
    save_page(transcription_page, site, transcription_text, "Adding HathiTrust full text ID value...")

ark_identifier = get_ark_identifier(hathitrust_full_text_id)

IA_id = get_work_data(work_data, "Internet Archive ID")
GB_id = get_work_data(work_data, "Google Books ID")

oclc = get_work_data(work_data, "OCLC control number")
if not oclc:
    oclc = get_oclc(hathitrust_id, GB_id)

if not GB_id:
    GB_id = get_book_id_by_oclc(oclc)

lccn = get_data_from_xml("lccn")

if not openlibrary_work_id:
    openlibrary_version_id, openlibrary_work_id, lccn = get_openlibrary_data(openlibrary_version_id, oclc)

# openlibrary_work_id = "OL8421169W"
# openlibrary_version_id = "OL17961024M"


transcription_text = transcription_page.text
expected_progress = "base_work_item_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    base_work = create_base_work_item(base_work, title, work_type, work_type_name, genre, author_item, author_WD_alias, original_pub_date, original_year, country, transcription_page_title, alternative_title, subtitle_for_data_items, related_author_item, series, narrative_location, openlibrary_work_id, previous_work, derivative_work, variable_name=base_work_conf_variable)
    print_in_yellow("Add progress 'base_work_item_created' manually. Restart to mitigate ver= problem (temporary).")
    exit()
    process_break()

    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that base work item has been created...")



version_conf_variable = "ver"

filename = get_work_data(work_data, "filename")
version_item = get_work_data(work_data, wikidata_item_of("version"))
publisher = get_work_data(work_data, wikidata_item_of("publisher"), common_publishers)
# if not lccn:
if not publisher and get_work_data(work_data, wikidata_item_of("publisher")) == "self":
    publisher = author_item

gutenberg_id = get_work_data(work_data, "Gutenberg ID")
gutenberg_ia_id = get_work_data(work_data, "Gutenberg Internet Archive ID")
gutenberg_version_item = get_work_data(work_data, "Gutenberg version item")

edition_number = get_work_data(work_data, "edition number")



transcription_text = transcription_page.text
expected_progress = "version_item_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)


if not at_expected_progress:
    loc_classification = get_loc_classification(lccn)
    version_item = create_version_item(title, version_item, pub_date, year, author_item, author_WD_alias, base_work, publisher, location, filename, hathitrust_id, IA_id, transcription_page_title, GB_id, alternative_title, subtitle_for_data_items, illustrator_item, editor_item, translator_item, dedications, lccn, ark_identifier, oclc, edition_number, openlibrary_version_id, loc_classification, variable_name=version_conf_variable)
    add_version_to_base_work_item(base_work, version_item)

    if gutenberg_id or gutenberg_ia_id:
        print("Gutenberg ID found! Creating Gutenberg version item...")
        gutenberg_version_item = create_gutenberg_version_item(gutenberg_id, gutenberg_ia_id, gutenberg_version_item, title, subtitle_for_data_items, version_item, author_item, translator_item, base_work, transcription_page_title, variable_name="gutver")
        add_version_to_base_work_item(base_work, gutenberg_version_item)

    

    print_in_yellow("Add progress 'version_item_created' manually. Restart to mitigate ver= problem (temporary).")
    exit()
    process_break()

    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_page.text, expected_progress) # ugly solution to a common problem, fix later
    save_page(transcription_page, site, transcription_text, "Noting that version item has been created...")

category_namespace_prefix = "Category:"
commons_category_conf_variable = "com"

# commons_category = get_commons_category_from_wikidata(author_item)

transcription_text = transcription_page.text
expected_progress = "commons_category_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    commons_category, commons_category_title, commons_category_text = create_commons_category(title, category_namespace_prefix, author_item, work_type_name, original_year, country_name, author_WD_alias, series, mainspace_work_title, author_surname, base_work, translator, commons_category)

    commons_category_page = pywikibot.Page(commons_site, commons_category)
    save_page(commons_category_page, commons_site, commons_category_text, f"Creating Commons category for book {title} that will be filled shortly...", transcription_page_title)


    add_commons_category_to_item(base_work, commons_category, commons_category_title)

    process_break()

    transcription_text = update_conf_value(transcription_text, commons_category_conf_variable, commons_category)
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that Commons category has been created...")




filename_conf_variable = "f"
scan_source = get_work_data(work_data, "site to download scan from")
is_personal_scan = get_work_data(work_data, "personal scan")
scanner = get_work_data(work_data, "user who produced scan")

if is_personal_scan:
    scan_source = "scan"
    if not scanner:
        scanner = get_user_who_scanned_file(filename)
        if not scanner:
            scanner = username
else:
    scanner = None

transcription_text = transcription_page.text
expected_progress = "scan_file_uploaded"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    # if not filename:
    filename = upload_scan_file(title, year, version_item, scan_source, scanner, commons_category, IA_id, hathitrust_full_text_id, transcription_page_title, filename, GB_id)

    add_scan_file_to_version_item(wikidata_site, version_item, filename, transcription_page_title)

    process_break()

    transcription_text = update_conf_value(transcription_text, filename_conf_variable, filename)
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that scan file has been uploaded...")






transcription_text = transcription_page.text
expected_progress = "page_counts_compared"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    compare_page_counts(transcription_text, filename)

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that page counts have been compared...")

    handle_repeat_images(transcription_text, transcription_page_title)







advertising_is_transcluded = check_if_advertising_transcluded(page_data)

print(drop_initial_letter_data)

image_data = generate_image_data(page_data, title, year, drop_initial_letter_data)

transcription_text = transcription_page.text
expected_progress = "image_counts_compared"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:

    compare_image_counts(image_data)

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that image counts have been compared...")


transcription_text = transcription_page.text
expected_progress = "images_uploaded"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    upload_images_to_commons(image_data, filename, author_item, author, transcription_page_title, title, year, pub_date, country_name, commons_category, illustrator_item, illustrator)

    add_main_image_to_wikidata_items(base_work, version_item, image_data, transcription_page_title)

    process_break()
    
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that work images have been uploaded...")






cover_image = get_cover_image_file(image_data)





index_page_title = f"Index:{filename}"
file_extension = extract_file_extension(filename)

# author_item = get_wikidata_item_from_wikisource()

# title = get_label(base_work)
print(publisher)
if publisher == author_item:
    publisher_name = "self"
else:
    publisher_name = get_wikisource_page_from_wikidata(publisher)
location_name = get_label(location)

drop_initials_float_quotes = get_work_data(work_data, "drop initials float quotes")
convert_fqms = get_work_data(work_data, "convert fqms")
toc_is_auxiliary = get_work_data(work_data, "toc is auxiliary")
sectioned_transclusion = get_work_data(work_data, "transclusion is sectioned")
chapter_prefix = get_work_data(work_data, "prefix for chapter names")
part_prefix = get_work_data(work_data, "prefix for part names")
# parts_exist = check_if_parts_exist(transcription_text)
parts_exist = False
chapters_are_subpages_of_parts = get_work_data(work_data, "chapters are subpages of parts")
if chapters_are_subpages_of_parts == None and parts_exist:
    chapters_are_subpages_of_parts = True
if chapter_prefix == "Book" or chapter_prefix == "Part":
    chapters_are_subpages_of_parts = False

if chapters_are_subpages_of_parts == "n":
    chapters_are_subpages_of_parts = False

if work_type_name == "poetry collection":
    chapters_are_subpages_of_parts = False

first_section_automatically_after_chapter = get_work_data(work_data, "first section is automatically after chapter")

if first_section_automatically_after_chapter == "n":
    first_section_automatically_after_chapter = False
else:
    first_section_automatically_after_chapter = True

force_chapter_numbers = get_work_data(work_data, "force chapter numbers")

chapters = get_chapter_data(transcription_text, page_data, chapter_prefix, chapters_are_subpages_of_parts, title, chapter_type, work_type_name, force_chapter_numbers, part_prefix, sectioned_transclusion)

sections = get_section_data(chapters, page_data, transcription_text, first_section_automatically_after_chapter)

toc_format = find_form_section(transcription_text, "toc")
chapter_format = find_form_section(transcription_text, "ch")
section_format = find_form_section(transcription_text, "sec")

toc = generate_toc(chapters, mainspace_work_title, toc_format, toc_is_auxiliary, page_data, chapters_are_subpages_of_parts)

if "/illus/" in transcription_text:
    illustrations = generate_illustrations(image_data, page_data, chapters, mainspace_work_title, transcription_text)
else:
    illustrations = ""

transcription_text = transcription_page.text
expected_progress = "transcription_parsed"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    page_data = parse_transcription_pages(page_data, image_data, transcription_text, chapters, sections, mainspace_work_title, title, toc, chapter_format, section_format, chapter_beginning_formatting, drop_initials_float_quotes, convert_fqms, page_break_string, chapter_type, section_type, illustrations, work_type_name, first_section_automatically_after_chapter, sectioned_transclusion)

    transcription_text = insert_parsed_pages(page_data, transcription_text)

    save_page(transcription_page, site, transcription_text, "Parsing QT transcription into wiki markup...")

    print_in_blue("REMEMBER TO PROOFREAD THE TOC/ILLUSTRATIONS PAGES! THOSE WERE GENERATED AUTOMATICALLY!")
    process_break()

    # update transcription text since it's probably been modified since parsing
    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that transcription has been parsed, and is ready for Wikisource entry...")

# Get page data again, since it's been updated
page_data = get_page_data(transcription_text, page_break_string)

# for page in page_data:
#     print(page)
# exit()

index_pagelist = create_index_pagelist(page_data)

# print(index_pagelist)

first_page = get_first_page(index_pagelist)

# exit()

transcription_text = transcription_page.text
expected_progress = "index_page_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    create_index_page(index_page_title, index_pagelist, transcription_text, mainspace_work_title, title, author, illustrator, editor, translator, publisher_name, year, file_extension, location_name, version_item, transcription_page_title, page_data, filename, toc_is_auxiliary, toc)

    process_break()

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that index page has been created...")



transcription_text = transcription_page.text
expected_progress = "pages_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    create_pages(page_data, filename, transcription_page_title, username, page_break_string)

    process_break()

    change_proofread_progress(index_page_title)

    transcription_text = transcription_page.text
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that pages in the Page namespace have been created...")




transcription_text = transcription_page.text
expected_progress = "pages_transcluded"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    transclude_pages(chapters, page_data, first_page, mainspace_work_title, title, author, year, filename, cover_image, author_death_year, transcription_page_title, original_year, work_type_name, genre_name, country, toc_is_auxiliary, advertising_is_transcluded, current_year, related_author, series_name, editor, translator, derivative_work, transcription_text, chapters_are_subpages_of_parts, sectioned_transclusion)

    create_redirects(mainspace_work_title, alternative_title, subtitle, second_subtitle)

    process_break()

    change_transclusion_progress(index_page_title, advertising_is_transcluded)

    add_wikisource_page_to_item(version_item, mainspace_work_title)

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that the work is fully transcluded...")


transcription_text = transcription_page.text
expected_progress = "added_to_new_texts"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    add_to_new_texts(mainspace_work_title, title, author, original_year)

    process_break()

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that the completed work has been added to New texts...")

transcription_text = transcription_page.text
expected_progress = "archived"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    # archive transcription
    transcription_text = "<syntaxhighlight lang=\"wikitext\">\n" + transcription_text + "\n</syntaxhighlight>\n[[Category:Finished QuickTranscribe projects]]"
    save_page(transcription_page, site, transcription_text, "Archiving QT transcription...")

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that transcription has been archived...")
    # exit()

transcription_text = transcription_page.text
expected_progress = "removed_scan_links_from_backlinks"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    remove_esl_and_ssl_from_backlinks(mainspace_work_title)

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that transcription backlink scan templates have been removed...")



# STOPPED FOR NOW DUE TO KNOWN ISSUE WITH EXPORTER (not related to QT at all)

# transcription_text = transcription_page.text
# expected_progress = "export_tested"
# at_expected_progress = check_QT_progress(transcription_text, expected_progress)

# if not at_expected_progress:
#     test_pdf_export(mainspace_work_title)

#     transcription_text = update_QT_progress(transcription_text, expected_progress)
#     save_page(transcription_page, site, transcription_text, "Noting that export of the work has been tested...")


# exit()






subworks = get_subwork_data(chapters, page_data, image_data, mainspace_work_title)

if subworks:

    transcription_text = transcription_page.text
    expected_progress = "subwork_data_items_created"
    at_expected_progress = check_QT_progress(transcription_text, expected_progress)

    if not at_expected_progress:
        create_subwork_wikidata_items(subworks, version_item, base_work, title, transcription_page_title, year, original_year, author_WD_alias, author_item, pub_date, country, genre, original_pub_date, narrative_location)

        process_break()

        transcription_text = update_QT_progress(transcription_text, expected_progress)
        save_page(transcription_page, site, transcription_text, "Noting that the subwork Wikidata items have all been created...")


    transcription_text = transcription_page.text
    expected_progress = "subworks_disambiguated"
    at_expected_progress = check_QT_progress(transcription_text, expected_progress)

    if not at_expected_progress:
        redirect_and_disambiguate_subworks(subworks, author_surname, original_year, author, title)

        process_break()

        transcription_text = update_QT_progress(transcription_text, expected_progress)
        save_page(transcription_page, site, transcription_text, "Noting that the subwork Wikidata items have all been created...")


    transcription_text = transcription_page.text
    expected_progress = "subworks_listed_at_author"
    at_expected_progress = check_QT_progress(transcription_text, expected_progress)

    if not at_expected_progress:
        add_individual_works_to_author_page(subworks, author, work_type_name, original_year)

        process_break()

        transcription_text = update_QT_progress(transcription_text, expected_progress)
        save_page(transcription_page, site, transcription_text, "Noting that the subworks have been listed at the author page...")

    transcription_text = transcription_page.text
    expected_progress = "subworks_added_to_related_authors"
    at_expected_progress = check_QT_progress(transcription_text, expected_progress)

    if not at_expected_progress:
        add_works_to_related_authors(subworks, year)
        process_break()

        transcription_text = update_QT_progress(transcription_text, expected_progress)
        save_page(transcription_page, site, transcription_text, "Noting that the subworks have been added to the related authors' pages...")

transcription_text = transcription_page.text
expected_progress = "projectfiles_folders_archived"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    archive_projectfiles_folders()

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that projectfiles folders have been archived locally...")
