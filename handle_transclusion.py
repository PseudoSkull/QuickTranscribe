# WS_collection

import pywikibot
import re
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from handle_wikidata import get_value_from_property
from edit_mw import save_page
import json

# FIND A WAY TO CLEAN THE TRANSCLUDE PAGES LOGIC UP. IT'S A BIT OF A MESS.

eras = {
    "modern": 1900,
    "early modern": 1631,
    "renaissance": 1421,
    "medieval": 601,
    "ancient": 0,
}
# Ancient	Before AD 600
# Medieval	601–1420
# Renaissance	1421–1630
# Early modern	1631–1899
# Modern	1900–present


def generate_genre_category(genre_name):
    category = genre_name.capitalize()
    if genre_name == "children's fiction":
        category = "Children's literature"
    return category

def generate_type_category(work_type_name, country):
    # print(work_type_name)
    "P1549: demonym"
    demonym = get_value_from_property(country, "P1549")

    # convert to JSON then to dict, to get it out of type WbMonolingualText
    # demonym = json.loads(demonym.toJSON())

    """
    Demonym returns:
    {
        "language": "en",
        "text": "American"
    }
    """

    if demonym:
        demonym_language = demonym.language
        demonym_text = demonym.text
        if demonym_language == "en":
            demonym = demonym_text
        else:
            print_in_red(f"Demonym found for {country}, but it wasn't in English.")
            process_break()
    else:
        print_in_red(f"No demonym found for {country}.")
        process_break()

    type_category = f"{demonym} {work_type_name}s"

    return type_category

def generate_era_category(original_year):
    for era, start_year in eras.items():
        if original_year >= start_year:
            category_name = era.capitalize() + " works"
            return category_name
    
def get_last_page(page_data, chapter_start):
    for page_num, page in enumerate(page_data):
        if page_num < chapter_start:
            continue
        else:
            if page["page_quality"] == "0":
                return page["page_num"] - 1

def generate_toc_page_tag(toc_pages, filename):
    toc_begin = toc_pages[0]
    toc_end = toc_pages[-1]
    page_tag = f"<pages index=\"{filename}\" from={toc_begin} to={toc_end} />"
    return page_tag

def transclude_pages(chapters, page_data, first_page, mainspace_work_title, title, author_WS_name, year, filename, cover_filename, author_death_year, transcription_page_title, original_year, work_type_name, genre_name, country):
    # author_death_year, transcription_page_title
    site = pywikibot.Site('en', 'wikisource')
    # transclude front matter page
    front_matter_page = pywikibot.Page(site, mainspace_work_title)
    page_offset = first_page - 1

    # chapter_names = list(chapters.keys())
    # chapter_page_nums = list(chapters.values())

    first_chapter = chapters[0]
    first_chapter_name = first_chapter["title"]
    first_chapter_page_num = first_chapter["page_number"]
    first_content_page = first_chapter_page_num + page_offset
    print("First content page:", first_content_page)

    author_header_display = author_WS_name # for now. There will be logic here later.
    defaultsort = "" # for now. There will be logic here later.
    # disambiguation_pointer = f"{{{{other versions|{title}}}}}\n" # for now. There will be logic here later.
    disambiguation_pointer = "" # for now. There will be logic here later.
    # Hierarchy: disambig > work > version
    # IDEA: Go to version_item, then check base_work for a versions page on WS. If it doesn't have one, then check for disambig.

    if cover_filename:
        cover_display = f"""
 | cover      = {cover_filename}"""
    else:
        cover_display = ""



    front_matter_header = f"""{disambiguation_pointer}{{{{header
 | title      = {title}
 | author     = {author_header_display}
 | section    = 
 | previous   = 
 | next       = [[/Chapter 1|{first_chapter_name}]]
 | year       = {year}{cover_display}
 | notes      = 
}}}}{defaultsort}

"""
    # produce all the page tags
    pages_tags = []
    toc_pages = []
    for page_num in range(1, first_content_page):
        page_num_zero_indexed = page_num - 1
        page = page_data[page_num_zero_indexed]
        page_quality = page["page_quality"]
        page_type = page["type"]
        if page_quality != "0":
            if page_type == "toc":
                toc_pages.append(page_num)
                if page_num == first_content_page - 1:
                    page_tag = generate_toc_page_tag(toc_pages, filename)
                    toc_pages = []
                else:
                    continue
            else:
                if len(toc_pages) > 0:
                    page_tag = generate_toc_page_tag(toc_pages, filename)
                    toc_pages = []
                page_tag = f"<pages index=\"{filename}\" include={page_num} />"
            pages_tags.append(page_tag)
    page_break = "{{page break|label=}}"
    page_tags = f"\n{page_break}\n".join(pages_tags)
    # remove the last page break
    # page_tags.split("\n")
    # page_tags.pop()
    # page_tags = "\n".join(pages_tags)


    copyright_template_name = "PD-US" # for now, some logic later
    additional_copyright_parameters = f"|{author_death_year}" # for now, some logic later

    # categories = ["Ready for export"] # for now, some logic later
    era_category = generate_era_category(original_year)
    type_category = generate_type_category(work_type_name, country)
    genre_category = generate_genre_category(genre_name)

    categories = []

    categories.append(era_category)
    categories.append(type_category)
    categories.append(genre_category)

    categories.sort()

    categories_text = []

    for category in categories:
        categories_text.append(f"[[Category:{category}]]")
    if len(categories) > 0:
        categories_text = "\n\n" + "\n".join(categories_text)
    else:
        categories_text = ""
    front_matter_footer = f"""


{{{{authority control}}}}
{{{{{copyright_template_name}{additional_copyright_parameters}}}}}{categories_text}"""

    front_matter_text = front_matter_header + page_tags + front_matter_footer

    save_page(front_matter_page, site, front_matter_text, "Transcluding front matter...", transcription_page_title)

    chapter_num = 0

    for chapter_num, chapter in enumerate(chapters):
        chapter_num_zero_indexed = chapter_num
        chapter_num = chapter_num + 1 # 1 indexed
        chapter_name = chapter["title"]
        chapter_start = chapter["page_number"] + page_offset
        title_display = f"[[../|{title}]]" # for now, would change if the chapter is a subsubsection

        # try:
        previous_chapter_num_zero_indexed = chapter_num_zero_indexed - 1
        previous_chapter_num = chapter_num - 1
        previous_chapter = chapters[previous_chapter_num_zero_indexed]
        previous_chapter_name = previous_chapter["title"]
        previous_chapter_display = f"[[../Chapter {previous_chapter_num}|{previous_chapter_name}]]"
    # except IndexError:
        if previous_chapter_num == 0:
            previous_chapter_display = "[[../|Front matter]]"

        try:
            next_chapter_num_zero_indexed = chapter_num_zero_indexed + 1
            next_chapter_num = chapter_num + 1
            next_chapter = chapters[next_chapter_num_zero_indexed]
            next_chapter_name = next_chapter["title"]
            next_chapter_display = f"[[../Chapter {next_chapter_num}|{next_chapter_name}]]"
            next_chapter_page_num = next_chapter["page_number"] + page_offset
            chapter_end = next_chapter_page_num - 1
        except IndexError:
            next_chapter_display = "[[../|Return to front matter]]"
            chapter_end = get_last_page(page_data, chapter_start)

        chapter_page_title = f"{mainspace_work_title}/Chapter {chapter_num}"
        chapter_page = pywikibot.Page(site, chapter_page_title)
        chapter_text = f"""{{{{header
 | title      = {title_display}
 | author     = {author_header_display}
 | section    = {chapter_name}
 | previous   = {previous_chapter_display}
 | next       = {next_chapter_display}
 | notes      = 
}}}}{defaultsort}

<pages index="{filename}" from={chapter_start} to={chapter_end} />"""

        save_page(chapter_page, site, chapter_text, f"Transcluding chapter {chapter_name} ({chapter_num})...", transcription_page_title)