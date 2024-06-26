# WS_collection

import pywikibot
import re
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from handle_wikidata import get_value_from_property, get_author_death_year, get_wikidata_item_from_wikisource
from edit_mw import save_page, get_english_plural, has_digits, linkify, get_title_hierarchy, get_current_pd_cutoff_year
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
        if genre == "adventure":
            if work_type_name == "novel":
                category = f"Adventure novels"
        if genre == "alternate":
            category = "Alternate history"
        if genre == "autobiography":
            category = "Autobiographies"
        if genre == "biography":
            category = "Biographies"
        elif genre == "captivity":
            category = "Captivity narratives"
        if genre == "children's" or genre == "children":
            category = "Children's books"
        if genre == "gen" or genre == "genealogy":
            category = ["Genealogy", "Non-fiction books"]
        elif genre == "historical":
            if work_type_name == "novel":
                category = f"Historical fiction novels"
            else:
                category = f"Historical {work_type_plural}"
        elif genre == "mystery":
            category = "Mystery novels"
        elif genre == "nature":
            category = "Nature"
        elif genre == "nonfiction":
            category = "Non-fiction books"
        elif genre == "Christian":
            category = "Christian literature"
        elif genre == "satire":
            if work_type_name == "novel":
                category = "Satirical novels"
        elif genre == "western":
            category = "Western fiction"
        if type(category) == str:
            categories.append(category)
        else:
            categories += category
    return categories

def check_if_parts_exist(transcription_text):
    if "/bk/" in transcription_text or "/pt/" in transcription_text or "part-header" in transcription_text:
        return True

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
            demonym = "French"
            process_break()
    else:
        print_in_red(f"No demonym found for {country}.")
        process_break()

    if work_type_name == "work":
        type_category = f"{demonym} literature"
    else:
        work_type_plural = get_english_plural(work_type_name)
        type_category = f"{demonym} {work_type_plural}"

    if work_type_name == "ssa" or work_type_name == "short story anthology":
        type_category = "Anthologies of short stories"
    if work_type_name == "ssc" or work_type_name == "short story collection":
        type_category = "Collections of short stories"
    elif work_type_name == "pc" or work_type_name == "poetry collection":
        type_category = "Collections of poetry"
    if work_type_name == "pa" or work_type_name == "poetry anthology":
        type_category = "Anthologies of poetry"
    elif work_type_name == "ec" or work_type_name == "essay collection":
        type_category = "Collections of essays"
    if work_type_name == "ea" or work_type_name == "essay anthology":
        type_category = "Anthologies of essays"
    elif work_type_name == "diary":
        type_category = "Journals"
    
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

def generate_chapter_link(chapters, chapter_num_zero_indexed, chapters_are_subpages_of_parts, overarching_chapter, work_type_name="novel"):
    chapter = chapters[chapter_num_zero_indexed]
    chapter_num = chapter["chapter_num"]
    chapter_name = chapter["title"]
    chapter_prefix = chapter["prefix"]
    chapter_type = chapter["type"]
    part_num = chapter["part_num"]
    if not chapter_prefix:
        chapter_prefix = "Chapter"
    chapter_internal_name = f"{chapter_prefix} {chapter_num}"

    if chapter_type == "part":
        chapter_internal_name = f"{chapter_prefix} {part_num}"
        part_title_is_also_a_chapter_title = check_if_part_title_is_also_a_chapter_title(chapter_name, chapters)

        if part_title_is_also_a_chapter_title and "collection" in work_type_name:
            # print(f"GOTHERE {part_title_is_also_a_chapter_title}")
            # exit()
            chapter_name = f"{chapter_name} (part)"
    
    dots_to_chapter = "../"
    overarching_chapter_prefix = overarching_chapter["prefix"]
    if (chapter_prefix == "Book" or chapter_prefix == "Part") and chapters_are_subpages_of_parts:
        dots_to_chapter = "../../"
    if (overarching_chapter_prefix == "Book" or overarching_chapter_prefix == "Part") and chapters_are_subpages_of_parts:
        if chapter_num == 1:
            dots_to_chapter = "/"
        else:
            dots_to_chapter = f"../{overarching_chapter_prefix} {part_num}/{chapter_internal_name}|{chapter_internal_name}"

    if len(dots_to_chapter) > 10: # lazy solution
        chapter_link = linkify(dots_to_chapter)
    elif chapter_num == None or chapter_type == "short story" or chapter_type == "poem" or chapter_type == "essay":
        chapter_link = f"[[{dots_to_chapter}{chapter_name}/]]"
    elif chapter_name == None:
        chapter_link = f"[[{dots_to_chapter}{chapter_internal_name}/]]"
    else:
        chapter_link = f"[[{dots_to_chapter}{chapter_internal_name}/]]"


    return chapter_link


def generate_chapter_links(overall_chapter_num, chapter, chapters, chapters_are_subpages_of_parts):
    dots_to_front_matter = "../"
    if chapters_are_subpages_of_parts:
        dots_to_front_matter = "../../"
    
    front_matter_link = f"[[../|Front matter]]"
    return_to_front_matter_link = f"[[{dots_to_front_matter}|Return to front matter]]"
    
    chapter_name = chapter["title"]
    chapter_prefix = chapter["prefix"]

    if overall_chapter_num == -1: # front matter
        previous_chapter_link = ""
    else:
    # try:
        previous_chapter_num_zero_indexed = overall_chapter_num - 1

        previous_chapter_link = generate_chapter_link(chapters, previous_chapter_num_zero_indexed, chapters_are_subpages_of_parts, chapter)
        if previous_chapter_num_zero_indexed == -1:
            previous_chapter_link = front_matter_link


    next_chapter_num_zero_indexed = overall_chapter_num + 1

    try:
        next_chapter_link = generate_chapter_link(chapters, next_chapter_num_zero_indexed, chapters_are_subpages_of_parts, chapter)
    except IndexError:
        next_chapter_link = return_to_front_matter_link

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
    if '"' in filename:
        filename = "'" + filename + "'"
    else:
        filename = '"' + filename + '"'

    if start_page != end_page:
        transclusion_tag = f"<pages index={filename} from={start_page} to={end_page} />"
    else:
        transclusion_tag = f"<pages index={filename} include={start_page} />"
    return transclusion_tag

def get_actual_page_num(page_num, page_data, chapter_format=None):
    for actual_page_num, page in enumerate(page_data):
        actual_page_num += 1 # not zero-indexed
        page_marker = page["marker"]
        page_format = page["format"]
        if str(page_num) == str(page_marker):
            if chapter_format:
                if page_format == chapter_format:
                    return actual_page_num
            else:
                return actual_page_num

def page_is_image_page(page):
    content = page["content"]
    page_is_image_page_condition = len(content.split("\n\n")) == 1 and ("{{FreedImg" in content or "[[File:" in content)
    return page_is_image_page_condition

def get_last_roman_page_num(page_data):
    iterating_roman_pages = False
    for page_num, page in enumerate(page_data):
        page_num += 1
        page_format = page["format"]
        if page_format == "roman":
            iterating_roman_pages = True

        if iterating_roman_pages and page_format != "roman":
            return page_num - 1

def get_transclusion_tags(chapters, page_data, overall_chapter_num, filename, chapter=None, first_content_page=None, front_matter=False, chapter_format=None, transclusion_is_sectioned=False):
    # splits = []
    if front_matter:
        chapter_start = 1
        # first_chapter_page_num = chapters[0]["page_num"]
        # chapter_end = get_actual_page_num(first_chapter_page_num, page_data)
        chapter_end = first_content_page - 1
    else:
        if chapter:
            print_in_yellow("if chapter:")
            page_num = chapter["page_num"]
            actual_page_num = get_actual_page_num(page_num, page_data, chapter_format=chapter_format)
        else:
            print_in_yellow("if chapter: else >")
            actual_page_num = first_content_page
        chapter_start = actual_page_num
        try:
            next_chapter = chapters[overall_chapter_num + 1]
            next_chapter_format = next_chapter["format"]
            if chapter_format:
                if chapter_format != next_chapter_format:
                    chapter_end = get_last_roman_page_num(page_data)
                else:
                    chapter_end_page = next_chapter["page_num"]
                    chapter_end = get_actual_page_num(chapter_end_page, page_data, chapter_format=chapter_format) - 1
                try:
                    next_chapter_sectioned_at_beginning = next_chapter["sectioned_at_beginning"]
                    if transclusion_is_sectioned and not next_chapter_sectioned_at_beginning:
                        chapter_end += 1
                except:
                    pass
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
        print(f"We're at {page_num}")
        # if front_matter:
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
        
        page_type_condition = (page_type == "break")
        if page_type == "break" or page_num == chapter_end or next_page_quality == "0" or not next_page_marker.isdigit() or (front_matter and not page_type == "toc") or page_is_image_page(page) or page_is_image_page(next_page):
            print(f"Got here and page_type == break is {page_type_condition}")
            page_split = page_num
            pages_tag = generate_transclusion_tag(filename, starting_page_num, page_split)
            chapter_transclusion_tags.append(pages_tag)
            starting_page_num = page_split + 1
            if (next_page_marker == "ad" and not page_marker == "ad") or page_num == chapter_end:
                break
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

def generate_chapter_categories(chapter):
    categories = []
    chapter_type = chapter["type"]
    if chapter_type == "short story" or chapter_type == "ss":
        categories.append("Short stories")
    elif chapter_type == "poem" or chapter_type == "po":
        categories.append("Poems")
    elif chapter_type == "essay" or chapter_type == "es":
        categories.append("Essays")
    
    if len(categories) > 0:
        categories = "\n\n[[Category:" + "]]\n[[Category:".join(categories) + "]]"
    else:
        categories = ""

    return categories


def transclude_chapters(chapters, page_data, page_offset, title, mainspace_work_title, site, transcription_page_title, author_header_display, translator_display, defaultsort, filename, advertising_is_transcluded, editor_display, chapters_are_subpages_of_parts, work_type_name, transclusion_is_sectioned, original_year, current_year):
    number_of_chapters = len(chapters)
    part_prefix = None
    for overall_chapter_num, chapter in enumerate(chapters):
        chapter_prefix = chapter["prefix"]
        part_num = chapter["part_num"]
        copyright_template = ""
        if chapter_prefix == "Book" or chapter_prefix == "Part":
            part_prefix = chapter_prefix
        dots_to_front_matter = "../"
        if chapter_prefix == "Chapter" and chapters_are_subpages_of_parts:
            dots_to_front_matter = "../../"
        if not chapter_prefix:
            chapter_prefix = "Chapter"
        title_display = f"[[{dots_to_front_matter}|{title}]]" # for now, would change if the chapter is a subsubsection
        previous_chapter_display, next_chapter_display = generate_chapter_links(overall_chapter_num, chapter, chapters, chapters_are_subpages_of_parts)
        chapter_format = chapter["format"]
        chapter_transclusion_tags = get_transclusion_tags(chapters, page_data, overall_chapter_num, filename, chapter, transclusion_is_sectioned=transclusion_is_sectioned, chapter_format=chapter_format)
        chapter_name = chapter["title"]
        chapter_num = chapter["chapter_num"]
        chapter_type = chapter["type"]
        section_translator = chapter["translator"]
        section_translator_display = ""
        if section_translator:
            section_translator_display = f"""
 | section-translator = {section_translator}"""
        else:
            section_translator_display = ""

        if chapter_type == "front-matter chapter":
            continue
    
        chapter_has_references = chapter["refs"]
        related_author = chapter["related_author"]
        
    
        smallrefs = ""
        authority_control = ""
        if chapter_has_references:
            smallrefs = "\n\n{{smallrefs}}"
        if chapter_type == "ss":
            chapter_type = "short story"
        if chapter_type == "po":
            chapter_type = "poem"
        if chapter_type == "es":
            chapter_type = "essay"

        if related_author:
            related_author_display = f"""
 | related_author = {related_author}"""
        else:
            related_author_display = ""

        contributor = chapter["contributor"]

        if contributor:
            contributor_display = f"""
 | contributor = {contributor}"""
        else:
            contributor_display = ""

        if chapter_type == "short story" or chapter_type == "poem" or chapter_type == "essay":
            chapter_internal_name = chapter_name
            authority_control = "\n\n\n{{authority control}}"
            if "anthology" in work_type_name:
                contributor = chapter["contributor"]
                subwork_author_item = get_wikidata_item_from_wikisource("Author:"+contributor)
                subwork_author_death_year = get_author_death_year(subwork_author_item)
                copyright_template = "\n{{" + generate_copyright_template(original_year, subwork_author_death_year, current_year) + "}}"
        else:
            if chapter_type == "part":
                chapter_internal_name = f"{chapter_prefix} {part_num}"
            else:
                chapter_internal_name = f"{chapter_prefix} {chapter_num}"
            
        if not chapter_prefix and chapter_num and not authority_control:
            chapter_prefix = "Chapter"
        if not chapter_prefix and not chapter_num:
            chapter_internal_name = chapter_name
        if chapter_name == None:
            chapter_name = chapter_internal_name
        
        if chapter_type == "part" and "collection" in work_type_name:
            chapter_internal_name = chapter_name
            part_title_is_also_a_chapter_title = check_if_part_title_is_also_a_chapter_title(chapter_internal_name, chapters)

            if part_title_is_also_a_chapter_title:
                chapter_internal_name = f"{chapter_internal_name} (part)"
        
        if chapter_internal_name == chapter_name:
            defaultsort = generate_defaultsort_tag(chapter_name)
        else:
            defaultsort = generate_defaultsort_tag(mainspace_work_title)
        
        if chapter_prefix == "Chapter" and chapters_are_subpages_of_parts:
            chapter_internal_name = f"{part_prefix} {part_num}/Chapter {chapter_num}"
            print("WE GOT HERE YAKNOW")


            # chapter_name = f"Chapter {chapter_num}"
        # if chapter_name == title:
        #     chapter_internal_name = "main content chapter"

        chapter_categories = generate_chapter_categories(chapter)

        if chapter_internal_name == "Chapter None":
            chapter_internal_name = chapter_name

        if transclusion_is_sectioned:
            section_name = chapter["section_name"]
            chapter_transclusion_tags = chapter_transclusion_tags.replace(" />", f" onlysection=\"{section_name}\" />")

        chapter_page_title = f"{mainspace_work_title}/{chapter_internal_name}"
        chapter_page = pywikibot.Page(site, chapter_page_title)
        defaultsort = ""
        chapter_text = f"""{{{{header
 | title      = {title_display}
 | author     = {author_header_display}{translator_display}
 | section    = {chapter_name}
 | previous   = {previous_chapter_display}
 | next       = {next_chapter_display}{editor_display}{contributor_display}{section_translator_display}{related_author_display}
 | notes      = 
}}}}{defaultsort}

{chapter_transclusion_tags}{smallrefs}{authority_control}{copyright_template}{chapter_categories}"""
        # print(chapter_text)

        if chapter_name == chapter_internal_name:
            edit_summary = f"Transcluding {chapter_name}..."
        elif chapter_name == title and number_of_chapters < 4:
            edit_summary = f"Transcluding {chapter_name} (main content chapter)..."
        elif (chapter_name == "Advertisements" and not advertising_is_transcluded) or not chapter_transclusion_tags:
            print_in_yellow("Advertising not proofread. Skipping advertisement chapter transclusion...")
            continue
        else:
            edit_summary = f"Transcluding {chapter_name} ({chapter_internal_name})..."
        
        print(chapter_page_title)
        print(chapter_text)
        save_page(chapter_page, site, chapter_text, edit_summary, transcription_page_title)

def generate_defaultsort_tag(title, mainspace_work_title=False, for_logic=False):
    # defaultsort = ""
    # return defaultsort
    bad_prefixes = [
        "A ",
        "An ",
        "The ",
    ]

    # defaultsorting against ""
    # if title.startswith('"') and title.endswith('"'):
    #     title = title[1:-1]
    # elif title.startswith('"'):
    #     title = title[1:]
    title = title.replace("\"", "")
    
    for prefix in bad_prefixes:
        if title.startswith(prefix):
            defaultsort_title = title[len(prefix):]
            defaultsort = f"{{{{DEFAULTSORT:{defaultsort_title}}}}}"
            return defaultsort
        
    if title[:-1].isdigit() and mainspace_work_title and not for_logic: # if it's a chapter number
        return ""
    elif mainspace_work_title or for_logic:
        return f"{{{{DEFAULTSORT:{title}}}}}"
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
        if (page_quality == "i" or page_quality == "1" or page_quality == "0") and (page_marker == "ad" or page_marker == "adv"):
            return False
    return True

def determine_if_refs_in_front_matter(page_data):
    for page in page_data:
        footer = page["footer"]
        content = page["content"]
        if "/begin/" in content:
            return False
        if "{{smallrefs}}" in footer:
            return True
# def is_PD_old(death_year, current_year):

def check_if_part_title_is_also_a_chapter_title(part_title, chapters):
    for chapter in chapters:
        chapter_title = chapter["title"]
        chapter_type = chapter["type"]
        if part_title == chapter_title and chapter_type != "part":
            return True
    return False

def generate_copyright_template(year, author_death_year, current_year):
    if year <= get_current_pd_cutoff_year():
        if author_death_year:
            if (current_year - author_death_year) >= 101:
                template_name = "PD-old"
            else:
                template_name = f"PD-US|{author_death_year}"
        else:
            # PD-old-assumed, if older than 1874
            if year > (current_year - 151):
                template_name = "PD-old"
            else:
                template_name = "PD-US"
    elif year < 1964:
        template_name = f"PD-US-not-renewed|pubyear={year}|{author_death_year}"
    elif year < 1978:
        template_name = f"PD-US-no-notice|{author_death_year}"
    elif year < 1989:
        template_name = f"PD-US-no-notice-post-1977|{author_death_year}"
    return template_name

def transclude_pages(chapters, page_data, first_page, mainspace_work_title, title, author_WS_name, year, filename, cover_filename, author_death_year, transcription_page_title, original_year, work_type_name, genre_name, country, toc_is_auxiliary, advertising_is_transcluded, current_year, related_author, series_name, editor, translator, derivative_work, transcription_text, chapters_are_subpages_of_parts, transclusion_is_sectioned):
    # author_death_year, transcription_page_title
    site = pywikibot.Site('en', 'wikisource')
    # transclude front matter page
    front_matter_page = pywikibot.Page(site, mainspace_work_title)
    page_offset = first_page - 1

    # chapter_names = list(chapters.keys())
    # chapter_page_nums = list(chapters.values())
    first_content_page = get_first_content_page(page_data)
    if len(chapters) > 0:
        first_chapter = chapters[0]
        first_chapter_name = first_chapter["title"]
        first_chapter_page_num = first_chapter["page_num"]
        # first_content_page = first_chapter_page_num + page_offset
        first_chapter_prefix = first_chapter["prefix"]
        if not first_chapter_prefix:
            first_chapter_prefix = "Chapter"
        first_chapter_num = 1
        first_chapter_type = first_chapter["type"]
        if (first_chapter["chapter_num"] == None and first_chapter["type"] != "part") or first_chapter_type == "short story" or first_chapter_type == "poem" or first_chapter_type == "essay":
            first_chapter_num = None
            first_chapter_display = f"[[/{first_chapter_name}/]]"
        elif first_chapter_name == None:
            first_chapter_display = f"[[/{first_chapter_prefix} {first_chapter_num}/]]"
        else:
            first_chapter_display = f"[[/{first_chapter_prefix} {first_chapter_num}/]]"
    else:
        first_chapter_display = ""
    print("First content page:", first_content_page)


    if "(" in author_WS_name:
        override_author = "| override_author = "
        author_header_display = f"{override_author}[[Author:{author_WS_name}|]]"
    else:
        author_header_display = author_WS_name # for now. There will be logic here later.
    defaultsort = generate_defaultsort_tag(mainspace_work_title, mainspace_work_title=True)
    # disambiguation_pointer = f"{{{{other versions|{title}}}}}\n" # for now. There will be logic here later.
    title_hierarchy = get_title_hierarchy(mainspace_work_title, translator)
    print(title_hierarchy)
    if title_hierarchy == "disambig":
        disambiguation_pointer = f"{{{{similar|{title}}}}}\n"
    elif title_hierarchy == "version":
        disambiguation_pointer = f"{{{{other versions|{title}}}}}"
    else:
        disambiguation_pointer = ""
    # Hierarchy: disambig > work > version
    # IDEA: Go to version_item, then check base_work for a versions page on WS. If it doesn't have one, then check for disambig.

    if cover_filename:
        cover_display = f"""
 | cover      = {cover_filename}"""
    else:
        cover_display = ""

    """
 | year        = 1915
 | portal      = Biographical film/Films with historical settings/Silent film
 | related_author = Abraham Lincoln
 """

    if related_author:
        related_author_display = f"""
 | related_author = {related_author}"""
    else:
        related_author_display = ""

    if series_name:
        if "Portal:" in series_name:
            series_name = series_name.replace("Portal:", "")
        portal_display = f"""
 | portal     = {series_name}"""
    else:
        portal_display = ""
    
    if editor:
        editor_display = f"""
 | editor     = {editor}"""
    else:
        editor_display = ""

    if translator:
        translator_display = f"""
 | translator = {translator}"""
    else:
        translator_display = ""

    defaultsort = ""

    front_matter_header = f"""{disambiguation_pointer}{{{{header
 | title      = {title}
 | author     = {author_header_display}{translator_display}
 | section    = 
 | previous   = 
 | next       = {first_chapter_display}
 | year       = {year}{cover_display}{portal_display}{related_author_display}{editor_display}
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


    copyright_template = generate_copyright_template(original_year, author_death_year, current_year) # for now, some logic later
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

    if derivative_work: # FOR NOW, until it gets more complicated
        categories.append("Novels adapted into films")



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

    

    
    if len(chapters) == 0 and "</ref>" in transcription_text:
        smallrefs = "\n{{smallrefs}}"
    else:
        # refs_are_in_front_matter = determine_if_refs_in_front_matter(page_data)
        # if refs_are_in_front_matter:
        #     smallrefs = "\n{{smallrefs}}"
        # else:
        #     smallrefs = ""
        smallrefs = "" # FOR NOW

    front_matter_footer = f"""

{smallrefs}
{{{{authority control}}}}
{{{{{copyright_template}}}}}{categories_text}"""

    front_matter_text = front_matter_header + page_tags + aux_toc + hidden_export_toc + front_matter_footer

    print(front_matter_text)

    save_page(front_matter_page, site, front_matter_text, "Transcluding front matter...", transcription_page_title)

    if len(chapters) > 0:
        transclude_chapters(chapters, page_data, page_offset, title, mainspace_work_title, site, transcription_page_title, author_header_display, translator_display, defaultsort, filename, advertising_is_transcluded, editor_display, chapters_are_subpages_of_parts, work_type_name, transclusion_is_sectioned, original_year, current_year)