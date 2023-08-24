# WS_collection

import pywikibot
import re
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from handle_wikidata import get_value_from_property
from edit_mw import save_page, get_english_plural, has_digits
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


def generate_genre_categories(genre_name, work_type_name):
    # categories = genre_name.capitalize()
    if type(genre_name) == str:
        genres = [genre_name,]
    else:
        genres = genre_name
    categories = []
    for genre in genres:
        work_type_plural = get_english_plural(work_type_name)
        if genre == "alternate":
            category = "Alternate history"
        if genre == "autobiography":
            category = "Autobiographies"
        if genre == "biography":
            category = "Biographies"
        if genre == "children's" or genre == "children":
            category = "Children's books"
        elif genre == "historical":
            if work_type_name == "novel":
                category = f"Historical fiction novels"
            else:
                category = f"Historical {work_type_plural}"
        elif genre == "Christian":
            category = "Christian literature"
        categories.append(category)
    return categories

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

    if work_type_name == "work":
        type_category = f"{demonym} literature"
    else:
        work_type_plural = get_english_plural(work_type_name)
        type_category = f"{demonym} {work_type_plural}"

    return type_category

def generate_era_category(original_year):
    for era, start_year in eras.items():
        if original_year >= start_year:
            category_name = era.capitalize() + " works"
            return category_name
    
def get_last_page(page_data, chapter_start):
    # for page_num, page in enumerate(page_data):
    #     if page_num < chapter_start:
    #         continue
    #     else:
    #         if page["type"] == "last":
    #             return page["page_num"]
            # if page["page_quality"] == "0":
            #     return page["page_num"] - 1
    return len(page_data) - 1

def generate_toc_page_tag(toc_pages, filename):
    toc_begin = toc_pages[0]
    toc_end = toc_pages[-1]
    page_tag = f"<pages index=\"{filename}\" from={toc_begin} to={toc_end} />"
    return page_tag

def generate_chapter_link(chapters, chapter_num_zero_indexed):
    chapter = chapters[chapter_num_zero_indexed]
    chapter_num = chapter["chapter_num"]
    chapter_name = chapter["title"]
    chapter_prefix = chapter["prefix"]
    if not chapter_prefix:
        chapter_prefix = "Chapter"
    chapter_internal_name = f"{chapter_prefix} {chapter_num}"

    if chapter_num == None:
        chapter_link = f"[[../{chapter_name}/]]"
    elif chapter_name == None:
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
        if chapter_end:
            if page_num > chapter_end:
                break
        if page_num < chapter_start:
            continue
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
        if chapter_end:
            if page_num > chapter_end:
                break
        if page_num < chapter_start:
            continue
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

def get_actual_page_num(page_num, page_data):
    for actual_page_num, page in enumerate(page_data):
        actual_page_num += 1 # not zero-indexed
        page_marker = page["marker"]
        if str(page_num) == str(page_marker):
            return actual_page_num

def page_is_image_page(page):
    content = page["content"]
    page_is_image_page_condition = len(content.split("\n\n")) == 1 and ("{{FreedImg" in content or "[[File:" in content)
    return page_is_image_page_condition

def get_transclusion_tags(chapters, page_data, overall_chapter_num, filename, chapter=None, first_content_page=None, front_matter=False):
    # splits = []
    if front_matter:
        chapter_start = 1
        # first_chapter_page_num = chapters[0]["page_num"]
        # chapter_end = get_actual_page_num(first_chapter_page_num, page_data)
        chapter_end = first_content_page - 1
    else:
        if chapter:
            page_num = chapter["page_num"]
            actual_page_num = get_actual_page_num(page_num, page_data)
        else:
            actual_page_num = first_content_page
        chapter_start = actual_page_num
        try:
            chapter_end_page = chapters[overall_chapter_num + 1]["page_num"]
            chapter_end = get_actual_page_num(chapter_end_page, page_data) - 1
        # if not chapter_end:
        except IndexError:
            chapter_end = get_last_page(page_data, chapter_start)

    chapter_end = pop_pages_not_needing_proofreading(page_data, chapter_start, chapter_end)
    print(f"Okay so CHAPTER START = {chapter_start} CHAPTER END IS {chapter_end}")
    splits = get_page_tag_splits(page_data, chapter_start, chapter_end)

    number_of_splits = len(splits)

    chapter_transclusion_tags = []

    starting_page_num = chapter_start
    for page_num in range(chapter_start, chapter_end+1):
        if front_matter:
            page_num -= 1
        page = page_data[page_num]
        page_quality = page["page_quality"]
        if chapter_start == chapter_end:
            pages_tag = generate_transclusion_tag(filename, chapter_start, chapter_end)
            chapter_transclusion_tags.append(pages_tag)
            break
        if page_quality == "0":
            starting_page_num += 1
            continue
        next_page = page_data[page_num + 1]
        page_num += 1
        page_type = page["type"]
        next_page_quality = next_page["page_quality"]
        next_page_marker = next_page["marker"]
        next_page_content = next_page["content"]
        content = page["content"]
        page_marker = page["marker"]
            # continue

        # if page_quality == "0":
        #     # page_offset += 1
        #     # print(f"GOT HERE. Page offset: {page_offset} Page marker: {page_marker}")
        #     continue
        
        if front_matter:
            try:
                next_page_type = next_page["type"]
                if page_type == "toc" and next_page_type == "toc":
                    continue
                    # page_split = page_num
                    # pages_tag = generate_transclusion_tag(filename, starting_page_num, page_split)
                    # chapter_transclusion_tags.append(pages_tag)
                    # starting_page_num = page_split + 1
            except IndexError:
                pass
            page_split = page_num
            pages_tag = generate_transclusion_tag(filename, starting_page_num, page_split)
            chapter_transclusion_tags.append(pages_tag)
            starting_page_num = page_split + 1
            continue

        if page_type == "break" or page_num == chapter_end or next_page_quality == "0" or not next_page_marker.isdigit() or (front_matter and not page_type == "toc") or page_is_image_page(page) or page_is_image_page(next_page):
            page_split = page_num
            pages_tag = generate_transclusion_tag(filename, starting_page_num, page_split)
            chapter_transclusion_tags.append(pages_tag)
            starting_page_num = page_split + 1
            # chapter_transclusion_tags.append(f"<pages index=\"{filename}\" include={page_num} />")
        # elif page["page_quality"] == "0":
        #     if page_num == chapter_end:
        #         chapter_transclusion_tags.append(f"<pages index=\"{filename}\" include={page_num} />")
        #     else:
        #         continue
        else:
            continue
            # chapter_transclusion_tags.append(f"<pages index=\"{filename}\" include={page_num} />")

    # if number_of_splits == 1:
    #     page_split = splits[0]
    #     page_after_page_split = page_split + 1
    #     first_tag = generate_transclusion_tag(filename, chapter_start, page_split)
    #     last_tag = generate_transclusion_tag(filename, page_after_page_split, chapter_end)
    #     chapter_transclusion_tags.append(first_tag)
    #     chapter_transclusion_tags.append(last_tag)
    # elif number_of_splits > 1:
    #     pass # logic later
    # else:
    #     chapter_transclusion_tags = generate_transclusion_tag(filename, chapter_start, chapter_end)
    
    page_break = "{{page break|label=}}"

    if type(chapter_transclusion_tags) == list:
        chapter_transclusion_tags = f"\n{page_break}\n".join(chapter_transclusion_tags)

    return chapter_transclusion_tags

def transclude_chapters(chapters, page_data, page_offset, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort, filename, advertising_is_transcluded):
    number_of_chapters = len(chapters)
    for overall_chapter_num, chapter in enumerate(chapters):
        title_display = f"[[../|{title}]]" # for now, would change if the chapter is a subsubsection
        previous_chapter_display, next_chapter_display = generate_chapter_links(overall_chapter_num, chapter, chapters)
        chapter_transclusion_tags = get_transclusion_tags(chapters, page_data, overall_chapter_num, filename, chapter)

        chapter_name = chapter["title"]
        chapter_num = chapter["chapter_num"]
        chapter_prefix = chapter["prefix"]
        chapter_has_references = chapter["refs"]

        smallrefs = ""
        if chapter_has_references:
            smallrefs = "\n\n{{smallrefs}}"

        if not chapter_prefix and chapter_num:
            chapter_prefix = "Chapter"
        chapter_internal_name = f"{chapter_prefix} {chapter_num}"
        if not chapter_prefix and not chapter_num:
            chapter_internal_name = chapter_name
        if chapter_name == None:
            chapter_name = chapter_internal_name

        # if chapter_name == title:
        #     chapter_internal_name = "main content chapter"

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

{chapter_transclusion_tags}{smallrefs}"""
        # print(chapter_text)

        if chapter_name == chapter_internal_name:
            edit_summary = f"Transcluding {chapter_name}..."
        elif chapter_name == title and number_of_chapters < 4:
            edit_summary = f"Transcluding {chapter_name} (main content chapter)..."
        elif chapter_name == "Advertisements" and not advertising_is_transcluded:
            print_in_yellow("Advertising not proofread. Skipping advertisement chapter transclusion...")
            continue
        else:
            edit_summary = f"Transcluding {chapter_name} ({chapter_internal_name})..."
        print(chapter_text)
        save_page(chapter_page, site, chapter_text, edit_summary, transcription_page_title)

def generate_defaultsort_tag(mainspace_work_title):
    bad_prefixes = [
        "A ",
        "An ",
        "The ",
    ]
    for prefix in bad_prefixes:
        if mainspace_work_title.startswith(prefix):
            defaultsort_title = mainspace_work_title[len(prefix):]
            defaultsort = f"{{{{DEFAULTSORT:{defaultsort_title}}}}}"
            return defaultsort
    return ""

def get_first_content_page(page_data): # if there's no chapters in the book
    for page_num, page in enumerate(page_data):
        page_num += 1
        if page["type"] == "begin":
            return page_num

def check_if_advertising_transcluded(page_data):
    for page in page_data:
        page_quality = page["page_quality"]
        page_marker = page["marker"]
        if page_quality == "i" and (page_marker == "ad" or page_marker == "adv"):
            return False
    return True


# def is_PD_old(death_year, current_year):

def generate_copyright_template(year, author_death_year, current_year):
    if year < 1928:
        if (current_year - author_death_year) >= 101:
            template_name = "PD-old"
        else:
            template_name = f"PD-US|{author_death_year}"
    elif year < 1964:
        template_name = f"PD-US-not-renewed|pubyear={year}|{author_death_year}"
    elif year < 1978:
        template_name = f"PD-US-no-notice|{author_death_year}"
    elif year < 1989:
        template_name = f"PD-US-no-notice-post-1977|{author_death_year}"
    return template_name

def transclude_pages(chapters, page_data, first_page, mainspace_work_title, title, author_WS_name, year, filename, cover_filename, author_death_year, transcription_page_title, original_year, work_type_name, genre_name, country, toc_is_auxiliary, advertising_is_transcluded, current_year, transcription_text):
    # author_death_year, transcription_page_title
    site = pywikibot.Site('en', 'wikisource')
    # transclude front matter page
    front_matter_page = pywikibot.Page(site, mainspace_work_title)
    page_offset = first_page - 1

    # chapter_names = list(chapters.keys())
    # chapter_page_nums = list(chapters.values())
    if len(chapters) > 0:
        first_chapter = chapters[0]
        first_chapter_name = first_chapter["title"]
        first_chapter_page_num = first_chapter["page_num"]
        first_content_page = first_chapter_page_num + page_offset
        first_chapter_prefix = first_chapter["prefix"]
        if not first_chapter_prefix:
            first_chapter_prefix = "Chapter"
        first_chapter_num = 1
        if first_chapter["chapter_num"] == None:
            first_chapter_num = None
            first_chapter_display = f"[[/{first_chapter_name}/]]"
        elif first_chapter_name == None:
            first_chapter_display = f"[[/{first_chapter_prefix} {first_chapter_num}/]]"
        else:
            first_chapter_display = f"[[/{first_chapter_prefix} {first_chapter_num}|{first_chapter_name}]]"
    else:
        first_content_page = get_first_content_page(page_data)
        first_chapter_display = ""
    print("First content page:", first_content_page)


    if "(" in author_WS_name:
        override_author = "| override_author = "
        author_header_display = f"{override_author}[[Author:{author_WS_name}|]]"
    else:
        author_header_display = author_WS_name # for now. There will be logic here later.
    defaultsort = generate_defaultsort_tag(mainspace_work_title) # for now. There will be logic here later.
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

    page_tags = get_transclusion_tags(chapters, page_data, -1, filename, first_content_page=first_content_page, front_matter=True)

    page_break = "{{page break|label=}}"
    # page_tags = f"\n{page_break}\n".join(pages_tags)

    if len(chapters) == 0:
        page_tags += f"\n{page_break}\n" + get_transclusion_tags(chapters, page_data, 0, filename, first_content_page=first_content_page)

    aux_toc = ""

    if toc_is_auxiliary:
        aux_toc = f"\n\n{{{{{mainspace_work_title}/TOC}}}}"

    hidden_export_toc = ""

    if chapters:
        if chapters[-1]["title"] == "Advertisements" and advertising_is_transcluded:
            hidden_export_toc = """
{{hidden export TOC|
* [[/Advertisements/]]
}}"""


    copyright_template = generate_copyright_template(year, author_death_year, current_year) # for now, some logic later
    # additional_copyright_parameters = f"|{author_death_year}" # for now, some logic later

    # categories = ["Ready for export"] # for now, some logic later
    categories = []

    era_category = generate_era_category(original_year)
    categories.append(era_category)

    type_category = generate_type_category(work_type_name, country)
    categories.append(type_category)

    if genre_name:
        genre_categories = generate_genre_categories(genre_name, work_type_name)
        categories += genre_categories




    categories.sort()

    categories_text = []

    for category in categories:
        if category != None:
            categories_text.append(f"[[Category:{category}]]")
    if len(categories) > 0:
        categories_text = "\n\n" + "\n".join(categories_text)
    else:
        categories_text = ""
    
    if "(" in mainspace_work_title:
        parentheses_contents_index = mainspace_work_title.index("(")
        parentheses_contents = mainspace_work_title[parentheses_contents_index:]
        if has_digits(parentheses_contents):
            categories_text = ""

    front_matter_footer = f"""


{{{{authority control}}}}
{{{{{copyright_template}}}}}{categories_text}"""

    smallrefs = ""
    
    if len(chapters) == 0 and "</ref>" in transcription_text:
        smallrefs = "\n\n{{smallrefs}}"

    front_matter_text = front_matter_header + page_tags + aux_toc + hidden_export_toc + smallrefs + front_matter_footer

    print(front_matter_text)

    save_page(front_matter_page, site, front_matter_text, "Transcluding front matter...", transcription_page_title)

    if len(chapters) > 0:
        transclude_chapters(chapters, page_data, page_offset, title, mainspace_work_title, site, transcription_page_title, author_header_display, defaultsort, filename, advertising_is_transcluded)