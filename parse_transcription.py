# WS_collection

import pywikibot
import re
import roman
import inflect

from cleanup import remove_triple_newlines
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page
from handle_title_case import convert_to_title_case
from handle_projectfiles import write_to_json_file, get_json_data
from handle_wikisource_conf import get_regex_match
from handle_commons import get_image_filename
# from handle_pages import get_marker_from_page_num
from handle_transclusion import get_last_page


# DO THIS TIME: /i// tag.
#: '/i// handle
#: /i//'.'.'.'//i/ handle

# DO NEXT TIME THERE'S A DEDICATION WITH AN AUTHOR: dedic tag to be used for the Wikidata item. OR, detect if the marker is "ded", and if there's only one author item. If so, use that item. Dedicated to property: P825
# DO NEXT TIME: {{lps|link=Sense and Sensibility|pre=Sense and|post=Sensibility|lq="|rq="}}

"""
{{c|{{larger|CONTENTS}}}}
{{TOC begin|sc=yes|max-width=25em}}
{{TOC row 1-1-1|{{x-smaller|CHAPTER}}||{{x-smaller|PAGE}}}}
{{TOC row 1-1-1|{{fine|I}}|{{fine|[[The Blind Man's Eyes (July 1916)/Chapter 1|A Financier Dies]]}}|{{fine|1}}}}
{{TOC end}}
"""

basic_elements = {
    "b2": "bar|2",
    "brp": "£",
    "bt": "***|char=·",
    "d": "dhr",
    "end": "The End",
    "fin": "Finis",
    "n": "nop",
    "peh": "peh",
    "st": "***",
    "-": "<spl>", # for handling split between tags
}

block_elements = {
    # sizes
    "xxxxlb": "xxxx-larger block",
    "xxxlb": "xxx-larger block",
    "xxlb": "xx-larger block",
    "xlb": "x-larger block",
    "lb": "larger block",
    "fb": "fine block",
    "sb": "smaller block",
    "xsb": "x-smaller block",
    "xxsb": "xx-smaller block",

    # fonts
    "bb": "bold block",
    "blb": "blackletter block",
    "cb": "cursive block",
    "ib": "italic block",
    "scb": "small-caps block",

    # alignment
    "bc": "block center",
    "bq": "blockquote",
    "hi": "hanging indent",

    # semantic
    "let": "letter",
}

named_chapter_pattern = r"\/ch\/.+?\n\n"
named_chapter_pattern_with_settings = r"\/ch\/.+?\/.+?\n\n"
empty_chapter_pattern = r"\/ch\/\n\n"
chapter_pattern_for_poetry_collection = r"(\/ch\/.+?\n\n\/po.+?\n)"

chapter_pattern = rf"({named_chapter_pattern}|{named_chapter_pattern_with_settings}|{empty_chapter_pattern})"


chapter_tags = [
    "bibl",
    "bk",
    "ch",
    "chh",
    "chrn",
    "concl",
    "contch",
    "dedch",
    "epi",
    "fwd",
    "int",
    "intr",
    "inty",
    "pref",
    "prol",
    "pt",
    "refch",
]








###################### main logic ######################

def string_not_in_content(content, string, action):
    is_string = False
    if type(string) == str:
        string = [string,]
        is_string = True
    for item in string:
        if is_string:
            string = item
        if item in content:
            print(f"{string} found in content. {action}...")
            return False
        # else:
            # return True
    return True

def strings_not_in_content(content, list, message):
    for tag in list:
        tag = get_plain_tag(tag)
        if string_not_in_content(content, tag, f"{message} {tag}"):
            continue
        else:
            return False
    return True

def get_bare_title(mainspace_work_title):
    return mainspace_work_title.split(" (")[0]

def get_marker_from_page_num(expected_page_num, page_data):
    for page_num, page in enumerate(page_data):
        page_num += 1
        if page_num == expected_page_num:
            return page["marker"]


## TAGS ##

def get_plain_tag(abbreviation):
    if "/" not in abbreviation:
        return f"/{abbreviation}/"
    else:
        return abbreviation

def get_noparams_start_tag(abbreviation):
    if abbreviation.startswith("/") and abbreviation.endswith("/"):
        return f"{abbreviation}/"
    else:
        return f"/{abbreviation}//"
    
def get_end_tag(abbreviation):
    if abbreviation.startswith("/") and abbreviation.endswith("/"):
        return f"/{abbreviation}"
    else:
        return f"//{abbreviation}/"


## PARSE ##

def get_string_from_lines(content, strings):
    content_split_lines = content.split("\n")
    
    if type(strings) == str:
        strings = [strings,]

    list_of_tags = []

    for string in strings:
        string = get_plain_tag(string)
        list_of_tags.append(string)

    matches = {}

    for line_num, line in enumerate(content_split_lines):
        for tag in list_of_tags:
            if tag in line:
                matches[line_num] = line
    
    return matches

def replace_line(content, replacement, line_num):
    content_split_lines = content.split("\n")
    content_split_lines[line_num] = replacement
    return "\n".join(content_split_lines)


def format_form_tag(row, replacements):
    for tag, replacement in replacements.items():
        print(replacement)
        tag = get_plain_tag(tag)
        print(f"Tag: {tag} Replacement: {replacement} Row: {row}")
        if replacement:
            replacement = str(replacement) # somehow not getting here as str sometimes
            row = row.replace(tag, replacement)
    
    row = row.replace("| ", "|")
    return row












###################### headers/footers ######################

def add_to_header(start_template, header):
    if header:
        return header + start_template + "\n"
    else:
        return start_template

def add_to_footer(end_template, footer):
    if footer:
        return end_template + "\n" + footer
    else:
        return end_template

def handle_block_continuations(page, tag, block_continuations, start_template, end_template, split_list=None):
    content = page["content"]
    header = page["header"]
    footer = page["footer"]
    start_tag = get_noparams_start_tag(tag)
    end_tag = get_end_tag(tag)
    while 1:
        if tag in block_continuations:
            print(f"Formatting continuation of {tag} in progress...")
            continuation_index = block_continuations[tag]
            
            # handle headers/footers

            if continuation_index == 0:
                footer = add_to_footer(end_template, footer)
                if tag != "toc":
                    content = content.replace(start_tag, start_template)
                block_continuations[tag] += 1
            else:
                header = add_to_header(start_template, header)
                if end_tag not in content:
                    footer = add_to_footer(end_template, footer)
                    block_continuations[tag] += 1
                else:
                    print(f"Formatting continuation of {tag} complete.")
                    if tag != "toc":
                        content = content.replace(end_tag, end_template, 1)
                    del block_continuations[tag]

            # handle content
            
            if split_list:
                content = split_list[continuation_index]
            
            break
        else:
            print(f"Formatting of {tag} continues across multiple pages. Handling...")
            if tag in content:
                block_continuations[tag] = 0

    page["content"] = content
    page["header"] = header
    page["footer"] = footer

    return block_continuations, page

def handle_inline_continuations(content, page, page_data, tag, continuation_prefix, continuation_param, inline_continuations):
    print(f"Handling inline continuation (tag: {tag}, prefix: {continuation_prefix}, param: {continuation_param})")

    start_tag = get_noparams_start_tag(tag)
    end_tag = get_end_tag(tag)

    if start_tag not in content or end_tag not in content:
        template_start = f"{{{{{continuation_prefix}"
        page_num = page["page_num"]
        marker = page["marker"]
        # marker = int(marker)
        page_num_zero_indexed = page_num - 1
        next_page = page_data[page_num_zero_indexed+1]
        next_page_content = next_page["content"]
        next_page_marker = next_page["marker"]
        previous_page = page_data[page_num_zero_indexed-1]
        previous_page_content = previous_page["content"]
        crosspage_start_pattern = rf"/{tag}//(.*?)$"
        crosspage_end_pattern = rf"^(.*?)//{tag}/"

        if end_tag not in content: # CHANGE TO IF NOT CLOSED
            crosspage_start = re.search(crosspage_start_pattern, content).group(1)
            crosspage_end = re.search(crosspage_end_pattern, next_page_content).group(1)
            full_phrase = f"{crosspage_start} {crosspage_end}"

            inline_continuation_data = {}
            inline_continuation_data["start"] = crosspage_start
            inline_continuation_data["end"] = crosspage_end

            inline_continuations.append(inline_continuation_data)
            # print(f"{inline_continuations} is inline continuations in the function")
        elif start_tag not in content:
            inline_continuation_data = inline_continuations[0]
            crosspage_start = inline_continuation_data["start"]
            crosspage_end = inline_continuation_data["end"]
            full_phrase = f"{crosspage_start} {crosspage_end}"

            inline_continuations.pop(0)
        
        template_end = f"|{continuation_param}={full_phrase}|pre={crosspage_start}|post={crosspage_end}}}}}"
        continuation_start_template = template_start + "s" + template_end
        continuation_end_template = template_start + "e" + template_end

        content = re.sub(crosspage_start_pattern, continuation_start_template, content)
        content = re.sub(crosspage_end_pattern, continuation_end_template, content)

    

    return content, inline_continuations








################### transclusion functions ###################

def generate_section_transclusion_start_tag(chapter_prefix, chapter):
    section_transclusion_name = chapter["section_name"]
    section_transclusion_tag = f"<*{section_transclusion_name}*>"

    return section_transclusion_tag

def generate_section_transclusion_end_tag(chapter_prefix, chapter):
    section_transclusion_name = chapter["section_name"]
    section_transclusion_tag = f"<*-{section_transclusion_name}-*>"

    return section_transclusion_tag

def add_section_transclusion_tags(page, chapters, overall_chapter_num):
    # Notes:
    #* THIS WILL ONLY WORK right now with single chapter switches on one page.
    #* It ONLY SUPPORTS the chaptered structure right now. Poetry collections later should modify this significantly

    if overall_chapter_num == 0:
        # if this is the front matter this isn't needed
        return page

    content = page["content"]

    overall_chapter_num_zero_indexed = overall_chapter_num - 1
    chapter = chapters[overall_chapter_num_zero_indexed]
    previous_chapter = chapters[overall_chapter_num_zero_indexed-1]
    chapter_prefix = chapter["prefix"]

    
    
    section_transclusion_start_tag = generate_section_transclusion_start_tag(chapter_prefix, chapter)


    section_transclusion_end_tag = generate_section_transclusion_end_tag(chapter_prefix, chapter)
    
    if ("ph|class=chapter" in content or "ph|class=part" in content) and overall_chapter_num != 1:
        previous_chapter_num = overall_chapter_num_zero_indexed

        if content.startswith("{{ph|class=chapter") or content.startswith("{{ph|class=part"):
            previous_chapter_start_tag = section_transclusion_start_tag
        else:
            previous_chapter_start_tag = generate_section_transclusion_start_tag(chapter_prefix, previous_chapter)
        # THIS HAS A PROBLEM, see https://en.wikisource.org/wiki/The_Strange_Case_of_Miss_Annie_Spragg/Chapter_13

        
            
        previous_chapter_end_tag = generate_section_transclusion_end_tag(chapter_prefix, previous_chapter)
        
        content = content.replace("\n{{ph|class=chapter", f"{previous_chapter_end_tag}{section_transclusion_start_tag}{{{{ph|class=chapter")
        content = content.replace("\n{{ph|class=part", f"{previous_chapter_end_tag}{section_transclusion_start_tag}{{{{ph|class=part")

        content = previous_chapter_start_tag + content + section_transclusion_end_tag
    else:
        content = section_transclusion_start_tag + content + section_transclusion_end_tag


    page["content"] = content
    
    return page






def handle_forced_page_breaks(page, page_break_string):
    content = page["content"]
    page_break_tag = get_plain_tag("pbr")
    
    # page_break_string = "<!-- page break after this page -->"

    if string_not_in_content(content, page_break_tag, "Handling forced page break"):
        return page

    content = content.replace(f"\n{page_break_tag}", f"\n{page_break_string}")
    page["type"] = "break"
    
    page["content"] = content
    return page











################ chapter/TOC functions ####################

def get_chapter_splice_points(text):
    pattern = r"/toc/(.+?)/"
    matches = re.findall(pattern, text)

    if not matches:
        # print("No roman numerals found.")
        return None

    result = []
    for match in matches:
        roman_numeral = match.upper()
        try:
            decimal_value = roman.fromRoman(roman_numeral)
            result.append(decimal_value)
            # print_in_green(f"Roman numeral found: {roman_numeral}")
        except roman.InvalidRomanNumeralError:
            print_in_yellow(f"{roman_numeral} is not a valid roman numeral.")

    return result

def determine_if_books_or_parts_exist(text):
    if "/bk/" in text or "/pt/" in text:
        return True
    return False

# def parse_chapter_settings(chapter_settings, chapter):
#     title_pattern = r"t=(.+?)"
#     if title_pattern:


def get_chapter_parameters(line):
    chapter_parameters = line.split("/")[1:] # because the first will always be '' which is useless
    
    number_of_parameters = len(chapter_parameters)

    if number_of_parameters == 2:
        chapter_tag = chapter_parameters[0]
        chapter_settings = None
        chapter_title = None
        # chapter_display_title = None
    else:
        chapter_tag = chapter_parameters[0]
        chapter_settings = chapter_parameters[1]
        chapter_settings = chapter_settings.split(",")
        chapter_title = chapter_parameters[2]
        if chapter_settings == "":
            chapter_settings = None
        if chapter_title == "":
            chapter_title = None

    chapter_parameters = {
        "chapter_tag": chapter_tag,
        "chapter_settings": chapter_settings,
        "chapter_title": chapter_title,
    }

    return chapter_parameters

def parse_chapter_settings(chapter_settings):
    if not chapter_settings:
        return None

    chapter_settings_data = {}

    # chapter_settings = chapter_settings.split(",")
    for setting in chapter_settings:
        if setting == "aux=y" or setting == "aux":
            chapter_settings_data["auxiliary"] = True
        if setting.startswith("i="):
            chapter_settings_data["header_invisible"] = setting.split("=")[1]
        if setting.startswith("flt="):
            chapter_settings_data["first_line_is_title"] = setting.split("=")[1]
        if setting.startswith("t="):
            chapter_settings_data["title"] = setting.split("=")[1]
        if "con=" in setting:
            chapter_settings_data["contributor"] = setting.split("=")[1]
        if "tr=" in setting:
            chapter_settings_data["translator"] = setting.split("=")[1]
        if "base=" in setting:
            chapter_settings_data["base_work_item"] = setting.split("=")[1]
        if "ty=" in setting:
            chapter_settings_data["type"] = setting.split("=")[1]
            if chapter_settings_data["type"] == "nam":
                chapter_settings_data["type"] = "non-work chapter"
            elif chapter_settings_data["type"] == "fm":
                chapter_settings_data["type"] = "front-matter chapter"
        if "rel=" in setting:
            chapter_settings_data["related_author"] = setting.split("=")[1]
        if "oy=" in setting:
            chapter_settings_data["original_year"] = int(setting.split("=")[1])

    return chapter_settings_data

def get_chapter_data(text, page_data, chapter_prefix, chapters_are_subpages_of_parts, work_title, chapter_type, work_type_name, force_chapter_numbers, part_prefix, transclusion_is_sectioned):
    print("Getting chapter data...")

    chapters_json_file = "chapter_data.json"
    chapters = get_json_data(chapters_json_file)
    try:
        if len(chapters) >= 0:
            print("Chapter data JSON found!")
            return chapters
    except TypeError:
        pass

    prefixless_chapter_titles = {
        "bibl": "Bibliography",
        "chrn": "Chronology",
        "concl": "Conclusion",
        "dedch": "Dedication",
        "epi": "Epilogue",
        "fwd": "Foreword",
        "int": "Introduction",
        "intr": "Introduction",
        "inty": "Introductory",
        "pref": "Preface",
        "prol": "Prologue",
        "refch": "References",
    }

    chapter_prefixes = {
        "bk": "Book",
        "ch": "Chapter",
        "pt": "Part",
    }
    
    parts_exist = determine_if_books_or_parts_exist(text)

    chapter_num = 0

    if parts_exist:
        part_num = 0
    else:
        part_num = None

    chapters = []

    first_chapter_tag_found = ""


    # Below for loop is for checking if chapters are in the work AT ALL
    for chapter_tag in chapter_tags:
        chapter_tag = get_plain_tag(chapter_tag)
        if chapter_tag in text:
            print_in_green(f"{chapter_tag} found in transcription text. Getting chapter data...")
            first_chapter_tag_found = chapter_tag
            break
    
    if not first_chapter_tag_found:
        print_in_yellow("No chapters found in transcription text. Assuming this is a front matter only work...")


    # {"prefix": "Chapter", "chapter_num": 3, "title": "IF KING ETHELRED OF ENGLAND HAD NOT MARRIED THE NORMAN EMMA", "display_title": "IF KING ETHELRED OF ENGLAND HAD NOT MARRIED THE NORMAN EMMA", "page_num": 30, "hidden": false, "refs": false, "part_num": null, "has_sections": false, "splice": false}

    previous_chapter = None
    section_tag = get_plain_tag("sec")
    chapter_splice_points = get_chapter_splice_points(text)

    skip_chapter_because_of_chapter_half = False

    for page in page_data:
        page_num = page["marker"]
        page_format = page["format"]

        chapter = {}

        chapter["type"] = "default"
        chapter["header_invisible"] = False
        chapter["first_line_is_title"] = False
        chapter["subtitle"] = None
        chapter["related_author"] = None
        chapter["original_year"] = None
        chapter["base_work_item"] = None
        chapter["translator"] = None

        if (page_num == "ad" or page_num == "adv") and len(chapters) > 0:
            chapter["prefix"] = None
            chapter["chapter_num"] = None
            chapter["title"] = "Advertisements"
            chapter["display_title"] = "Advertisements"
            chapter["auxiliary"] = False
            chapter["contributor"] = None
            chapter["page_num"] = page_num
            chapter["hidden"] = True # the important bit
            chapter["refs"] = False # for now
            chapter["part_num"] = None
            chapter["has_sections"] = False
            chapter["splice"] = False
            chapter["type"] = "advertisements"
            chapter["format"] = page_format
            chapter["related_author"] = None
            chapter["original_year"] = None
            chapter["subtitle"] = None
            
            chapters.append(chapter)
            break
        
        content = page["content"]
        content_lines = content.split("\n\n")

        if "/sub/" in content:
            chapter_subtitle = re.search(r"\/sub\//(.+?)\n\n", content).group(1)
            print(f"Subtitle found: {chapter_subtitle}")
            chapter_subtitle = convert_to_title_case(chapter_subtitle)
            chapter["subtitle"] = chapter_subtitle

        is_sectioned_at_beginning = False

        if transclusion_is_sectioned:
            for chapter_tag in chapter_tags:
                if content.startswith(f"/{chapter_tag}/"):
                    is_sectioned_at_beginning = True
                    break

        for line in content_lines:
            for chapter_tag in chapter_tags:
                increment_chapter_num = True

                chapter_tag_without_slashes = chapter_tag
                chapter_tag = get_plain_tag(chapter_tag)
                if chapter_tag in line:
                    
                    # get_basic_chapter_data(line)
                    if skip_chapter_because_of_chapter_half and chapter_tag == "/ch/":
                        skip_chapter_because_of_chapter_half = False
                        print("ARE WE NOT EVEN FUCKING GETTING HERE?????")
                        break
                    
                    if chapter_tag == "/chh/":
                        skip_chapter_because_of_chapter_half = True
                    
                    chapter_parameters = get_chapter_parameters(line) # because the first will always be '' which is useless
                    
                    chapter_tag = chapter_tag_without_slashes
                    chapter_settings = chapter_parameters["chapter_settings"]

                    chapter_settings = parse_chapter_settings(chapter_settings)

                    chapter_title = chapter_parameters["chapter_title"]
                    

                    if chapter_tag in prefixless_chapter_titles:
                        chapter_title = prefixless_chapter_titles[chapter_tag]
                        chapter["prefix"] = None
                        chapter["chapter_num"] = None
                        chapter["type"] = "preface"
                        chapter_title = prefixless_chapter_titles[chapter_tag]
                
                    elif chapter_tag == "bk" or chapter_tag == "pt":
                        part_num += 1
                        chapter["prefix"] = chapter_prefixes[chapter_tag]
                        if part_prefix:
                            chapter["prefix"] = part_prefix
                        chapter["chapter_num"] = part_num
                        if "collection" not in work_type_name:
                            chapter_title = None
                        chapter["type"] = "part"

                        if chapters_are_subpages_of_parts == "y" or chapters_are_subpages_of_parts == None:
                            chapter_num = 0
                    
                    elif chapter_tag == "contch":
                        chapter["prefix"] = None
                        chapter["chapter_num"] = None
                        # if not chapter_title or chapter_title == "\n":
                        chapter_title = work_title
                        # else:
                        #     chapter["title"] = chapter_title
                        
                    else:
                        print("GOT TO CHAPTER NUM")
                        print(chapter_num)
                        # chapter_num += 1

                        if chapter_prefix == "n":
                            chapter["prefix"] = None
                        elif work_type_name == "ssc" or work_type_name == "short story collection" or work_type_name == "ssa" or work_type_name == "short story anthology":
                            if chapter_prefix == "y":
                                chapter["prefix"] = "Chapter"
                            else:
                                chapter["prefix"] = None
                            chapter["type"] = "short story"
                        elif work_type_name == "pc" or work_type_name == "poetry collection" or work_type_name == "pa" or work_type_name == "poetry anthology":
                            chapter["prefix"] = None
                            chapter["type"] = "poem"
                        elif work_type_name == "ec" or work_type_name == "essay collection" or work_type_name == "ea" or work_type_name == "essay anthology":
                            chapter["prefix"] = None
                            chapter["type"] = "essay"
                        elif not chapter_prefix:
                            chapter["prefix"] = "Chapter"
                        else:
                            chapter["prefix"] = chapter_prefix
                            chapter["type"] = "numbered chapter"
                        if chapter_num == 0 and (chapter_type == "default" or chapter_type == "numbered chapter"):
                            chapter_num += 1
                            increment_chapter_num = False
                        chapter["chapter_num"] = chapter_num

                        if part_prefix and chapter["type"] == "part":
                            chapter["prefix"] = part_prefix

                        # chapter["title"] = None
                    

                    # Get chapter page num
                    if type(page_num) == str and page_num.isdigit():
                        chapter["page_num"] = int(page_num)
                    else:
                        chapter["page_num"] = page_num
                    
                    # if not chapter["title"]:
                    chapter["title"] = chapter_title

                    chapter["hidden"] = False
                    chapter["auxiliary"] = False
                    chapter["contributor"] = None
                    chapter["refs"] = False # for now
                    chapter["part_num"] = part_num
                    chapter["has_sections"] = False
                    # print(chapter)
                    # chapter["title"] = chapter_title
                    chapter["display_title"] = chapter["title"]

                    if chapter_settings:
                        for setting in chapter_settings:
                            if setting in chapter:
                                chapter[setting] = chapter_settings[setting]
                        
                    if chapter_type == "nam" or (chapter["type"] != "default" and not force_chapter_numbers and chapter["type"] != "numbered chapter"):
                        chapter["prefix"] = None
                        chapter["chapter_num"] = None
                        print(chapter_num)
                        increment_chapter_num = False
                        # chapter_num -= 1
                        # chapter["type"] = "non-work chapter"
                    
                    if chapter_type == "fm" or chapter["type"] == "front-matter chapter":
                        chapter["prefix"] = None
                        chapter["chapter_num"] = None
                        # chapter["type"] = "front-matter chapter"
                    
                    if chapter["auxiliary"]:
                        chapter["prefix"] = None
                        chapter["chapter_num"] = None
                        increment_chapter_num = False
                    
                    if chapter["title"] and (": " in chapter["title"] and (chapter["type"] != "preface" and chapter["type"] != "default")):
                        chapter["title"], chapter["subtitle"] = chapter["title"].split(": ")

                    if chapter_title and not chapter["first_line_is_title"]:
                        chapter["title"] = convert_to_title_case(chapter["title"])
                        chapter["display_title"] = convert_to_title_case(chapter["display_title"])
                        if chapter["subtitle"]:
                            chapter["subtitle"] = convert_to_title_case(chapter["subtitle"])

                    splice_chapter = False
                    if chapter_splice_points:
                        print(f"if chapter splice points. Chapter num: {chapter_num}")
                        if chapter_num in chapter_splice_points:
                            print("if chapter num in chapter splice points")
                            splice_chapter = True
                    chapter["splice"] = splice_chapter
                    chapter["format"] = page_format

                    if increment_chapter_num:
                        chapter_num += 1
                        chapter["chapter_num"] = chapter_num

                    chapter["sectioned_at_beginning"] = is_sectioned_at_beginning
                    section_name = None

                    if transclusion_is_sectioned:
                        if chapter["type"] == "part":
                            section_name = f"Part {part_num}"
                        elif chapters_are_subpages_of_parts and chapter["type"] != "part":
                            section_name = f"Part {part_num} Chapter {chapter_num}"
                        else:
                            section_name = f"Chapter {chapter_num}"

                    chapter["section_name"] = section_name

                    chapters.append(chapter)
                    previous_chapter = chapter
                    previous_chapter_index = len(chapters) - 1
                
                if section_tag in content:
                    previous_chapter["has_sections"] = True
                    chapters[previous_chapter_index] = previous_chapter

    chapters = get_chapters_with_refs(chapters, page_data)

    print(chapters)
    # exit()
    write_to_json_file(chapters_json_file, chapters)
    print_in_green("Chapter data retrieved! Go and make sure it's all correct.")
    exit()

def get_chapters_with_refs(chapters, page_data):
    chapters_with_refs = []

    for chapter_num, chapter in enumerate(chapters):
        chapter_page_num = chapter["page_num"]
        try:
            next_chapter = chapters[chapter_num + 1]
            next_chapter_page_num = next_chapter["page_num"]
            last_page = get_actual_page_num(next_chapter_page_num, page_data)
        except IndexError:
            # next_chapter_page_num = chapter_page_num + 1000
            last_page = len(page_data) - 1

        
        first_page = get_actual_page_num(chapter_page_num, page_data)

        for page_num in range(first_page, last_page + 1):
            page = page_data[page_num]
            content = page["content"]
            if "/r/" in content or "/rc/" in content or "/rcs/" in content or "/rce/" in content or "/ua/" in content:
                chapter["refs"] = True
                # chapters_with_refs.append(chapter)
                break
        
        chapters_with_refs.append(chapter)
    
    return chapters_with_refs

def get_chapter_from_title(title, chapters):
    for chapter in chapters:
        chapter_title = chapter["title"]
        if chapter_title == title:
            return chapter

def get_chapter_from_page_num(chapters, page_num, for_sections=False):
    print(page_num)
    try:
        page_num = int(page_num)
        # print(f"WELL WE GOT HERE??? {page_num}")
        first_chapter = chapters[0]
        first_chapter_type = first_chapter["type"]
        if first_chapter_type == "preface":
            first_chapter = chapters[1]
        first_chapter_start_page = first_chapter["page_num"]
        # print(f"WELL WE GOT HERE??????? {page_num} {first_chapter_start_page}")
        # if type(page_num) == int and type(first_chapter_start_page) == int:
        if page_num < first_chapter_start_page:
            print(f"Page number {page_num} is less than first chapter start page {first_chapter_start_page}.")
            print("I'm getting here you know")
            # print()
            return "Front matter"
        # (TypeError, ValueError)
    except (TypeError, ValueError):
        print(f"Well page num IS {page_num}")
        if page_num == "fro":
            return "Front matter"
        if for_sections:
            pass
        else:
            print_in_red(f"Page number {page_num} is not an integer.")
            # exit()
    for chapter_num, chapter in enumerate(chapters):
        # print(f"Chapter {chapter}")
        # print(f"Page {page_num}")
        chapter_page_num = chapter["page_num"]
        chapter_prefix = chapter["prefix"]
        part_num = chapter["part_num"]
        if for_sections and part_num and chapter_prefix == "Book" or chapter_prefix == "Part":
            continue
        try:
            next_chapter = chapters[chapter_num + 1]
            next_chapter_page_num = next_chapter["page_num"]
            if type(next_chapter_page_num) != int: # if advertisements
                next_chapter_page_num = chapter_page_num + 1000
        except IndexError:
            next_chapter_page_num = chapter_page_num + 1000 # arbitrary number to make sure it's sufficiently higher than current page number
        # print(chapter)
        if type(chapter_page_num) == str:
            chapter_page_num = 0
        
        print(f"Page num: {page_num} Chapter page num: {chapter_page_num} Next chapter page num: {next_chapter_page_num}")
        
        # if previous_chapter_page_num == 0 and chapter_page_num > overall_page_num:
        #     front_matter = {}
        #     front_matter["chapter_num"] = 0
        #     front_matter["part_num"] = 0
        #     front_matter["page_num"] = 0
        # print(f"Type of chapter page num: {type(chapter_page_num)}. Type of page num: {type(page_num)} Type of next chapter page num: {type(next_chapter_page_num)}")
        # if type(page_num) != str:
        
        if chapter_page_num <= page_num and next_chapter_page_num > page_num:
            return chapter
        # else:
        #     return chapter

def get_actual_page_num(chapter_page_num, page_data):
    # if type(chapter_page_num) == int:
    #     return chapter_page_num
    # else:
    for actual_page_num, page in enumerate(page_data):
        page_marker = page["marker"]
        if page_marker == str(chapter_page_num):
            return actual_page_num

def add_section(sections, section_num, chapter_num, part_num, page_num, overall_page_num, section_name=None, section_prefix=None):
    section = {}
    if overall_page_num:
        overall_page_num += 1 # not zero indexed
    section["chapter_num"] = chapter_num
    section["part_num"] = part_num
    section["section_num"] = section_num
    section["page_num"] = page_num
    section["overall_page_num"] = overall_page_num
    section["title"] = section_name
    section["prefix"] = section_prefix
    sections.append(section)
    return sections
    

def get_section_data(chapters, page_data, transcription_text, first_section_automatically_after_chapter):
    print("Getting section data...")
    sections_json_file = "section_data.json"
    sections = get_json_data(sections_json_file)
    if sections:
        print_in_green("Section data JSON found!")
        return sections

    sections = []

    section_tag = get_plain_tag("sec")

    if section_tag in transcription_text:
        chapter_num = 0
        section_num = 0
        # first_section_added = False
        previous_chapter_title = "Front matter"
        for overall_page_num, page in enumerate(page_data):
            section_pattern = r"(\/sec\/)\n"

            try:
                page_num = int(page["marker"])
            except ValueError:
                page_num = page["marker"]
            content = page["content"]
            
            section_matches = re.findall(section_pattern, content)

            for match in section_matches:
                chapter = get_chapter_from_page_num(chapters, page_num, for_sections=True)

                previous_chapter_num = chapter_num
                # try:
                #     previous_chapter_title = chapters[previous_chapter_num]["title"]
                # except:
                #     previous_chapter_title = None
                chapter_title = chapter["title"]
                print(f"Chapter title: {chapter_title} Previous chapter title: {previous_chapter_title}")
                chapter_num = chapter["chapter_num"]
                chapter_start_page_num = chapter["page_num"]
                part_num = chapter["part_num"]
                chapter_prefix = chapter["prefix"]
                if ((chapter_prefix == "Book" or chapter_prefix == "Part") and part_num):
                    continue
                #  or not first_section_automatically_after_chapter
                chapter_has_sections = chapter["has_sections"]
                if not chapter_has_sections:
                    print_in_red(f"ERROR: Chapter data says chapter has no sections, but section was found in chapter when collecting section data! Something is wrong with the code. Please fix it. Chapter num: {chapter_num}, part num: {part_num}, page num: {page_num}, overall page num: {overall_page_num}, match: {match}")
                    exit()
                else:
                    if (chapter_num != previous_chapter_num or (chapter_title != previous_chapter_title)):
                        section_num = 1
                        if first_section_automatically_after_chapter:
                            unreadable_overall_page_num = None # Change later when logic can do this
                            sections = add_section(sections, section_num, chapter_num, part_num, chapter_start_page_num, unreadable_overall_page_num)
                            previous_chapter_title = chapter_title
                
                # add first section of chapter if it's the first time encountering that chapter
                
                
                section_num += 1

                # add section
                sections = add_section(sections, section_num, chapter_num, part_num, page_num, overall_page_num)
                # section_num += 1


    else:
        print_in_yellow("No sections found in transcription text.")

    # print(sections)
    # exit()
    write_to_json_file(sections_json_file, sections)
    return sections
    

def get_aux_toc_items(chapters, mainspace_work_title, chapters_are_subpages_of_parts):
    aux_toc_items = []
    spacing = ""
    is_subchapter = False
    part_prefix = ""
    for chapter in chapters:
        # if parts_exist:
        chapter_prefix = chapter["prefix"]
        if not chapter_prefix:
            chapter_prefix = "Chapter"
        chapter_prefix += " "
        chapter_num = chapter["chapter_num"]
        if chapter_prefix == "Chapter ":
            chapter_num = chapter["chapter_num"]
            if is_subchapter:
                spacing = ":"
        elif chapter_prefix == "Book " or chapter_prefix == "Part ":
            spacing = ""
            is_subchapter = True
            part_prefix = chapter_prefix
            # subchapters = chapter["subchapters"]
            # aux_subchapters = get_aux_toc_items(subchapters, mainspace_work_title, ":")
            # spacing = ":"
            # aux_subchapters = "\n".join(aux_subchapters)
        part_num = chapter["part_num"]
        
        chapter_numbered_name = f"{chapter_prefix}{chapter_num}"
        chapter_numbered_display_name = chapter_numbered_name

        if is_subchapter and chapters_are_subpages_of_parts and chapter_prefix == "Chapter ":
            chapter_numbered_name = f"{part_prefix}{part_num}/{chapter_numbered_name}"


        chapter_title = chapter["title"]

        if chapter_title == "Advertisements":
            continue
        
        internal_chapter_name = f"{mainspace_work_title}/"

        if chapter_title and chapter_num:
            # aux_toc_entry = f"* [[{mainspace_work_title}/|{chapter_title}]]"
            internal_chapter_name += chapter_numbered_name
            chapter_display = f"{chapter_numbered_display_name}: {chapter_title}"
        elif chapter_title and not chapter_num:
            internal_chapter_name += chapter_title
            chapter_display = chapter_title
            aux_toc_entry = f"{spacing}* [[{mainspace_work_title}/{chapter_title}|{chapter_title}]]"
        else:
            internal_chapter_name += chapter_numbered_name
            chapter_display = chapter_numbered_display_name
            aux_toc_entry = f"{spacing}* [[{mainspace_work_title}/{chapter_numbered_name}|{chapter_numbered_name}]]"

        aux_toc_entry = f"{spacing}* [[{internal_chapter_name}|{chapter_display}]]"

        aux_toc_items.append(aux_toc_entry)
    
    return aux_toc_items

def convert_page_num_to_roman_if_roman(page_num, page_data):
    for page in page_data:
        page_marker = page["marker"]
        if page_marker == str(page_num):
            page_format = page["format"]
            if page_format == "roman":
                page_num = roman.toRoman(page_num).lower()
            return page_num

def generate_toc(chapters, mainspace_work_title, toc_format, toc_is_auxiliary, page_data, chapters_are_subpages_of_parts, smallcaps=True, header=False):
    print("Generating TOC...")

    if toc_is_auxiliary:
        # toc_format = "auxiliary"
        aux_toc_beginning = "{{AuxTOC|\n"
        aux_toc_ending = "\n}}"
        # aux_toc_items = []
        aux_toc_items = get_aux_toc_items(chapters, mainspace_work_title, chapters_are_subpages_of_parts)
        aux_toc_items = "\n".join(aux_toc_items)
        aux_toc = aux_toc_beginning + aux_toc_items + aux_toc_ending
        print(aux_toc)
        return aux_toc

    if smallcaps:
        smallcaps = "yes"
    else:
        smallcaps = "no"
    # if header:
    header = f"\n{{{{TOC row 1-1-1|{{{{asc|Chapter}}}}||{{{{asc|Page}}}}}}}}"
    # else:
    #     header = ""
    # WHY DOES
    toc_beginning = f"""{{{{c|{{{{larger|{{{{uc|Contents}}}}}}}}}}}}
{{{{TOC begin}}}}{header}
"""
    print(f"TOC BEGINNING IS {toc_beginning} BEFORE")
#     toc_beginning = f"""{{{{c|{{{{larger|CONTENTS}}}}}}}}
# <div class="toc-block">
# """
    toc_ending = """{{TOC end}}"""
    # toc_ending = "</div>"

    for chapter_num, chapter in enumerate(chapters):
        page_num = chapter["page_num"]
        page_num = convert_page_num_to_roman_if_roman(page_num, page_data)
        chapter_title = chapter["title"]
        if chapter_title == "Advertisements":
            continue
        chapter_prefix = chapter["prefix"]
        chapter_type = chapter["type"]
        splice = chapter["splice"]
        chapter_is_auxiliary = chapter["auxiliary"]
        # chapter_num = chapter_num + 1 # 1-indexed rather than 0
        chapter_num = chapter["chapter_num"]
        if chapter_num:
            chapter_num_as_roman = roman.toRoman(chapter_num)
        else:
            chapter_num_as_roman = ""

        if not chapter_num and not chapter_prefix:
            toc_link = f"[[{mainspace_work_title}/{chapter_title}|{chapter_title}]]"
        else:
            if not chapter_prefix:
                chapter_prefix = "Chapter"
            toc_link = f"[[{mainspace_work_title}/{chapter_prefix} {chapter_num}|{chapter_title}]]"

        if chapter_type == "poem" or chapter_type == "short story" or chapter_type == "essay":
            toc_link = f"[[{mainspace_work_title}/{chapter_title}|{chapter_title}]]"
        
        chapter_contributor = chapter["contributor"]

        if toc_format:
            toc_row = toc_format

            replacements = {
                "cnum": str(chapter_num_as_roman),
                "cnam": toc_link,
                "cpre": chapter_prefix.upper() if chapter_prefix else "", # just in case prefix is put into the toc, but usually it isn't
                "pnum": str(page_num),
                "ccon": f"[[Author:{chapter_contributor}|]]" if chapter_contributor else "",
            }
            
            toc_row = format_form_tag(toc_row, replacements)

        else:
            toc_row = f"{{{{TOC row 1-1-1|{chapter_num_as_roman}|{toc_link}|{page_num}}}}}"

        if chapter_is_auxiliary:
            toc_row = toc_row.replace("|", "|class=wst-toc-aux|", 1)

        toc_row = toc_row.replace("|.|", "||")
        
        toc_beginning += toc_row + "\n"
        
        if splice:
            splice_tag = get_plain_tag("spl")
            toc_beginning += splice_tag + "\n"
    # print(f"TOC BEGINNING IS {toc_beginning} AFTER")
    toc = toc_beginning + toc_ending
    print_in_green("TOC generated.")
    return toc


"""
{{c|{{larger|LIST OF ILLUSTRATIONS}}}}
{{dhr}}
{{TOC begin|sc=|max-width=25em}}
{{TOC row 2-1|[[The Blind Man's Eyes (July 1916)#frontis|"Until I come to you as—as you have never known me yet!"]]|''Frontispiece''}}
{{TOC row 2-1|[[The Blind Man's Eyes (July 1916)/Chapter 6#img|"He's been murdered!"]]|{{sc|Page}} 64}}
{{TOC row 2-1|[[The Blind Man's Eyes (July 1916)/Chapter 10#img|"It will not be merely accusation they make against me—it will be my sentence!"]]|{{ditto|Page}} 122}}
{{TOC row 2-1|[[The Blind Man's Eyes (July 1916)/Chapter 18#img|She gazed about again, therefore, and told him what she saw]]|{{ditto|Page}} 266}}
{{TOC end}}
"""

def determine_illustration_page_number(image, page_data):
    image_page_number = image["page_num"] - 1
    page_with_image = page_data[image_page_number]
    page_marker = page_with_image["marker"]
    if page_marker.isdigit():
        return page_marker
    else:
        previous_page_number = image_page_number + 1
        while 1:
            previous_page = page_data[previous_page_number]
            previous_page_marker = previous_page["marker"]
            previous_page_quality = previous_page["page_quality"]
            if previous_page_marker.isdigit() and previous_page_quality != "0":
                print(previous_page_marker)
                return previous_page_marker
            previous_page_number += 1
        # previous_page_number -= 1
    # image_type = image["type"]
    # if image_type == "sequential":
    #     return image_page_number
    # elif image_type == "frontispiece":
    #     return "''Frontispiece''"
    # elif image_type == "sequential":
    #     return image_page_number


def generate_illustrations(image_data, page_data, chapters, mainspace_work_title, transcription_text):
    first_sequential_image_done = False
    illustrations_beginning = """c|{{larger|{{uc|Illustrations}}}}}}
{{dhr}}
{{TOC begin}}
"""
    for image in image_data:
        image_type = image["type"]
        image_caption = image["caption"]
        image_page_number = image["page_num"]
        if image_type == "frontispiece":
            page_number_parameter = "''Frontispiece''"
            page_number_to_parse = "fro"
            if "\n-fro\n" in transcription_text:
                illustration_page_number = "fro"
            else:
                illustration_page_number = get_marker_from_page_num(image_page_number, page_data)
        elif image_type == "sequential" and image_caption:
            # illustration_page_number = determine_illustration_page_number(image, page_data)
            # if first_sequential_image_done:
            #     page_word = "{{ditto|page}} "
            # if not first_sequential_image_done:
            #     first_sequential_image_done = True
            #     page_word = "{{sc|page}} "
            if "\n-i\n" not in transcription_text:
                illustration_page_number = get_marker_from_page_num(image_page_number, page_data)
                page_number_to_parse = illustration_page_number
            else:
                illustration_page_number = determine_illustration_page_number(image, page_data)
                page_number_to_parse = "i"
            page_word = "" # For now
            page_number_parameter = page_word + illustration_page_number
        else:
            continue
        if chapters:
            chapter = get_chapter_from_page_num(chapters, illustration_page_number)
            illustration_link = generate_page_link(chapter, page_number_to_parse, mainspace_work_title)
            illustrations_beginning += f"{{{{TOC row 2-1|[[{illustration_link}|{image_caption}]]|{page_number_parameter}}}}}\n"

    illustrations_end = "{{TOC end"
    illustrations = illustrations_beginning + illustrations_end
    return illustrations



def format_chapter_beginning_to_smallcaps(page, work_type_name):
    global chapter_pattern
    words_to_avoid_pairing_with_names = [
        "Although",
        "And",
        "As",
        "How",
        "If",
        "Is",
        "That",
        "The",
        "Then",
        "Was",
        "What",
        "When",
        "Where",
        "Why",
    ]
    content = page['content']

    if string_not_in_content(content, "/ch/", "Formatting chapter beginning to smallcaps"):
        return page
    
    quote_pattern = r"\"?\'?"
    if work_type_name == "poetry collection":
        chapter_pattern = chapter_pattern_for_poetry_collection
    
    full_names_pattern = rf"{chapter_pattern}({quote_pattern}[A-Z][a-z]+ [A-Z][a-z]+)"
    general_pattern = rf"{chapter_pattern}({quote_pattern}[A-Z][a-z]+)"
    # general_pattern = rf"{chapter_pattern}(.+\s)"
    first_person_pattern = rf"{chapter_pattern}({quote_pattern}[I O A An] [a-z]+)" # TODO: test this
    replacement = r"\1{{sc|\2}}"

    # replace full names first, so that they don't get replaced by the general pattern

    full_names_replaced = re.sub(full_names_pattern, replacement, content)
    first_person_replaced = re.sub(first_person_pattern, replacement, full_names_replaced)
    general_replaced = re.sub(general_pattern, replacement, first_person_replaced)

    page['content'] = general_replaced

    return page

def format_arbitrary_drop_inital(page, image_data, img_num):
    content = page["content"]

    if string_not_in_content(content, "/di/", "Formatting arbitrary drop initial") and string_not_in_content(content, "/dii/", "Formatting arbitrary drop initial with image"):
        return img_num, page
    
    drop_initial_image_pattern = r"(\/dii\/.+?\/)"
    drop_initial_pattern = r"\/di\/(.+)\/"

    drop_initial_image = re.search(drop_initial_image_pattern, content)

    if drop_initial_image:
        image = image_data[img_num]
        image_title = image["title"]
        image_extension = image["extension"]
        image_letter = image["letter"]
        image_filename = image_title + "." + image_extension
        replacement = f"{{{{di|{image_letter}|image={image_filename}}}}}" # DROP INITIAL IMAGE SIZE HANDLED IN CSS

        content = re.sub(drop_initial_image_pattern, replacement, content)
        img_num += 1

    page["content"] = content

    return img_num, page

def find_image_with_letter(image_data, first_letter):
    for image in image_data:
        image_letter = image["letter"]
        if image_letter == first_letter:
            return image

def format_drop_initial_as_image(content, image_data, first_letter):
    print("Formatting drop initial as image...")

    image = find_image_with_letter(image_data, first_letter)

    image_title = image["title"]
    image_extension = image["extension"]
    image_filename = image_title + "." + image_extension
    image_size = image["size"]

    content = content.replace(f"{{{{di|{first_letter}", f"{{{{di|{first_letter}|image={image_filename}")

    return content


def format_chapter_beginning_to_drop_initial(page, drop_initials_float_quotes, chapter_beginning_formatting, image_data):

    content = page["content"]

    # CHANGE LATER TO INCLUDE ALL KINDS OF CHAPTERS
    if string_not_in_content(content, "/ch/", "Formatting chapter beginning to drop initial"):
        return page
    

    chapter_beginning_pattern = rf"{chapter_pattern}(.)(.)"

    chapter_beginning = re.search(chapter_beginning_pattern, content)

    chapter_heading = chapter_beginning.group(1)
    first_letter = chapter_beginning.group(2)
    second_letter = chapter_beginning.group(3)

    initial_template = chapter_beginning_formatting[:2]

    drop_initial_quotes = [
        '"',
        "'",
    ]

    if first_letter in drop_initial_quotes:
        replacement = rf"\1{{{{{initial_template}|\3|fl=\2}}}}"
        first_letter = second_letter
        content = re.sub(chapter_beginning_pattern, replacement, content)
    
    elif first_letter.isalpha():
        replacement = rf"\1{{{{{initial_template}|\2}}}}\3"
        content = re.sub(chapter_beginning_pattern, replacement, content)


    if chapter_beginning_formatting.endswith("ii"):
        content = format_drop_initial_as_image(content, image_data, first_letter)

    page["content"] = content

    return page


"""
The formatting continuations logic will have to be changed later, to account for a circumstance like this:

-

/fb//

-

//fb/

/fb//

-

//fb/

The logic will have to somehow do itself twice. While loop that breaks after second time?

It will also have to account for this:

-

/fb//

//fb/

/fb//

-

//fb/

So yes, on page 1 an fb EXISTS, but does not have a continuation. So we can't just check to see if it EXISTS, we have to check to see if it has a continuation.
"""

def add_illustrations_to_transcription(page, illustrations):
    content = page["content"]
    illus_tag = get_plain_tag("illus")

    if string_not_in_content(content, illus_tag, "Adding illustrations to transcription"):
        return page
    
    content = convert_simple_markup(content, "illus", illustrations)

    page["content"] = content
    
    return page


def add_toc_to_transcription(page, toc, block_continuations):

    content = page["content"]
    # header = page["header"]
    # footer = page["footer"]

    toc_tag = get_plain_tag("toc")
    spl_tag = get_plain_tag("spl")

    if string_not_in_content(content, toc_tag, "Adding TOC to transcription"):
        # Your mind is in the right place. But still, how are we going to know which TOC split it is if there's no iterator outside this function?
        return block_continuations, page
    
    if spl_tag in toc:
        toc_split = toc.split("\n" + spl_tag + "\n")
        if "toc-block" in toc:
            start_template = "<div class=\"toc-block\">"
            end_template = "</div>"
        else:
            start_template = "{{TOC begin}}"
            end_template = "{{TOC end}}"

        block_continuations, page = handle_block_continuations(page, toc_tag, block_continuations, start_template, end_template, split_list=toc_split)

        content = page["content"] # make sure to update content after handling formatting continuations

    else:
        content = convert_simple_markup(content, "toc", toc)


    page["content"] = content
    # page["header"] = header
    # page["footer"] = footer

    return block_continuations, page

def convert_chapter_headers(page, chapters, overall_chapter_num, chapter_format, chapter_type, chapter_half_is_in_work, first_section_automatically_after_chapter):
    # IF MULTIPLE CHAPTERS, THEY NEED TO BE SECTIONED OUT WITH ANCHORS!!!!!
    content = page["content"]

    if strings_not_in_content(content, chapter_tags, "Converting chapter headings with"):
        return overall_chapter_num, page


    chapters_in_page = []

    # Make this more dynamic, to deal with more scenarios
    for chapter_tag in chapter_tags:
        chapters_in_page_of_tag = get_string_from_lines(content, chapter_tag)
        # print(chapters_in_page_of_tag)
        if chapters_in_page_of_tag:
            chapters_in_page.append(chapters_in_page_of_tag)
    
    print(chapters_in_page)

    for chapter in chapters_in_page:
        for line_num, ch_tag in chapter.items():
            # part_num_zero_indexed = part_num - 1
            # chapter = chapters[chapter_num]
            if not ("/ch/" in ch_tag and chapter_half_is_in_work):
                overall_chapter_num += 1

            overall_chapter_num_zero_indexed = overall_chapter_num - 1
            chapter = chapters[overall_chapter_num_zero_indexed]

            chapter_header_is_invisible = chapter["header_invisible"]

            if chapter_header_is_invisible:
                content = replace_line(content, "", line_num)
            
            # chapter_type = chapter["type"]

            roman_chapter_num = ""
            real_chapter_num = chapter["chapter_num"]
            if real_chapter_num:
                print(real_chapter_num)
                roman_chapter_num = roman.toRoman(real_chapter_num)
                inflect_engine = inflect.engine()
                chapter_num_as_word = inflect_engine.number_to_words(real_chapter_num).capitalize()
                chapter_num_as_ordinal = inflect_engine.ordinal(chapter_num_as_word.lower()).capitalize()
                if chapter_type == "num":
                    displayed_section_num = real_chapter_num
                elif chapter_type == "word":
                    displayed_section_num = chapter_num_as_word
                elif chapter_type == "ord":
                    displayed_section_num = chapter_num_as_ordinal
                else:
                    displayed_section_num = roman_chapter_num
            else:
                displayed_section_num = None

            chapter_prefix = chapter["prefix"]

            if chapter_prefix:
                chapter_prefix += " "
            else:
                chapter_prefix = ""

            chapter_title = chapter["display_title"]
            chapter_has_sections = chapter["has_sections"]

            if chapter_format:
                # if len(chapters_in_page) == 1:
                replacements = {
                    "cnam": chapter_title,
                    "cnum": displayed_section_num,
                    "cpre": chapter_prefix,
                }

                chapter_text = format_form_tag(chapter_format, replacements)

                if chapter_text == chapter_format:
                    chapter_text = f"{{{{ph|class=chapter|{chapter_title}.}}}}"
                if ch_tag == "/ch/" and chapter_half_is_in_work:
                    if chapter_type == "short story":
                        print("CLEARLY I'M NOT GETTING HERE")
                        chapter_text = f"{{{{ph|class=chapter|{chapter_title}}}}}"
                    else:
                        print("Well, am I getting to the other one???")
                        print(chapter_type)
                        chapter_text = f"{{{{ph|class=chapter|{chapter_prefix}{displayed_section_num}}}}}"
                # else: handle section tags
            else:
                if ch_tag == "/ch/" and chapter_half_is_in_work:
                    if chapter_type == "short story":
                        chapter_text = f"{{{{ph|class=chapter|{chapter_title}}}}}"
                    else:
                        chapter_text = f"{{{{ph|class=chapter|{chapter_prefix}{displayed_section_num}}}}}"
                elif chapter_title == None: # try this very verbose solution, but why on earth is it needed???
                    chapter_text = f"{{{{ph|class=chapter|{chapter_prefix}{displayed_section_num}}}}}"
                elif ch_tag == "/contch/":
                    chapter_text = f"{{{{ph|class=title-header|{chapter_title}}}}}"
                elif not chapter_prefix and not displayed_section_num:
                    chapter_text = f"{{{{ph|class=chapter|{chapter_title}}}}}"
                else:
                    # print(type(chapter_title))
                    # print(chapter_title)
                    chapter_text = f"{{{{ph|class=chapter num|{chapter_prefix}{displayed_section_num}}}}}\n{{{{ph|class=chapter title|{chapter_title}|level=2}}}}"
            if ". . ." not in chapter_text:
                chapter_text = chapter_text.replace(" .", ".")
            
            if "/chh/" in ch_tag:
                chapter_text = chapter_text.replace("class=chapter ", "class=chapter-half ")
                chapter_text = chapter_text.replace("class=chapter|", "class=chapter-half|")
            
            if ch_tag == "/pt/" or ch_tag == "/bk/" or chapter_type == "part":
                part_num = chapter["part_num"]
                roman_part_num = roman.toRoman(part_num)
                chapter_text = f"{{{{ph|class=part-header|{chapter_prefix} {roman_part_num}}}}}"
            
            if chapter_has_sections and "/chh/" not in ch_tag and first_section_automatically_after_chapter:
                chapter_text += "\n/sec/"

            content = replace_line(content, chapter_text, line_num)
        chapter_subtitle = chapter["subtitle"]
        if chapter_subtitle:
            content = re.sub(r"\/sub\//.+?\n\n", f"{{{{ph|class=chapter-subtitle|{chapter_subtitle}}}}}\n\n", content)
            # chapter_num += 1

    content = content.replace("  ", " ")

    page["content"] = content
    return overall_chapter_num, page


def convert_section_headers(page, sections, overall_section_num, section_format, section_type):
    content = page["content"]
    sec_tag = get_plain_tag("sec")

    if string_not_in_content(content, sec_tag, "Converting section headings"):
        return overall_section_num, page
    
    sections_in_page = get_string_from_lines(content, sec_tag)

    for line_num, sec_tag in sections_in_page.items():
        # part_num_zero_indexed = part_num - 1
        # chapter = chapters[chapter_num]

        overall_section_num += 1

        overall_section_num_zero_indexed = overall_section_num - 1
        try:
            section = sections[overall_section_num_zero_indexed]
        except Exception as e:
            print(f"WELP, we got an error: {e}. Let's just see what happens when we say, fuck it.")
            input()
            return overall_section_num, page

        real_section_num = section["section_num"]
        roman_section_num = roman.toRoman(real_section_num)
        if section_type == "num":
            displayed_section_num = real_section_num
        else:
            displayed_section_num = roman_section_num
        section_prefix = section["prefix"]
        section_anchor_prefix = "Section"
        section_anchor = f"{section_anchor_prefix} {displayed_section_num}"

        section_title = section["title"]
        if section_title:
            section_anchor = section_title
    
        if section_format:
            replacements = {
                    "snam": section_title,
                    "snum": roman_section_num,
                    "spre": section_prefix,
                }

            section_text = format_form_tag(section_format, replacements)
        else:
            if section_title == None: # try this very verbose solution, but why on earth is it needed???
                section_text = f"{{{{anchor|{section_anchor}}}}}{{{{ph|class=section|{displayed_section_num}}}}}"
        
        content = replace_line(content, section_text, line_num)
    
    page["content"] = content
    return overall_section_num, page

            # else:
            #     # print(type(chapter_title))
            #     # print(chapter_title)
            #     # section_text = f"{{{{ph|class=chapter num|{chapter_prefix} {roman_chapter_num}}}}}\n{{{{ph|class=chapter title|{chapter_title}|level=2}}}}"
            #     pass # for now


def check_if_chapter_half_in_work(transcription_text):
    return "/chh/" in transcription_text

########################## references ##########################


def handle_reference_continuations(page, content, reference_continuations):
    # content = page["content"]
    marker = page["marker"]
    # footer = page["footer"]

    print(f"Reference continuations: {reference_continuations}")
    # if string_not_in_content(content, "/rc/", "Handling reference continuations"):
    #     return page

    # if "/rcs/" in content and "/rce/" in content:
    #     continued_reference = re.findall(r"\/rcs\//(.+?)\//rce\/", content)[0]
    #     ref_id = f"P{marker}"
    #     reference_continuations.append(ref_id)

    if "/rcs/" in content and "/rce/" in content:
        ref_id = reference_continuations[0]
        ref_id_2 = f"P{marker}"
        reference_continuations = [ref_id_2]
        continued_reference1 = re.findall(r"\/rc\//(.+?)\//rce", content)[0]
        continued_reference2 = re.findall(r"\/rcs\//(.+?)\//rc", content)[0]
        content = content.replace(f"/rcs//{continued_reference2}//rc", f"<ref name=\"{ref_id_2}\">{continued_reference2}//rc")
        content = content.replace(f"/rc//{continued_reference1}//rce", f"<ref follow=\"{ref_id}\">{continued_reference1}//rce")

    
    else:
        if "/rcs/" in content:
            continued_reference = re.findall(r"\/rcs\//(.+?)\//rc\/", content)[0]
            ref_id = f"P{marker}"
            reference_continuations.append(ref_id)

        if "/rc//" in content:
            continued_reference = re.findall(r"\/rc\//(.+?)\//rc", content)[0]
            print(content)
            ref_id = reference_continuations[0]
        
        if "//rce/" in content:
    
            reference_continuations = []

        content = content.replace(f"/rcs//{continued_reference}//rc", f"<ref name=\"{ref_id}\">{continued_reference}//rc")
        content = content.replace(f"/rc//{continued_reference}//rc", f"<ref follow=\"{ref_id}\">{continued_reference}//rc")

    content = content.replace("//rc/", "</ref>")
    content = content.replace("//rce/", "</ref>")

    return content, reference_continuations
    

def handle_references(page, reference_continuations):
    content = page["content"]
    footer = page["footer"]

    if string_not_in_content(content, "/r/", "Handling references") and string_not_in_content(content, "/rc/", "Handling reference continuations") and string_not_in_content(content, "/ua/", "Handling Wikisource contributor notes") and string_not_in_content(content, "/r1/", "Handling references"):
        return page, reference_continuations
    
    if "/rt/" in content:
        if "//rt/" not in content:
            references = re.findall(r"\/rt\//(.+)", content)

        for reference in references:
            reference_text = f"<ref>{reference}</ref>"
            content = content.replace("/r/", reference_text, 1)
            content = content.replace(f"/rt//{reference}", "")
    
    if "/r//" in content:
        references = re.findall(r"\/r\//(.+?)\//r\/", content)

        for reference in references:
            reference_text = f"<ref>{reference}</ref>"
            content = content.replace(f"/r//{reference}//r/", reference_text)

    if "/r1/" in content:
        # numbered_reference_begin_tags like /r1//, /r2//, etc.
        content = re.sub(r"\/r([0-9])\//", r"<ref name=ref\1>", content)
        content = re.sub(r"\//r([0-9])\/", "</ref>", content)

        content = re.sub(r"\/r([0-9])\/", r"<ref name=ref\1 \/>", content)
    

    if "/ua//" in content:
        references = re.findall(r"\/ua\//(.+?)\//ua\/", content)

        for reference in references:
            reference_text = f"<ref>{{{{ua|{reference}}}}}</ref>"
            content = content.replace(f"/ua//{reference}//ua/", reference_text)

    if "/rc/" in content:
        content, reference_continuations = handle_reference_continuations(page, content, reference_continuations)

    
    if footer:
        footer += "\n{{smallrefs}}"
    else:
        footer = "{{smallrefs}}"

    page["content"] = content
    page["footer"] = footer

    return page, reference_continuations





########################## templates ##########################

def add_space_to_apostrophe_quotes(page):
    content = page["content"]

    apostrophe_quotes = [
        "\"'",
        "'\""
    ]

    if string_not_in_content(content, apostrophe_quotes, "Adding spaces to apostrophe quotes"):
        return page

    for apostrophe_quote in apostrophe_quotes:
        # create the template
        apostrophe_quote_spaced = " ".join(list(apostrophe_quote))
        apostrophe_quote_template = "{{" + apostrophe_quote_spaced + "}}"

        content = content.replace(apostrophe_quote, apostrophe_quote_template)

        # get rid of the template if it is actually because of italicized text
        first_symbol = apostrophe_quote[0]
        last_symbol = apostrophe_quote[-1]
        if first_symbol == "'":
            content = content.replace(f"'{apostrophe_quote_template}", f"'{apostrophe_quote}")
        elif last_symbol == "'":
            content = content.replace(f"{apostrophe_quote_template}'", f"{apostrophe_quote}'")

    page["content"] = content
    return page

def add_half_to_transcription(page, title):
    content = page["content"]

    if string_not_in_content(content, "/half/", "Adding half title to transcription"):
        return page
    
    half = f"ph|class=half|{title}"
    content = convert_simple_markup(content, "half", half)

    page["content"] = content

    return page

def convert_language_tags(page):
    content = page["content"]

    if string_not_in_content(content, "/l/", "Converting /l/ to {{lang}} tags in transcription"):
        return page
    
    content = re.sub(r"\/l\/(.+?)\/(.+?)\//l\/", r"{{lang|\1|\2}}", content)

    page["content"] = content

    return page

def convert_complex_dhr(page):
    content = page["content"]

    if string_not_in_content(content, "/d/", "Adding dhrs to transcription"): #fornow
        return page

    content = re.sub(r"\/d\/([0-9])\/", rf"{{{{dhr|\1}}}}", content) # replace /d/2/ with {{dhr|2}} for example
    
    page["content"] = content

    return page

def convert_complex_stars(page):
    content = page["content"]

    if string_not_in_content(content, "/st/", "Adding asterisk separator to transcription") and string_not_in_content(content, "/bt/", "Adding bullet points separator to transcription"): #fornow
        return page

    content = re.sub(r"\/st\/([0-9])\/", rf"{{{{***|\1}}}}", content) # replace /st/5/ with {{***|5}} for example
    content = re.sub(r"\/bt\/([0-9])\/", rf"{{{{***|char=·|\1}}}}", content) # replace /bt/5/ with {{***|char=·|5}} for example

    page["content"] = content

    return page



def convert_title_headers(page, title):
    content = page["content"]

    if string_not_in_content(content, "/ti/", "Converting title headers"):
        return page

    title_header = f"ph|class=title-header|{title}"

    content = convert_simple_markup(content, "ti", title_header)

    page["content"] = content

    return page

def convert_author_links(page):
    content = page["content"]

    if string_not_in_content(content, "/al/", "Converting /al/ to author links in transcription"):
        return page
    
    content = re.sub(r"\/al\//(.+?)\//al\/", r"[[Author:\1|\1]]", content)

    page["content"] = content

    return page

def nowiki(string):
    return "<nowiki>" + string + "</nowiki>"

def convert_italics(page):
    content = page["content"]

    if string_not_in_content(content, "/i/", "Converting /i/ to italics in transcription"):
        return page
    
    nowiki_apostrophe = nowiki("'")

    # replace apostrophes directly outside with nowiki
    content = content.replace("'/i//", f"{nowiki_apostrophe}/i//")
    content = content.replace("//i/'", f"//i/{nowiki_apostrophe}")

    # replace apostrophes inside with nowiki

    italics_pattern = r"\/i\//(.+?)/\/i\/"

    strings_in_italics = re.findall(italics_pattern, content)

    for match in strings_in_italics:
        match = match.replace("'", nowiki_apostrophe)

        # legal lingo, for court case names
        match = match.replace(" v. ", " ''v.'' ")
        match = match.replace(" et. al.", " ''et. al.''")

        # numbers
        # TODO

        content = re.sub(italics_pattern, rf"''{match}''", content, count=1)

    # to fix instances of this
    content = content.replace("{{\" <nowiki>'</nowiki>}}", "{{\" '}}")
    content = content.replace("{{<nowiki>'</nowiki> \"}}", "{{' \"}}")

    page["content"] = content

    return page

def convert_smallcaps(page):
    content = page["content"]

    if string_not_in_content(content, "/sc/", "Converting /sc/ to smallcaps in transcription"):
        return page

    content = re.sub(r"\/sc\//(.+?)\//sc\/", r"{{sc|\1}}", content)

    page["content"] = content

    return page

def convert_degrees(page):
    content = page["content"]

    if string_not_in_content(content, "/deg/", "Formatting /deg/ to degrees in transcription"):
        return page

    degrees_to_format = re.findall(r"\/deg\//(.+?)\//deg\/", content)

    for degree in degrees_to_format:
        coordinate = degree
        coordinate = coordinate.replace("d", "°")
        coordinate = coordinate.replace("'", "′")
        coordinate = coordinate.replace("\"", "″")

        content = content.replace(f"/deg//{degree}//deg/", coordinate)

    page["content"] = content

    return page

def convert_right(page):
    content = page["content"]

    if string_not_in_content(content, "/ri/", "Converting /ri/ to right-aligned text in transcription"):
        return page

    content = re.sub(r"\/ri\/([0-9]+?)\/(.+?)\//ri\/", r"{{right|offset=\1em|\2}}", content)
    content = re.sub(r"\/ri\//(.+?)\//ri\/", r"{{right|\1}}", content)

    page["content"] = content

    return page


def get_internal_chapter_name(chapter):
    chapter_num = chapter["chapter_num"]
    chapter_prefix = chapter["prefix"]
    if not chapter_prefix:
        chapter_prefix = "Chapter"
    chapter_title = chapter["title"]
    chapter_type = chapter["type"]

    if chapter_type != "numbered chapter" and chapter_type != "default":
        internal_chapter_name = chapter_title
    else:
        internal_chapter_name = f"{chapter_prefix} {chapter_num}"

    return internal_chapter_name

def generate_page_link(chapter, page_number_to_parse, mainspace_work_title):
    if chapter == "Front matter":
        chapter_link = mainspace_work_title
        if page_number_to_parse == "fro":
            page_anchor = "frontis"
        elif page_number_to_parse == "cov":
            page_anchor = "cover"
        else:
            page_anchor = "x"
    else:
        internal_chapter_name = get_internal_chapter_name(chapter)
        chapter_link = f"{mainspace_work_title}/{internal_chapter_name}"
        if page_number_to_parse == "i":
            page_anchor = "img"
        else:
            page_anchor = page_number_to_parse
    chapter_link = chapter_link + "#" + page_anchor

    return chapter_link

def get_chapter_link_in_relation(page, relation, chapters):
    marker = page["marker"]
    try:
        marker = int(marker)
    except ValueError:
        print_in_red(f"Error! Marker is not an integer. Marker found: {marker}")
        exit()
    
    
    
    chapter = get_chapter_from_page_num(chapters, marker)
    chapter_link = get_internal_chapter_name(chapter)

    chapter_link = chapter_link.split(" ")
    chapter_num = int(chapter_link[-1])

    if relation == "+":
        chapter_num += 1
    elif relation == "-":
        chapter_num -= 1

    chapter_link = chapter_link[0] + " " + str(chapter_num)

    return chapter_link


def convert_chapter_links(page, chapters, mainspace_work_title):
    content = page["content"]

    previous_chapter_phrases = [
        "my last chapter",
        "my preceding chapter",
        "my previous chapter",
        "the last chapter",
        "the preceding chapter",
        "the previous chapter",
    ]

    next_chapter_phrases = [
        "the following chapter",
        "my next chapter",
        "the next chapter",
    ]

    for phrase in previous_chapter_phrases:
        if f"/{phrase}/" in content.lower():
            print(f"/{phrase}/ found in content. Converting to previous chapter link.")
            previous_chapter_link = get_chapter_link_in_relation(page, "-", chapters)
            content = content.replace(f"/{phrase}/", f"[[{mainspace_work_title}/{previous_chapter_link}|{phrase}]]")
            content = content.replace(f"/{phrase.capitalize()}/", f"[[{mainspace_work_title}/{previous_chapter_link}|{phrase}]]")
    
    for phrase in next_chapter_phrases:
        if f"/{phrase}/" in content.lower():
            print(f"/{phrase}/ found in content. Converting to next chapter link.")
            next_chapter_link = get_chapter_link_in_relation(page, "+", chapters)
            content = content.replace(f"/{phrase}/", f"[[{mainspace_work_title}/{next_chapter_link}|{phrase}]]")
            content = content.replace(f"/{phrase.capitalize()}/", f"[[{mainspace_work_title}/{next_chapter_link}|{phrase}]]")

    if " /chapter " in content.lower():
        print("/chapter / found in content. Converting to chapter link.")
        chapter_links_pattern = r" \/([Cc]hapter) (.+?)\/"
        chapter_links = re.findall(chapter_links_pattern, content)

        print(chapter_links)

        for chapter_link in chapter_links:
            chapter_link = list(chapter_link)
            text_in_chapter_link = chapter_link[0]
            chapter_number_to_parse = chapter_link[1]
            original_chapter_number = chapter_number_to_parse
            try:
                chapter_number_to_parse = int(chapter_number_to_parse)
            except ValueError:
                chapter_number_to_parse = roman.fromRoman(chapter_number_to_parse)
            
            chapter_link = f" [[{mainspace_work_title}/{text_in_chapter_link} {chapter_number_to_parse}|{text_in_chapter_link} {original_chapter_number}]]"

            content = re.sub(chapter_links_pattern, chapter_link, content, count=1)

    page["content"] = content
    return page



def convert_page_links(page, chapters, mainspace_work_title):
    content = page["content"]

    frontispiece_phrases = [
        "a decoration",
        "a frontispiece",
        "an illustration",
        "frontispiece",
    ]

    for phrase in frontispiece_phrases:
        if f"/{phrase}/" in content.lower():
            print(f"/{phrase}/ found in content. Converting to page link.")
            content = content.replace(f"/{phrase}/", f"[[{mainspace_work_title}#frontis|{phrase}]]")
            content = content.replace(f"/{phrase.capitalize()}/", f"[[{mainspace_work_title}#frontis|{phrase}]]")

    
    page["content"] = content
    
    if string_not_in_content(content.lower(), "/page ", "Converting /page / to page links in transcription") and string_not_in_content(content.lower(), "/pg. ", "Converting /pg. / to page links in transcription") and string_not_in_content(content.lower(), "/pages ", "Converting /pages / to page links in transcription") and string_not_in_content(content.lower(), "/pp. ", "Converting /pp. / to page links in transcription"):
        return page

    page_links_pattern = r"\/([Pp]age) ([0-9]+?)\/"
    page_links = re.findall(page_links_pattern, content)
    # pages_links = re.findall(r"\/([Pp])ages ([0-9]+?)[-|–| to ]([0-9]+?)\/", content)
    # pp_links = re.findall(r"\/pp. ([0-9]+?)[-|–| to ]([0-9]+?)\/", content)
    # pages_commas_links = re.findall(r"\/pages (.+?)\/", content).split(","), for ... : if " and " in ..., split on " and " too
    # pg_links = re.findall(r"\/([Pp])g. ([0-9]+?)\/", content)

    for page_link in page_links:
        page_link = list(page_link)
        text_in_page_link = page_link[0]
        page_number_to_parse = page_link[1]
        chapter = get_chapter_from_page_num(chapters, page_number_to_parse)
        chapter_link = generate_page_link(chapter, page_number_to_parse, mainspace_work_title)

        # example: [[Sense and Sensibility/Chapter 1#3|Page 3]]
        page_link = f"[[{chapter_link}|{text_in_page_link} {page_number_to_parse}]]"

        content = re.sub(page_links_pattern, page_link, content, count=1)
    
    page["content"] = content

    return page


def convert_wikilinks(page, inline_continuations, page_data):
    content = page["content"]

    if string_not_in_content(content, "/li/", "Converting /li/ to wikilinks in transcription"):
        return page, inline_continuations
    

    # {{lps|link=Sense and Sensibility|pre=Sense and|post=Sensibility|lq="|rq="}}
    continuation_prefix = "lp"
    continuation_param = "link"

    content, inline_continuations = handle_inline_continuations(content, page, page_data, "li", continuation_prefix, continuation_param, inline_continuations)


    content = re.sub(r"\/li\//(.+?)\//li\/", r"[[\1]]", content)

    page["content"] = content


    return page, inline_continuations


########################## block elements ##########################

def convert_block_element(page, abbreviation, template_name, block_continuations):
    block_tag = get_plain_tag(abbreviation)
    content = page["content"]

    if len(block_continuations.items()) == 0:
        if string_not_in_content(content, block_tag, f"Converting {block_tag} to {template_name} in transcription"):
            return page
    
    if abbreviation in block_continuations:
        start_template = f"{{{{{template_name}/s}}}}"
        end_template = f"{{{{{template_name}/e}}}}"

        block_continuations, page = handle_block_continuations(page, abbreviation, block_continuations, start_template, end_template)
    
    block_start_tag = get_noparams_start_tag(abbreviation)
    block_end_tag = get_end_tag(abbreviation)

    number_of_start_tags = content.count(block_start_tag)
    number_of_end_tags = content.count(block_end_tag)

    if number_of_start_tags > number_of_end_tags:
        start_template = f"{{{{{template_name}/s}}}}"
        end_template = f"{{{{{template_name}/e}}}}"

        block_continuations, page = handle_block_continuations(page, abbreviation, block_continuations, start_template, end_template)
        # page, block_continuations = handle_block_continuations(page, block_continuations, block_start_tag, block_end_tag)
        # print_in_red(f"Number of {block_start_tag} tags does not match number of {block_end_tag} tags in transcription")
        # exit()
    
    content = page["content"]

    content = content.replace(block_start_tag, f"{{{{{template_name}|")
    content = content.replace(block_end_tag, "}}")

    page["content"] = content

    return page

"""
def add_toc_to_transcription(page, toc, block_continuations):

    content = page["content"]
    # header = page["header"]
    # footer = page["footer"]

    toc_tag = get_plain_tag("toc")
    spl_tag = get_plain_tag("spl")

    if string_not_in_content(content, toc_tag, "Adding TOC to transcription"):
        # Your mind is in the right place. But still, how are we going to know which TOC split it is if there's no iterator outside this function?
        return block_continuations, page
    
    if spl_tag in toc:
        toc_split = toc.split("\n" + spl_tag + "\n")
        if "toc-block" in toc:
            start_template = "<div class=\"toc-block\">"
            end_template = "</div>"
        else:
            start_template = "{{TOC begin}}"
            end_template = "{{TOC end}}"

        block_continuations, page = handle_block_continuations(page, toc_tag, block_continuations, start_template, end_template, split_list=toc_split)

        content = page["content"] # make sure to update content after handling formatting continuations

    else:
        content = convert_simple_markup(content, "toc", toc)


    page["content"] = content
    # page["header"] = header
    # page["footer"] = footer

    return block_continuations, page
"""

def convert_block_elements(page, block_continuations):
    for abbreviation, template_name in block_elements.items():
        page = convert_block_element(page, abbreviation, template_name, block_continuations)
        # abbreviation_start_tag = get_noparams_start_tag(abbreviation)
        # if abbreviation_start_tag in page["content"]:
            # start_template = f"{{{{{template_name}/s}}}}"
            # end_template = f"{{{{{template_name}/e}}}}"

            # block_continuations, page = handle_block_continuations(page, abbreviation, block_continuations, start_template, end_template)
    return block_continuations, page

def convert_simple_markup(content, abbreviation, template):

    abbreviation = get_plain_tag(abbreviation)

    if string_not_in_content(content, abbreviation,  f"Replacing {abbreviation} with {template} in transcription"):
        return content

    if abbreviation == "/-/":
        template = "/" + template + "/"
    elif abbreviation == "/toc/":
        template = template
    else:
        template = "{{" + template + "}}"
    
    content = content.replace(abbreviation, template)
    content = content.replace("{{bar|2}}-", "{{bar|2}}")

    return content

def convert_basic_elements(page):
    content = page["content"]

    for abbreviation, template in basic_elements.items():
        content = convert_simple_markup(content, abbreviation, template)

    page["content"] = content
    return page


def remove_split_tag(page):
    content = page["content"]

    split_tag = "<spl>"

    if string_not_in_content(content, split_tag, "Removing split tags (used for splitting up adjacent QT markup for parsing) from transcription"):
        return page

    content = content.replace(split_tag, "")

    page["content"] = content

    return page



################################## poems ##################################

def convert_fqms(pattern, text):
    quotation_symbols = [
        # "'",
        '"',
        "{{\" '}}",
        "{{' \"}}",
    ]

    patterns = [
        pattern,
        ":",
        "\n",
        r"$",
    ]

    # print(text)
    # text = text.replace(f"{pattern}\"", f"{pattern}{{{{fqm}}}}")
    for symbol in quotation_symbols:
        for pattern in patterns:
            if symbol == '"':
                fqm = "{{fqm}}"
            else:
                fqm = f"{{{{fqm|{symbol}}}}}"
            text = re.sub(rf"{pattern}{symbol}", rf"{pattern}{fqm}", text)
    # print("Text after conversion:")
    # print(text)
    return text

def handle_fqm(text):
    print("Beginning")
    # text = convert_fqms("{{ppoem|class=poem|\n", text)
    # print(text)
    # text = text.replace("{{ppoem|class=poem|\n\"", "{{ppoem|class=poem|\n{{fqm}}")
    # text = text.replace("{{ppoem|class=poem|\n\'", "{{ppoem|class=poem|\n{{fqm|'}}")
    poem_pattern = r'\{\{ppoem\|class=.+?\|([.\s\S]*?)\n\}\}'
    poems = re.findall(poem_pattern, text)

    # remove poems from text so that they can be parsed

    # fix fqm in beginning of stanzas
    for poem in poems:
        print("For poem in poems")
        fixed_poem = convert_fqms("\n\n", poem)
        text = text.replace(poem, fixed_poem)
    # print("Text after beginning fqm:" + text)
    
    # correct when italics are mistakenly converted to fqm
    text = text.replace("{{fqm|'}}'", "''")

    print("Text after conversion:")
    print(text)
    return text

def handle_poem_continuations(poem_continuations): # unused for now, until poem continuation logic gets lengthy
    poem_continuations.append("follow")
    return poem_continuations

def detect_and_remove_nop_from_poem_continuation(content, end_continuation):
    is_stanza = False
    if "{{nop}}" in content or "/n/" in content:
        print("WE GOT TO STANZA")
        content = content.replace("\n{{nop}}", "")
        content = content.replace("\n/n/", "")
        end_continuation = "stanza"
        is_stanza = True
    return content, end_continuation, is_stanza

def convert_poems(page, poem_continuations, convert_fqms):
    content = page["content"]

    if len(poem_continuations) == 0:
        if string_not_in_content(content, "/po/", "Converting poems") and string_not_in_content(content, "/poi/", "Converting italic poems"):
            return poem_continuations, page

    # if there's an existing poem continuation, handle that before parsing other poems
    # WHEN THERE IS A CONTINUING ITALIC POEM, THAT WILL BE AN ISSUE. Need to make poem continuations into DICTIONARY to handle this
    if len(poem_continuations) > 0:
        start_continuation = poem_continuations[0]
        poem_continuations = []
        end_continuation = None
        if "//po/" in content or "//poi/" in content:
            content = content.replace("//po/", "}}", 1)
            content = content.replace("//poi/", "}}", 1)
        else:
            content += "\n}}"
            content, end_continuation, is_stanza = detect_and_remove_nop_from_poem_continuation(content, end_continuation)
            if is_stanza:
                pass
            elif "/f/" in content:
                content = content.replace("\n/f/", "")
                end_continuation = "same-line"
            else:
                print("WE DIDNT GET TO STANZA :(")
                end_continuation = "follow"
            
            poem_continuations.append(end_continuation)
        
        if end_continuation:
            end_continuation_display = f"end={end_continuation}|"
        else:
            end_continuation_display = ""

        
        content = f"{{{{ppoem|class=poem|start={start_continuation}|{end_continuation_display}\n" + content

    
    # parse poems that are not continued
    pattern = r"\/po\//([\s\S]+?)\//po\/"
    italic_pattern = r"\/poi\//([\s\S]+?)\//poi\/"
    replacement = r"{{ppoem|class=poem|\1}}"
    italic_replacement = r"{{ppoem|class=poem-italic|\1}}"
    content = re.sub(pattern, replacement, content)
    content = re.sub(italic_pattern, italic_replacement, content)

    lang_in_poem = re.findall(r"\|(..)\n", content)

    if len(lang_in_poem) > 0:
        for lang in lang_in_poem:
            content = content.replace(f"|{lang}\n", f"|lang={lang}|\n")
    
    # if /po// tag still in content after conversions, then start the continuation process
    if "/po//" in content or "/poi//" in content:
        end_continuation = "follow"
        content, end_continuation, is_stanza = detect_and_remove_nop_from_poem_continuation(content, end_continuation)
        content = content.replace("/po//", f"{{{{ppoem|class=poem|end={end_continuation}|")
        content = content.replace("/poi//", f"{{{{ppoem|class=poem-italic|end={end_continuation}|")
        poem_continuations.append(end_continuation)
        content += "\n}}"

    if convert_fqms != "n":
        content = handle_fqm(content)

    page["content"] = content
    return poem_continuations, page




################################## images ##################################




def convert_images(page, image_data, img_num):
    content = page["content"]

    img_tag = get_plain_tag("img")
    fle_tag = get_plain_tag("fle")

    if string_not_in_content(content, img_tag, "Converting images") and string_not_in_content(content, fle_tag, "Converting fleuron images"):
        return img_num, page
    
    image_tags = [
        "img",
        "fle",
        "plt",
        "fig",
    ]
    

    images_in_page = get_string_from_lines(content, image_tags)

    # pattern = r"\/img\/([0-9]+)\/"
    # images = re.findall(pattern, content)
    for line_num, image_tag in reversed(images_in_page.items()):
        image_number_pattern = r"\/n=([0-9]+)\/"
        image_number = re.search(image_number_pattern, image_tag)
        if image_number:
            image_number = image_number.group(1)
            image = image_data[int(image_number) - 1]
        else:
            image = image_data[img_num]
            img_num += 1
        image_filename = get_image_filename(image)
        image_caption = image["caption"]
        if image_caption:
            caption_display = f"\n | caption = {image_caption}"
        else:
            caption_display = ""
        image_size = image["size"]
        template_name = "FreedImg"

        image_settings = image["settings"]

        if type(image_settings) == str:
            image_settings = image_settings.split(",")

        float_display = ""
        float_setting = ""

        for setting in image_settings:
            if "fl=" in setting:
                template_name = "Img float"
                float_setting = setting.split("=")[1]
                if float_setting == "r":
                    float_setting = "right"
                elif float_setting == "l":
                    float_setting = "left"
        
    
        if float_setting:
            float_display = f"\n | float = {float_setting}"
            image_size = 150



        image_text = f"""{{{{{template_name}
 | file = {image_filename}{caption_display}
 | width = {image_size}px{float_display}
}}}}"""

        content = replace_line(content, image_text, line_num)

    if " | float = " in content:
        content = re.sub("float = left\n}}\n\n", "float = left\n}}", content)
        content = re.sub("float = right\n}}\n\n", "float = right\n}}", content)
        content = re.sub("float = left\n}}\n", "float = left\n}}", content)
        content = re.sub("float = right\n}}\n", "float = right\n}}", content)

    # content = re.sub(pattern, r"{{img|\1}}", content)

    page["content"] = content

    return img_num, page



def is_image_page(page):
    content = page["content"]
    img_tag = get_plain_tag("img")
    content_lines = content.split("\n\n")

    if len(content_lines) == 1 and img_tag in content:
        return True

    return False

def get_hyphenated_word_data(next_page_num, page_data, word_start, word_start_page):

    for page_num in range(next_page_num, len(page_data)):
        page = page_data[page_num]
        content = page["content"]
        page_quality = page["page_quality"]
        marker = page["marker"]
        if marker.isdigit() and page_quality != "0" and not is_image_page(page):
            content = content.split(" ")
            word_end = content[0]
            marker = page["marker"]
            hyphenated_word_data = {
                "start": word_start,
                "start_page": word_start_page,
                "end": word_end,
                "end_page": marker,
            }
            return hyphenated_word_data

    # pass

def handle_hyphenated_word_continuations(page, hyphenated_word_continuations, page_data):
    content = page["content"]

    page_num = page["marker"]
    overall_page_num = page["page_num"] - 1
    
    if len(hyphenated_word_continuations) != 0:
        continuation = hyphenated_word_continuations[0]
        word_start = continuation["start"]
        word_end = continuation["end"]
        end_page = continuation["end_page"]
        if page_num == end_page:
            print("Inserting hyphenation end template...")
            content = content.split(" ")
            content.pop(0)
            hyphenated_word_end = f"{{{{hwe|s={word_start}|e={word_end}}}}}"
            content = hyphenated_word_end + " " + " ".join(content)
            hyphenated_word_continuations = []
    else:
        content = content.split(" ")
        last_word_in_content = content[-1]
        # page_marker = page["marker"]
        if last_word_in_content.endswith("-"):
            next_page_num = overall_page_num + 1
            next_page = page_data[next_page_num]
            next_page_quality = next_page["page_quality"]
            next_page_marker = next_page["marker"]
            if not next_page_marker.isdigit() or next_page_quality == "0" or is_image_page(next_page):
                print("Word found that's hyphenated between images. Handling hyphenation continuations...")
                word_start = content.pop()
                word_start = word_start[:-1]
                word_start_page = page_num
                hyphenated_word_data = get_hyphenated_word_data(next_page_num, page_data, word_start, word_start_page)
                hyphenated_word_continuations.append(hyphenated_word_data)
                word_end = hyphenated_word_data["end"]
                hyphenated_word_start = f"{{{{hws|s={word_start}|e={word_end}}}}}"
                content.append(hyphenated_word_start)

                
                # hyphenated_word_continuations.append({
                #     "start": last_word_in_content,
                #     "end": "",
                #     "end_page": next_page_marker,
                # })
        content = " ".join(content)
    
    page["content"] = content

    return hyphenated_word_continuations, page
    

{
    "start": "an",
    "start_page": 184,
    "end": "grily,",
    "end_page": 185,
}



################################## parse pages ##################################

def parse_transcription_pages(page_data, image_data, transcription_text, chapters, sections, mainspace_work_title, title, toc, chapter_format, section_format, chapter_beginning_formatting, drop_initials_float_quotes, convert_fqms, page_break_string, chapter_type, section_type, illustrations, work_type_name, first_section_automatically_after_chapter, is_transclusion_sectioned):
    print("Parsing QT markup into wiki markup...")
    new_page_data = []
    img_num = 0
    # chapter_num = 0
    # part_num = 0
    overall_chapter_num = 0
    overall_section_num = 0
    poem_continuations = []
    block_continuations = {} # dictionary because of TOC needing split indices, CHANGE THIS LATER NOT SEMANTICALLY CORRECT
    inline_continuations = []
    reference_continuations = []
    hyphenated_word_continuations = []
    section_transclusion_continuations = []
    chapter_half_is_in_work = check_if_chapter_half_in_work(transcription_text)
    for page in page_data:
        page_num = page["page_num"]
        print(f"Parsing page {page_num}...")

        page = add_half_to_transcription(page, title)
        page = add_space_to_apostrophe_quotes(page)
        if chapter_beginning_formatting == "sc" or not chapter_beginning_formatting:
            page = format_chapter_beginning_to_smallcaps(page, work_type_name)
        elif chapter_beginning_formatting == "di" or chapter_beginning_formatting == "dii" or chapter_beginning_formatting == "li" or chapter_beginning_formatting == "lii":
            page = format_chapter_beginning_to_drop_initial(page, drop_initials_float_quotes, chapter_beginning_formatting, image_data)
        else:
            # page = format_chapter_beginning_to_large_initial(page)
            pass
        img_num, page = format_arbitrary_drop_inital(page, image_data, img_num)
        page = convert_complex_dhr(page)
        page = convert_complex_stars(page)
        page = convert_basic_elements(page)
        page = convert_title_headers(page, title)
        block_continuations, page = convert_block_elements(page, block_continuations)
        poem_continuations, page = convert_poems(page, poem_continuations, convert_fqms) # done
        page = convert_italics(page)
        page = convert_smallcaps(page)
        page = convert_degrees(page)
        page = convert_right(page)
        page = convert_language_tags(page)
        page, inline_continuations = convert_wikilinks(page, inline_continuations, page_data)
        page = convert_author_links(page)


        img_num, page = convert_images(page, image_data, img_num)
        page = convert_page_links(page, chapters, mainspace_work_title)
        page = convert_chapter_links(page, chapters, mainspace_work_title)


        page, reference_continuations = handle_references(page, reference_continuations)

        page = handle_forced_page_breaks(page, page_break_string)

        block_continuations, page = add_toc_to_transcription(page, toc, block_continuations)
        page = add_illustrations_to_transcription(page, illustrations)
        overall_chapter_num, page = convert_chapter_headers(page, chapters, overall_chapter_num, chapter_format, chapter_type, chapter_half_is_in_work, first_section_automatically_after_chapter)
        overall_section_num, page = convert_section_headers(page, sections, overall_section_num, section_format, section_type)
        if is_transclusion_sectioned:
            page = add_section_transclusion_tags(page, chapters, overall_chapter_num)
            print("AM I EVEN GETTING HERE")

        page = remove_split_tag(page)

        # If there's an image page between a hyphenated word, the hyphenation template should be used
        hyphenated_word_continuations, page = handle_hyphenated_word_continuations(page, hyphenated_word_continuations, page_data)


        new_page_data.append(page)
        # print(page)
        # if page_num > 80:
            # exit()
    print_in_green("All transcription pages parsed successfully!")
    return new_page_data




################################## insert pages ##################################

def get_transcription_header(transcription_text):
    transcription_lines = transcription_text.split("\n\n")
    transcription_header = []
    for line in transcription_lines:
        line_length = len(line)
        if (line.startswith("-") or line.startswith("—")) and line_length <= 4:
            break
        transcription_header.append(line)

    transcription_header = "\n\n".join(transcription_header)

    return transcription_header
        
{'page_num': 122, 'header': '', 'footer': '', 'content': '', 'page_quality': '0', 'marker': '107', 'type': ''}

def generate_header_footer_text(header, footer):
    header_tag = "head"
    footer_tag = "foot"
    header_start_tag = get_noparams_start_tag(header_tag)
    header_end_tag = get_end_tag(header_tag)
    footer_start_tag = get_noparams_start_tag(footer_tag)
    footer_end_tag = get_end_tag(footer_tag)

    header_text = ""
    footer_text = ""

    if header:
        header_text = f"{header_start_tag}\n{header}\n{header_end_tag}\n\n"
    if footer:
        footer_text = f"\n\n{footer_start_tag}\n{footer}\n{footer_end_tag}"

    return header_text, footer_text

def generate_marker_text(marker, quality, page_format, previous_page_format, content):
    if quality == "0" or (marker == "ad" and not content):
        marker_text = "—"
    else:
        marker_text = "-"
    
    if marker:
        marker_text += marker
    
    if page_format != previous_page_format:
        if previous_page_format == "roman":
            marker_text += "n"
        elif previous_page_format == "numeric":
            marker_text += "r"

    if quality != "0":
        marker_text += "\n\n"

    return marker_text

def insert_parsed_pages(page_data, transcription_text):
    print("Inserting parsed pages into transcription text...")
    transcription_header = get_transcription_header(transcription_text)

    transcription_text_pages = []

    for page_num, page in enumerate(page_data):
        content = page["content"]
        header = page["header"]
        footer = page["footer"]
        marker = page["marker"]
        quality = page["page_quality"]
        previous_page = page_data[page_num - 1]
        previous_page_format = previous_page["format"]
        page_format = page["format"]

        marker_text = generate_marker_text(marker, quality, page_format, previous_page_format, content)

        if quality == "0":
            page_text = marker_text
        else:
            if (marker == "ad" or marker == "adv") and not content:
                page_text = marker_text
            else:
                header_text, footer_text = generate_header_footer_text(header, footer)
                page_text = marker_text + header_text + content + footer_text
        
        transcription_text_pages.append(page_text)
    
    transcription_text_pages = "\n\n".join(transcription_text_pages)
    transcription_text_pages = transcription_header + "\n\n" + transcription_text_pages

    transcription_text_pages = remove_triple_newlines(transcription_text_pages)

    # fix introduction issues etc.
    transcription_text_pages = re.sub(r"\{\{ph\|class=chapter num\|\/cpre\/ \/cnum\/\}\}\n\{\{ph\|class=chapter title\|(.+?)\}\}\n", r"{{ph|class=chapter|\1}}\n", transcription_text_pages)
    transcription_text_pages = transcription_text_pages.replace("-1|/cnum/.|", "-1||")
    transcription_text_pages = transcription_text_pages.replace("-1|/cnum/|", "-1||")
    transcription_text_pages = transcription_text_pages.replace("wst-toc-aux|/cnum/|", "wst-toc-aux||")
    transcription_text_pages = transcription_text_pages.replace("wst-toc-aux|/cnum/.|", "wst-toc-aux||")
    transcription_text_pages = re.sub(r"/Chapter 1\|(.+?)\]\]\|i\}\}", r"/Chapter 1|\1]]|1}}", transcription_text_pages)
    transcription_text_pages = re.sub(r"/Chapter 1\|(.+?)\]\]\|iii\}\}", r"/Chapter 1|\1]]|3}}", transcription_text_pages)

    print_in_green("Transcription text page generated from parsed pages.")

    return transcription_text_pages






# new_page = format_chapter_beginnings_to_smallcaps(text)

# save_page(page, site, new_page, "Formatting chapter beginnings to smallcaps (test)")


# chapters = get_chapters(text)
# print(get_chapters(text))
# toc = generate_toc(chapters)
# half = f"{{{{c|{{{{larger|{title}}}}}}}}}"

# text = convert_simple_markup(text, "toc", toc)
# text = convert_simple_markup(text, "toc", toc)

# print(work_data)
# 

# print(toc)