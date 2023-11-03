# WS_collection

import pywikibot

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page
from handle_transclusion import generate_defaultsort_tag


def add_individual_works_to_author_page(subworks, author, work_type_name, original_year):
    site = pywikibot.Site("en", "wikisource")
    author_page_title = "Author:" + author
    author_page = pywikibot.Page(site, author_page_title)
    author_page_text = author_page.text

    # if work_type_name == "short story":
    #     work_type_plural = "short stories"
    # else:
    #     work_type_plural = work_type_name + "s"

    work_type_plural = "short stories" # FOR NOW

    individual_works = f"\n\n===Individual {work_type_plural}===\n"

    # Sort works by DEFAULTSORT and not by name, so that we can sort past "The", "A", etc.
    unsorted_work_links = [{"work_link": i["work_link"]} for i in subworks]
    work_links = []
    for work_link in unsorted_work_links:
        defaultsort_tag = generate_defaultsort_tag(work_link["work_link"], for_logic=True)
        work_link["defaultsort"] = defaultsort_tag
        work_links.append(work_link)
    
    work_links = sorted(work_links, key=lambda x: x['defaultsort'])
    print(work_links)

    individual_work_entries = []
    for work_link in work_links:
        work_link = work_link["work_link"]
        if "\"" in work_link:
            formatted_work_link = f"[[{work_link}|]]"
        else:
            formatted_work_link = f"\"[[{work_link}|]]\""
        individual_work_entry = f"* {formatted_work_link} ({original_year})"
        individual_work_entries.append(individual_work_entry)

    individual_works += "\n".join(individual_work_entries)



    if "==Works about" in author_page_text:
        author_page_text = author_page_text.replace("\n\n==Works about", f"{individual_works}\n\n==Works about")
    else:
        if "\n\n\n{{PD" in author_page_text:
            author_page_text = author_page_text.replace("\n\n\n{{PD", f"{individual_works}\n\n\n{{{{PD")
        elif "\n\n\n{{authority" in author_page_text:
            author_page_text = author_page_text.replace("\n\n\n{{authority", f"{individual_works}\n\n\n{{{{authority")
        else:
            author_page_text = author_page_text.replace("\n\n{{PD", f"{individual_works}\n\n\n{{{{PD")
    
    print(author_page_text)

    save_page(author_page, site, author_page_text, f"Adding individual subworks to author page")