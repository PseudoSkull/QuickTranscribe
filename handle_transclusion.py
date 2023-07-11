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


def generate_genre_category(genre_name, work_type_name):
    category = genre_name.capitalize()
    if genre_name == "children's" or genre_name == "children":
        category = "Children's books"
    elif genre_name == "historical":
        category = f"Historical {work_type_name}s"
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

# def get_chapter_num(chapter):
#     if "chapter_num" in chapter:
#         chapter_num = chapter["chapter_num"]
#     else:
#         chapter_num = chapter["part_num"]
#     return chapter_num

def generate_chapter_link(chapters, chapter_num_zero_indexed):
    chapter = chapters[chapter_num_zero_indexed]
    chapter_num = chapter["chapter_num"]
    chapter_name = chapter["title"]
    chapter_prefix = chapter["prefix"]
    chapter_internal_name = f"{chapter_prefix} {chapter_num}"

    if chapter_name == None:
        chapter_link = f"[[../{chapter_internal_name}/]]"
    else:
        chapter_link = f"[[../{chapter_internal_name}|{chapter_name}]]"

    return chapter_link


def generate_chapter_links(overall_chapter_num, chapter, chapters):
    front_matter_link = "[[../|Front matter]]"
    return_to_front_matter_link = "[[../|Return to front matter]]"
    chapter_name = chapter["title"]

    if overall_chapter_num == -1: # front matter
        previous_chapter_link = ""
    else:
    # try:
        previous_chapter_num_zero_indexed = overall_chapter_num - 1

        previous_chapter_link = generate_chapter_link(chapters, previous_chapter_num_zero_indexed)
        if previous_chapter_num_zero_indexed == -1:
            previous_chapter_link = front_matter_link


    next_chapter_num_zero_indexed = overall_chapter_num + 1

    try:
        next_chapter_link = generate_chapter_link(chapters, next_chapter_num_zero_indexed)
    except IndexError:
        next_chapter_link = "[[../|Return to front matter]]"

    return previous_chapter_link, next_chapter_link


def pop_pages_not_needing_proofreading(page_data, chapter_start, chapter_end):
    # gather pages not needing proofreading
    pages_not_needing_proofreading = []
    for page_num, page in enumerate(page_data):
        page_num += 1
        if page_num < chapter_start:
            continue
        elif page_num > chapter_end:
            break
        else:
            if page["page_quality"] == "0":
                # chapter_end = page["page_num"] - 1
                pages_not_needing_proofreading.append(page_num)
                # break

    # remove pages not needing proofreading from chapter_end
    for page in reversed(pages_not_needing_proofreading):
        if page == chapter_end:
            chapter_end -= 1
        else:
            break

    return chapter_end

def get_page_tag_splits(page_data, chapter_start, chapter_end):
    splits = []
    for page_num, page in enumerate(page_data):
        page_num_zero_indexed = page_num
        page_num += 1
        previous_page = page_data[page_num_zero_indexed - 1]
        if page_num < chapter_start:
            continue
        elif page_num > chapter_end:
            break
        else:
            page_type = page["type"]
            if page["page_quality"] == "0":
                if previous_page["page_quality"] == "0":
                    continue
                else:
                    splits.append(page_num - 1)
            elif page_type == "break":
                splits.append(page_num)
    # if len(splits) > 0:
    #     print(splits)
    #     exit()
    return splits
    # return

def generate_transclusion_tag(filename, start_page, end_page):
    if start_page != end_page:
        transclusion_tag = f"<pages index=\"{filename}\" from={start_page} to={end_page} />"
    else:
        transclusion_tag = f"<pages index=\"{filename}\" include={start_page} />"
    return transclusion_tag

def get_chapter_transclusion_tags(chapter, chapters, page_data, page_offset, overall_chapter_num, filename):
    # splits = []
    page_num = chapter["page_num"]
    actual_page_num = page_num + page_offset
    chapter_start = actual_page_num
    try:
        chapter_end = chapters[overall_chapter_num + 1]["page_num"] - 1 + page_offset
    except IndexError:
        chapter_end = get_last_page(page_data, chapter_start)

    chapter_end = pop_pages_not_needing_proofreading(page_data, chapter_start, chapter_end)
    splits = get_page_tag_splits(page_data, chapter_start, chapter_end)
    number_of_splits = len(splits)

    chapter_transclusion_tags = []

    if number_of_splits == 1:
        page_split = splits[0]
        page_after_page_split = page_split + 1
        first_tag = generate_transclusion_tag(filename, chapter_start, page_split)
        last_tag = generate_transclusion_tag(filename, page_after_page_split, chapter_end)
        chapter_transclusion_tags.append(first_tag)
        chapter_transclusion_tags.append(last_tag)
    elif number_of_splits > 1:
        pass # logic later
    else:
        chapter_transclusion_tags = generate_transclusion_tag(filename, chapter_start, chapter_end)
    
    page_break = "{{page break|label=}}"

    if type(chapter_transclusion_tags) == list:
        chapter_transclusion_tags = f"\n{page_break}\n".join(chapter_transclusion_tags)

    return chapter_transclusion_tags

def transclude_chapters(chapters, page_data, page_offset, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort, filename):
    for overall_chapter_num, chapter in enumerate(chapters):
        title_display = f"[[../|{title}]]" # for now, would change if the chapter is a subsubsection
        previous_chapter_display, next_chapter_display = generate_chapter_links(overall_chapter_num, chapter, chapters)
        chapter_transclusion_tags = get_chapter_transclusion_tags(chapter, chapters, page_data, page_offset, overall_chapter_num, filename)

        chapter_name = chapter["title"]
        chapter_num = chapter["chapter_num"]
        chapter_prefix = chapter["prefix"]
        chapter_internal_name = f"{chapter_prefix} {chapter_num}"
        if chapter_name == None:
            chapter_name = chapter_internal_name

        chapter_page_title = f"{mainspace_work_title}/{chapter_internal_name}"
        chapter_page = pywikibot.Page(site, chapter_page_title)
        chapter_text = f"""{{{{header
 | title      = {title_display}
 | author     = {author_header_display}
 | section    = {chapter_name}
 | previous   = {previous_chapter_display}
 | next       = {next_chapter_display}
 | notes      = 
}}}}{defaultsort}

{chapter_transclusion_tags}"""
        # print(chapter_text)

        if chapter_name == chapter_internal_name:
            edit_summary = f"Transcluding {chapter_name}..."
        else:
            edit_summary = f"Transcluding {chapter_name} ({chapter_internal_name})..."

        save_page(chapter_page, site, chapter_text, edit_summary, transcription_page_title)


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

    save_page(front_matter_page, site, front_matter_text, "Transcluding front matter...", transcription_page_title)

    transclude_chapters(chapters, page_data, page_offset, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort, filename)