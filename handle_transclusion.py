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

def get_chapter_num(chapter):
    if "chapter_num" in chapter:
        chapter_num = chapter["chapter_num"]
    else:
        chapter_num = chapter["part_num"]
    return chapter_num

def generate_chapter_link(chapters, chapter_num, chapter_num_zero_indexed):
    chapter = chapters[chapter_num_zero_indexed]
    # chapter_num = chapter_num_zero_indexed + 1
    
    # chapter_num = get_chapter_num(chapter)
    chapter_name = chapter["title"]
    chapter_prefix = chapter["prefix"]

    if chapter_name == None:
        chapter_link = f"[[../{chapter_prefix} {chapter_num}/]]"
    else:
        chapter_link = f"[[../{chapter_prefix} {chapter_num}|{chapter_name}]]"
    
    return chapter_link


def generate_chapter_links(chapter_num, part_num, chapter, chapters, subchapters_currently_being_iterated):
    chapter_num_zero_indexed = chapter_num - 1
    part_num_zero_indexed = part_num - 1
    front_matter_link = "[[../|Front matter]]"
    return_to_front_matter_link = "[[../|Return to front matter]]"

    # chapter_num = chapter_num + 1 # 1 indexed
    chapter_name = chapter["title"]
    # chapter_start = chapter["page_num"] + page_offset

    if chapter_num_zero_indexed == -1: # front matter
        previous_chapter_link = ""
    else:
    # try:
        previous_chapter_num_zero_indexed = chapter_num_zero_indexed - 1
        previous_chapter_num = chapter_num - 1
        previous_chapter = chapters[previous_chapter_num_zero_indexed]
        # print(previous_chapter_num)
        # print(previous_chapter)
        # print(chapter_num)

        if previous_chapter_num == 0:
            if subchapters_currently_being_iterated:
                previous_chapter_link = generate_chapter_link(chapters, part_num, part_num_zero_indexed)
            else:
                previous_chapter_link = front_matter_link
        elif "subchapters" in previous_chapter:
            previous_subchapters = previous_chapter["subchapters"]
            previous_subchapter = previous_subchapters[-1]
            # previous_chapter_subpages_num = len(previous_chapter_subpages)
            previous_chapter_num_zero_indexed = len(previous_subchapters) - 1
            previous_chapter_num = previous_subchapter["chapter_num"]
            # previous_chapter_subpages_num_zero_indexed = previous_chapter_subpages_num - 1
            previous_chapter_link = generate_chapter_link(previous_subchapters, previous_chapter_num, previous_chapter_num_zero_indexed)
        else:
            previous_chapter_link = generate_chapter_link(chapters, previous_chapter_num, previous_chapter_num_zero_indexed)



    next_chapter_num_zero_indexed = chapter_num_zero_indexed + 1
    next_chapter_num = chapter_num + 1
    # next_chapter = chapters[next_chapter_num_zero_indexed]
    # next_chapter_page_num = next_chapter["marker"]

    try:
        next_chapter_link = generate_chapter_link(chapters, next_chapter_num, next_chapter_num_zero_indexed)
        # chapter_end = next_chapter_page_num - 1
    except IndexError:
        if subchapters_currently_being_iterated:
            next_part_num = part_num + 1
            next_part_num_zero_indexed = part_num_zero_indexed + 1
            try:
                next_chapter_link = generate_chapter_link(chapters, next_part_num, next_part_num_zero_indexed)
            except IndexError:
                next_chapter_link = return_to_front_matter_link
        else:
            next_chapter_link = return_to_front_matter_link
        # chapter_end = get_last_page(page_data, chapter_start)


        # next_chapter_page_num = next_chapter["page_num"] + page_offset
    # except IndexError:
    
    return previous_chapter_link, next_chapter_link

def transclude_chapters(overall_chapter_num, part_num, chapters, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort, subchapters_currently_being_iterated=None):
    # overall_chapter_num = 0
    if subchapters_currently_being_iterated:
        parts = chapters
        chapters = subchapters_currently_being_iterated
        overall_chapter_num += 1
    for chapter in chapters:
        # overall_chapter_num += 1
        title_display = f"[[../|{title}]]" # for now, would change if the chapter is a subsubsection
        chapter_name = chapter["title"]
        chapter_num = get_chapter_num(chapter)
        # print(chapter)
        chapter_prefix = chapter["prefix"]
        if chapter_name == None:
            chapter_name = f"{chapter_prefix} {chapter_num}"

        # else:
        # if subchapters_currently_being_iterated:
        previous_chapter_display, next_chapter_display = generate_chapter_links(chapter_num, part_num, chapter, chapters, subchapters_currently_being_iterated)
        # else:
            # previous_chapter_display, next_chapter_display = generate_chapter_links(chapter_num, part_num, chapter, chapters, chapters)

        if "subchapters" in chapter:
            # print("GOT HERE")
            part_num_zero_indexed = part_num
            part_num += 1
            # part_num_zero_indexed = part_num - 1
            # previous_part_num = part_num_zero_indexed - 1
            subchapters = chapter["subchapters"]
            first_subchapter_index = 0
            first_subchapter = subchapters[first_subchapter_index]
            first_subchapter_num = get_chapter_num(first_subchapter)
            # previous_subpages = previous_part_num
            # if last_subchapter_of_previous_part:
            #     previous_chapter_display = last_subchapter_of_previous_part
            next_chapter_display = generate_chapter_link(subchapters, first_subchapter_num, first_subchapter_index)
            
        chapter_page_title = f"{mainspace_work_title}/{chapter_prefix} {chapter_num}"
        chapter_page = pywikibot.Page(site, chapter_page_title)
        chapter_text = f"""{{{{header
 | title      = {title_display}
 | author     = {author_header_display}
 | section    = {chapter_name}
 | previous   = {previous_chapter_display}
 | next       = {next_chapter_display}
 | notes      = 
}}}}{defaultsort}

"""
# <pages index="{filename}" from={chapter_start} to={chapter_end} />"""

        # save_page(chapter_page, site, chapter_text, f"Transcluding chapter {chapter_name} ({chapter_num})...", transcription_page_title)

        # if chapter_has_subpages:
        #    recursive function after save page

        # if last of subpages:
        #     return last_subchapter_of_previous_part
        print(chapter_text)

        if "subchapters" in chapter:
            parent_page = ""
            previous_part_link = generate_chapter_link(chapters, part_num, part_num_zero_indexed)
            print(previous_part_link)
            # exit()
            transclude_chapters(overall_chapter_num, part_num, chapters, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort, subchapters_currently_being_iterated=subchapters)


def transclude_pages(chapters, page_data, first_page, mainspace_work_title, title, author_WS_name, year, filename, cover_filename, author_death_year, transcription_page_title, original_year, work_type_name, genre_name, country, toc_is_auxiliary):
    # author_death_year, transcription_page_title
    site = pywikibot.Site('en', 'wikisource')
    # transclude front matter page
    front_matter_page = pywikibot.Page(site, mainspace_work_title)
    page_offset = first_page - 1

    # chapter_names = list(chapters.keys())
    # chapter_page_nums = list(chapters.values())

    first_chapter = chapters[0]
    first_chapter_name = first_chapter["title"]
    first_chapter_page_num = first_chapter["page_num"]
    first_content_page = first_chapter_page_num + page_offset
    first_chapter_prefix = first_chapter["prefix"]
    first_chapter_num = 1
    if first_chapter_name == None:
        first_chapter_display = f"[[/{first_chapter_prefix} {first_chapter_num}/]]"
    else:
        first_chapter_display = f"[[/{first_chapter_prefix} {first_chapter_num}|{first_chapter_name}]]"
    print("First content page:", first_content_page)


    if "(" in author_WS_name:
        override_author = "| override_author = "
        author_header_display = f"{override_author}[[Author:{author_WS_name}|]]"
    else:
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
 | next       = {first_chapter_display}
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

    aux_toc = ""

    if toc_is_auxiliary:
        aux_toc = f"\n\n{{{{{mainspace_work_title}/TOC}}}}"

    copyright_template_name = "PD-US" # for now, some logic later
    additional_copyright_parameters = f"|{author_death_year}" # for now, some logic later

    # categories = ["Ready for export"] # for now, some logic later
    categories = []

    era_category = generate_era_category(original_year)
    categories.append(era_category)

    type_category = generate_type_category(work_type_name, country)
    categories.append(type_category)

    if genre_name:
        genre_category = generate_genre_category(genre_name)
        categories.append(genre_category)




    categories.sort()

    categories_text = []

    for category in categories:
        if category != None:
            categories_text.append(f"[[Category:{category}]]")
    if len(categories) > 0:
        categories_text = "\n\n" + "\n".join(categories_text)
    else:
        categories_text = ""
    front_matter_footer = f"""


{{{{authority control}}}}
{{{{{copyright_template_name}{additional_copyright_parameters}}}}}{categories_text}"""

    front_matter_text = front_matter_header + page_tags + aux_toc + front_matter_footer

    print(front_matter_text)

    # save_page(front_matter_page, site, front_matter_text, "Transcluding front matter...", transcription_page_title)

    # chapter_num = 0

    subpages = None
    part_num = 0
    overall_chapter_num = 0
    # function for transcluding chapters. parent_page starts as false. if parent_page, parent_page is the previous link of the first chapter. if chapter has subpages, initiate recursive function.
    transclude_chapters(overall_chapter_num, part_num, chapters, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort)