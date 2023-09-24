# WS_collection

# Determine proofread status. If status = proofread or higher, then ok to proceed.

from debug import print_in_red, print_in_green, print_in_yellow
from edit_mw import save_page
import pywikibot
from handle_wikisource_conf import get_regex_match

"""
<onlyinclude>
{{new texts/item|The Calling (film series)/Emma|display=Emma|[[Portal:United States Army|United States Army]]|nowiki=yes|2021|type=film}}
{{new texts/item|The Prose Edda (1916)|Snorri Sturluson|translator=Arthur Gilchrist Brodeur|1916|display=The Prose Edda}}
{{new texts/item|The Gambler and Other Stories|Fyodor Dostoevsky|translator=Constance Garnett|1914}}
{{new texts/item|Weird Tales/Volume 6/Issue 2/In the Forest of Villefère|display=In the Forest of Villefère|Robert E. Howard|1925}}
{{new texts/item|Terrorism Act 2006|[[Portal:Parliament of the United Kingdom|Parliament of the United Kingdom]]|2006|nowiki=yes}}
{{new texts/item|Shakespeare - First Folio facsimile (1910)/The Famous History of the Life of King Henry the Eight|display=The Famous History of the Life of King Henry the Eight|[[Author:William Shakespeare (1564-1616)|William Shakespeare]]|1623|nowiki=yes}}
{{new texts/item|Jack Daniel's Properties v. VIP Products|Supreme Court of the United States|2023}}
{{new texts/item|Investigative Report Concerning the Purchase of Fully Automatic Rifles and Flash-Bang Distraction Devices by NPS Park Rangers|[[Portal:Office of Inspector General (United States Department of the Interior)|Office of Inspector General, Department of the Interior]]|2016|nowiki=yes}}
{{new texts/item|Don't Let Anyone Take It Away|[[Portal:Immigrant and Employee Rights Section|Immigrant and Employee Rights Section, Department of Defense]]|2019|nowiki=yes}}
</onlyinclude>
"""

"<!--MOVE OLDER ENTRIES BELOW HERE-->"

words_to_reject = [
    "nigger",
]

def get_entries(new_texts_page_text):
    onlyinclude = get_regex_match(new_texts_page_text, r"\<onlyinclude\>\n(.+?)\n\<\/onlyinclude\>", "onlyinclude text", dotall=True)
    new_texts_entries = onlyinclude.splitlines()

    return new_texts_entries
    # print(entries)

def move_last_entry_to_old_texts(new_texts_page_text, last_entry):
    move_older_entries_below = "<!--MOVE OLDER ENTRIES BELOW HERE-->"

    # remove last entry from new texts
    new_texts_page_text = new_texts_page_text.replace(last_entry, "")
    new_texts_page_text = new_texts_page_text.replace(move_older_entries_below, f"{move_older_entries_below}{last_entry}")

    return new_texts_page_text

def generate_nowiki_author(author):
    nowiki_author = f"[[Author:{author}|]]|nowiki=yes"
    return nowiki_author

def generate_display_title(mainspace_work_title, title):
    display_title = f"{mainspace_work_title}|display={title}"
    return display_title

def generate_new_texts_item(mainspace_work_title, author, year):
    new_texts_item = f"{{{{new texts/item|{mainspace_work_title}|{author}|{year}}}}}"
    return new_texts_item

def add_to_new_texts(mainspace_work_title, title, author, year):
    print("Adding finished transcription to new texts...")

    for word in words_to_reject:
        if word in title.lower():
            print_in_yellow(f"Title \"{title}\" contains rejected word \"{word}\". Not adding to new texts.")
            return
    
    site = pywikibot.Site("en", "wikisource")
    new_texts_pagename = "Template:New texts"
    new_texts_page = pywikibot.Page(site, new_texts_pagename)
    new_texts_page_text = new_texts_page.text

    new_texts_entries = get_entries(new_texts_page_text)

    for entry in new_texts_entries:
        if author in entry and entry != new_texts_entries[-1]:
            print_in_yellow(f"Author \"{author}\" already exists in new texts. Not adding to new texts.")
            return
    
    last_entry = "\n" + new_texts_entries[-1]

    new_texts_page_text = move_last_entry_to_old_texts(new_texts_page_text, last_entry)

    display_title = mainspace_work_title

    if title != mainspace_work_title:
        display_title = generate_display_title(mainspace_work_title, title)

    if " (" in author:
        author = generate_nowiki_author(author)
    
    new_texts_item = generate_new_texts_item(display_title, author, year)
    print(new_texts_item)
    onlyinclude_start_tag = "<onlyinclude>\n"

    new_texts_page_text = new_texts_page_text.replace(onlyinclude_start_tag, f"{onlyinclude_start_tag}{new_texts_item}\n")

    # print(new_texts_item)
    save_page(new_texts_page, site, new_texts_page_text, f"Adding completed QuickTranscribe project, [[{mainspace_work_title}|{title}]], to new texts...")

    # print(new_texts_page_text)
    
