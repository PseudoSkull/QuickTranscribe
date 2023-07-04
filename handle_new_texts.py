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

def generate_new_texts_item(mainspace_work_title, author, year):
    new_texts_item = f"{{{{new texts/item|{mainspace_work_title}|{author}|{year}}}}}"
    return new_texts_item

def add_to_new_texts(mainspace_work_title, author, year):
    print("Adding finished transcription to new texts...")

    site = pywikibot.Site("en", "wikisource")
    new_texts_pagename = "Template:New texts"
    new_texts_page = pywikibot.Page(site, new_texts_pagename)
    new_texts_page_text = new_texts_page.text

    new_texts_entries = get_entries(new_texts_page_text)
    last_entry = "\n" + new_texts_entries[-1]

    new_texts_page_text = move_last_entry_to_old_texts(new_texts_page_text, last_entry)

    new_texts_item = generate_new_texts_item(mainspace_work_title, author, year)
    onlyinclude_start_tag = "<onlyinclude>\n"

    new_texts_page_text = new_texts_page_text.replace(onlyinclude_start_tag, f"{onlyinclude_start_tag}{new_texts_item}\n")

    save_page(new_texts_page, site, new_texts_page_text, f"Adding completed QuickTranscribe project, [[{mainspace_work_title}]], to new texts...")

    # print(new_texts_page_text)
    # add new entry to new texts
    # new_texts_page_text = new_texts
    





    # new_texts_page_text += f"\n* [[{mainspace_work_title}]] ({author}, {year})"
    # new_texts_page.text = new_texts_page_text
    # new_texts_page.save("Adding new text to list of new texts", minor=False)
    # print_in_green("Added to new texts.")