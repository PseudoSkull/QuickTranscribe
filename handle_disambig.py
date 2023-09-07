# WS_collection

import pywikibot
from edit_mw import save_page

def standardize_disambiguation_page():
    # properly format to standards what's already at disambiguation page first (logic for this later)
    # create the redirects for works that don't have them yet (logic for this later)
    # find and add new works to disambiguation page based on search (logic for this later)
    # add {{similar}} to all work pages that don't have it yet (logic for this later)
    pass

def add_to_disambiguation_page(disambiguation_page_title, work_link, work_type_name, original_year, work_type, author_WS_name):
    # standardize_disambiguation_page(), a very hefty function, will call this in later logic
    site = pywikibot.Site("en", "wikisource")
    disambiguation_page = pywikibot.Page(site, disambiguation_page_title)
    disambiguation_page_text = disambiguation_page.text
    if "\"" in work_link:
        formatted_work_link = f"[[{work_link}|]]"
    else:
        formatted_work_link = f"\"[[{work_link}|]]\""
    disambiguation_entry = f"* {formatted_work_link} ({original_year}), a {work_type} by [[Author:{author_WS_name}|]]"
    
    if "==See also==" in disambiguation_page_text:
        disambiguation_page_text = disambiguation_page_text.replace("\n\n==See also==", f"{disambiguation_entry}\n\n==See also==")
    else:
        disambiguation_page_text += f"\n{disambiguation_entry}"

    print(disambiguation_page_text)
    
    exit()