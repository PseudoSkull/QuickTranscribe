# WS_collection

import pywikibot

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page
from handle_transclusion import generate_defaultsort_tag
from handle_wikisource_conf import get_year_from_date
import re

def format_work_link(work_link, work_title):
    if "/\"" in work_link or work_link.endswith("\""):
        formatted_work_link = f"[[{work_link}|{work_title}]]"
    else:
        formatted_work_link = f"\"[[{work_link}|{work_title}]]\""
    return formatted_work_link

def determine_a_or_an(word):
    if word[0] in "aeiou":
        return "an"
    else:
        return "a"

def get_individual_works_from_author_page(author_page_title, author_page_text, individual_works_string):
    if individual_works_string in author_page_text:
        individual_works = author_page_text.split(individual_works_string)[1]
        individual_works = individual_works.split("\n\n==")[0]
        individual_works = individual_works.split("\n\n\n{{")[0]
        individual_works_as_list = individual_works.split("\n")
        existing_works = []
        wd_authors = []
        for individual_work in individual_works_as_list:
            if individual_work == "":
                continue
            if "WD author" in individual_work:
                wd_authors.append(individual_work)
                continue
            print(f"\"{individual_work}\"")
            existing_work = re.search(r"\[\[(.+?)[\|\]]", individual_work).group(1)
            try:
                work_year = re.search(r"([0-9][0-9][0-9][0-9])", individual_work).group(1)
            except AttributeError:
                work_year = None
            existing_works.append({"work_link": existing_work, "work_year": work_year})
        return individual_works, existing_works, wd_authors
    return None, None, ""

def add_individual_works_to_author_page(subworks, author, work_type_name, original_year):
    site = pywikibot.Site("en", "wikisource")
    author_page_title = "Author:" + author
    author_page = pywikibot.Page(site, author_page_title)
    author_page_text = author_page.text

    # if work_type_name == "short story":
    #     work_type_plural = "short stories"
    # else:
    #     work_type_plural = work_type_name + "s"

    work_type_plural = "poem" + "s" # FOR NOW
    if "short story" in work_type_name:
        work_type_plural = "short stories" # FOR NOW
    elif "essay" in work_type_name:
        work_type_plural = "essays"

    individual_works = f"\n\n===Individual {work_type_plural}===\n"


    # Sort works by DEFAULTSORT and not by name, so that we can sort past "The", "A", etc.
    unsorted_work_links = [{"work_link": i["work_link"], "work_year": get_year_from_date(str(i["original_date"])) if i["original_date"] else f"{original_year}", "work_title": i["title"]} for i in subworks]
    previous_works_listing, existing_works, wd_authors = get_individual_works_from_author_page(author_page_title, author_page_text, individual_works)
    if existing_works:
        unsorted_work_links += existing_works
    
    work_links = []
    print(unsorted_work_links)
    for work_link in unsorted_work_links:
        # work_link["title"] = work["title"]
        defaultsort_tag = generate_defaultsort_tag(work_link["work_link"], for_logic=True)
        work_link["defaultsort"] = defaultsort_tag
        work_links.append(work_link)
    
    work_links = sorted(work_links, key=lambda x: x['defaultsort'])
    print(work_links)

    individual_work_entries = []
    for work_link_item in work_links:
        work_link = work_link_item["work_link"]
        original_year = work_link_item["work_year"]
        if "work_title" in work_link_item:
            work_title = work_link_item["work_title"]
        else:
            work_title = work_link_item["work_link"].split(" (")[0]
        
        formatted_work_link = format_work_link(work_link, work_title)

        if original_year:
            individual_work_entry = f"* {formatted_work_link} ({original_year})"
        else:
            individual_work_entry = f"* {formatted_work_link}"
        individual_work_entries.append(individual_work_entry)


    individual_works += "\n".join(individual_work_entries)
    individual_works = individual_works + "\n" + "\n".join(wd_authors)

    if previous_works_listing:
        author_page_text = author_page_text.replace(previous_works_listing, individual_works)
    else:
        if "==Works about" in author_page_text:
            author_page_text = author_page_text.replace("\n\n==Works about", f"{individual_works}\n\n==Works about")
        else:
            if "\n\n\n{{PD" in author_page_text:
                author_page_text = author_page_text.replace("\n\n\n{{PD", f"{individual_works}\n\n\n{{{{PD")
            elif "\n\n\n{{authority" in author_page_text:
                author_page_text = author_page_text.replace("\n\n\n{{authority", f"{individual_works}\n\n\n{{{{authority")
            else:
                author_page_text = author_page_text.replace("\n\n{{PD", f"{individual_works}\n\n\n{{{{PD")
    

    author_page_text = author_page_text.replace("\n\n\n\n", "\n\n\n")
    author_page_text = author_page_text.replace("\n\n\n==", "\n\n==")
    author_page_text = re.sub(r"\=\=\=Individual (.+?)s\=\=\=\n\n\=", "=", author_page_text)

    print(author_page_text)

    save_page(author_page, site, author_page_text, f"Adding individual subworks to author page")

def add_work_to_related_author_page(work, year):
    related_author = work["related_author"]
    if related_author:
        site = pywikibot.Site("en", "wikisource")
        author_page_title = "Author:" + related_author
        author_page = pywikibot.Page(site, author_page_title)
        author_page_text = author_page.text

        # temp fix
        original_author_page_text = author_page_text

        author_page_text = re.sub(r"(.)\=\=Works about ", r"\1\n\n==Works about ", author_page_text)
        if original_author_page_text != author_page_text:
            save_page(author_page, site, author_page_text, f"Fixing author page text")
            return

        author_page_text = author_page_text.replace("\n==About ", "\n==Works about ")


        work_link = work["work_link"]
        print(f"Related author found for {work_link}: {related_author}! Putting it on the author page for that related author.")
        original_date = work["original_date"]
        if original_date:
            year = get_year_from_date(str(original_date))
        
        work_type = work["type"]
        author = work["author"]
        work_title = work["title"]

        formatted_work_link = format_work_link(work_link, work_title)

        indefinite_article = determine_a_or_an(work_type)

        work_entry = f"* {formatted_work_link} ({year}), {indefinite_article} {work_type} by [[Author:{author}|{author}]]"

        if work_entry in author_page_text:
            print_in_yellow("Work already on author page. Skipping...")
            return
    
        try:
            author_surname = re.search(r"\|.+?lastname.+?\= (.+?)\n", author_page_text).group(1)
        except:
            author_surname = "Jesus" # for now

        if "\n==Works about" not in author_page_text:
            author_page_text = author_page_text.replace("\n\n\n{{PD", f"\n\n==Works about {author_surname}==\n{work_entry}\n\n\n{{{{")
            author_page_text = author_page_text.replace("\n\n{{PD", f"\n\n==Works about {author_surname}==\n{work_entry}\n\n\n{{{{")
            author_page_text = author_page_text.replace("\n\n{{authority", f"\n\n==Works about {author_surname}==\n{work_entry}\n\n\n{{{{authority")
            author_page_text = author_page_text.replace("\n\n{{Authority", f"\n\n==Works about {author_surname}==\n{work_entry}\n\n\n{{{{Authority")
        else:
            author_page_text = author_page_text.replace(f"\n\n==Works about {author_surname}==\n", f"\n\n==Works about {author_surname}==\n{work_entry}\n")
        
        author_page_text = author_page_text.replace("\n\n\n\n", "\n\n\n")
        author_page_text = author_page_text.replace("\n\n\n==", "\n\n==")

        save_page(author_page, site, author_page_text, f"Adding {work_type} to related author page")


def add_works_to_related_authors(subworks, year):
    for work in subworks:
        add_work_to_related_author_page(work, year)