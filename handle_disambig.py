# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
import pywikibot
from edit_mw import save_page

def standardize_disambiguation_page():
    # properly format to standards what's already at disambiguation page first (logic for this later)
    # create the redirects for works that don't have them yet (logic for this later)
    # find and add new works to disambiguation page based on search (logic for this later)
    # add {{similar}} to all work pages that don't have it yet (logic for this later)
    pass

def add_similar_template_to_page(disambiguation_page_title, work_page_title):
    site = pywikibot.Site("en", "wikisource")
    work_page = pywikibot.Page(site, work_page_title)
    work_page_text = work_page.text
    if "{{similar|" in work_page_text:
        print_in_green("{{similar}} already exists on this page. Skipping step...")
        return
    else:
        similar_template = f"{{{{similar|{disambiguation_page_title}}}}}"
        work_page_text = work_page_text.replace("{{header", f"{similar_template}\n{{{{header")
        work_page_text = work_page_text.replace("{{Header", f"{similar_template}\n{{{{header")
        if "{{header" not in work_page_text.lower():
            work_page_text = f"{similar_template}\n{work_page_text}"

    save_page(work_page, site, work_page_text, "Adding {{similar}} template to page...")

def add_to_disambiguation_page(disambiguation_page_title, work_link, wikisource_link, work_type_name, original_year, work_type, author_WS_name, first_line):
    # standardize_disambiguation_page(), a very hefty function, will call this in later logic
    print("Adding item to disambiguation page...")
    site = pywikibot.Site("en", "wikisource")
    disambiguation_page = pywikibot.Page(site, disambiguation_page_title)
    disambiguation_page_text = disambiguation_page.text
    if "\"" in work_link:
        formatted_work_link = f"[[{work_link}|]]"
    else:
        formatted_work_link = f"\"[[{work_link}|]]\""
    if work_type_name == "poem":
        disambiguation_entry = f"* {formatted_work_link} ({original_year}, \"{first_line}\"), a {work_type_name} by [[Author:{author_WS_name}|]]"    
    else:
        disambiguation_entry = f"* {formatted_work_link} ({original_year}), a {work_type_name} by [[Author:{author_WS_name}|]]"
    


    # LATER: PUT THE WORK NAME IN THE AUTHOR SURNAME HIERARCHY, and in the WORK TYPE HIERARCHY
    if "==See also==" in disambiguation_page_text:
        disambiguation_page_text = disambiguation_page_text.replace("\n\n==See also==", f"\n{disambiguation_entry}\n\n==See also==")
    else:
        disambiguation_page_text += f"\n{disambiguation_entry}"

    print(disambiguation_page_text)

    save_page(disambiguation_page, site, disambiguation_page_text, f"Adding item to disambiguation page...")
    
    add_similar_template_to_page(disambiguation_page_title, wikisource_link)