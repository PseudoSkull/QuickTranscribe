# WS_collection

import pywikibot
import re
import roman

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page
from handle_title_case import convert_to_title_case
from handle_projectfiles import write_to_json_file, get_json_data
from handle_wikisource_conf import get_regex_match
from handle_commons import get_image_filename


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
    "d": "dhr",
    "end": "dhr|2}}\n{{c|{{asc|The end}}",
    "n": "nop",
    "peh": "peh",
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
    "hi": "hanging indent",
}

named_chapter_pattern = r"\/ch\/\/.+?\n\n"
empty_chapter_pattern = r"\/ch\/\n\n"

chapter_pattern = rf"({named_chapter_pattern}|{empty_chapter_pattern})"


qt_markup = {
    "ch": "",
    "po": "",
    "al": "",
    "half": "",
    "toc": "",
}








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


def get_bare_title(mainspace_work_title):
    return mainspace_work_title.split(" (")[0]


## TAGS ##

def get_plain_tag(abbreviation):
    return f"/{abbreviation}/"

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

def get_string_from_lines(content, string):
    content_split_lines = content.split("\n")

    matches = {}

    for line_num, line in enumerate(content_split_lines):
        if string in line:
            matches[line_num] = line
    
    return matches

def replace_line(content, replacement, line_num):
    content_split_lines = content.split("\n")
    content_split_lines[line_num] = replacement
    return "\n".join(content_split_lines)


def format_form_tag(row, replacements):
    for tag, replacement in replacements.items():
        tag = get_plain_tag(tag)
        row = row.replace(tag, replacement)
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
    end_tag = get_end_tag(tag)
    while 1:
        if tag in block_continuations:
            print(f"Formatting continuation of {tag} in progress...")
            continuation_index = block_continuations[tag]
            
            # handle headers/footers

            if continuation_index == 0:
                footer = add_to_footer(end_template, footer)
                block_continuations[tag] += 1
            else:
                header = add_to_header(start_template, header)
                if end_tag not in content:
                    footer = add_to_footer(end_template, footer)
                    block_continuations[tag] += 1
                else:
                    print(f"Formatting continuation of {tag} complete.")
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
            print_in_green(f"Roman numeral found: {roman_numeral}")
        except roman.InvalidRomanNumeralError:
            print_in_yellow(f"{roman_numeral} is not a valid roman numeral.")

    return result

def determine_if_books_or_parts_exist(text):
    if "/bk/" in text or "/pt/" in text:
        return True
    return False

def get_chapter_data(text, page_data, chapter_prefix, chapters_are_subpages_of_parts):
    print("Getting chapter data...")
    chapters_json_file = "chapter_data.json"
    chapters = get_json_data(chapters_json_file)
    if chapters:
        print_in_green("Chapter data JSON found!")
        return chapters
    parts_exist = determine_if_books_or_parts_exist(text)

    chapter_num = 0

    if parts_exist:
        part_num = 0
    else:
        part_num = None

    chapters = []

    if "/ch/" in text:
        print_in_green("Chapters found in transcription text. Getting chapter data...")

        previous_chapter = None
        section_tag = get_plain_tag("sec")

        for page in page_data:
            page_num = page["marker"]
            content = page["content"]
            chapter_has_name = "/ch//" in content

            # if toc_is_auxiliary:
            if chapter_has_name:
                chapter_pattern = r"\/ch\/\/(.+?)\n\n"
            else:
                chapter_pattern = r"(\/ch\/)\n"

            book_pattern = r"(\/bk\/)"
            part_pattern = r"(\/pt\/)"

            all_chapter_types_pattern = rf"{chapter_pattern}|{book_pattern}|{part_pattern}"

            # page_number_pattern = r"\n\n-([0-9]+)\n\n"
            # chapter_and_page_pattern = rf"{page_number_pattern}{chapter_pattern}"
            chapter_matches = re.findall(all_chapter_types_pattern, content)
            chapter_splice_points = get_chapter_splice_points(text)

            for match in chapter_matches:
                is_chapter = match[0]
                is_book = match[1]
                is_part = match[2]
                # print(match)
                chapter = {}

                if is_book or is_part:
                    part_num += 1
                    if is_book:
                        chapter["prefix"] = "Book"
                        match = is_book
                    elif is_part:
                        chapter["prefix"] = "Part"
                        match = is_part
                    chapter["chapter_num"] = part_num
                    # chapter["subchapters"] = []

                    if chapters_are_subpages_of_parts == "y" or not chapters_are_subpages_of_parts:
                        chapter_num = 0

                else:
                    chapter_num += 1
                    if chapter_prefix == "n":
                        chapter["prefix"] = None
                    elif not chapter_prefix:
                        chapter["prefix"] = "Chapter"
                    else:
                        chapter["prefix"] = chapter_prefix
                    chapter["chapter_num"] = chapter_num
                    match = is_chapter


                if chapter_has_name:
                    chapter["title"] = None
                else:
                    title = convert_to_title_case(match)
                    chapter["title"] = title
                
                if type(page_num) == str and page_num.isdigit():
                    chapter["page_num"] = int(page_num)
                else:
                    chapter["page_num"] = page_num
                
                chapter["refs"] = False # for now
                chapter["part_num"] = part_num
                chapter["has_sections"] = False

                splice_chapter = False
                if chapter_splice_points:
                    if chapter_num in chapter_splice_points:
                        splice_chapter = True
                chapter["splice"] = splice_chapter

                chapters.append(chapter)

        # START PREVIOUS CHAPTER LOGIC, to find sections within next pages
                previous_chapter = chapter
                previous_chapter_index = len(chapters) - 1
            
            if section_tag in content:
                previous_chapter["has_sections"] = True
                chapters[previous_chapter_index] = previous_chapter
        # END PREVIOUS CHAPTER LOGIC
    else:
        print_in_yellow("No chapters found in transcription text. Assuming this is a front-matter-only work...")

    write_to_json_file(chapters_json_file, chapters)
    return chapters

def get_chapter_from_page_num(chapters, page_data, page_num, overall_page_num):
    try:
        page_num = int(page_num)
    except ValueError:
        print_in_red(f"Page number {page_num} is not an integer.")
        exit()
    for chapter_num, chapter in enumerate(chapters):
        # print(f"Chapter {chapter}")
        # print(f"Page {page_num}")
        chapter_page_num = chapter["page_num"]
        try:
            next_chapter = chapters[chapter_num + 1]
            next_chapter_page_num = next_chapter["page_num"]
        except IndexError:
            next_chapter_page_num = chapter_page_num + 1000 # arbitrary number to make sure it's sufficiently higher than current page number
            
        
        # if previous_chapter_page_num == 0 and chapter_page_num > overall_page_num:
        #     front_matter = {}
        #     front_matter["chapter_num"] = 0
        #     front_matter["part_num"] = 0
        #     front_matter["page_num"] = 0
        # print(f"Type of chapter page num: {type(chapter_page_num)}. Type of page num: {type(page_num)} Type of next chapter page num: {type(next_chapter_page_num)}")
        if chapter_page_num < page_num and next_chapter_page_num > page_num:
            return chapter

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
    

def get_section_data(chapters, page_data, transcription_text):
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
        for overall_page_num, page in enumerate(page_data):
            section_pattern = r"(\/sec\/)\n"

            try:
                page_num = int(page["marker"])
            except ValueError:
                page_num = page["marker"]
            content = page["content"]
            
            section_matches = re.findall(section_pattern, content)

            for match in section_matches:
                chapter = get_chapter_from_page_num(chapters, page_data, page_num, overall_page_num)
                # chapter = {}
                previous_chapter_num = chapter_num
                chapter_num = chapter["chapter_num"]
                chapter_start_page_num = chapter["page_num"]
                part_num = chapter["part_num"]
                
                # print(sections)

                chapter_has_sections = chapter["has_sections"]
                if not chapter_has_sections:
                    print_in_red(f"ERROR: Chapter data says chapter has no sections, but section was found in chapter when collecting section data! Something is wrong with the code. Please fix it. Chapter num: {chapter_num}, part num: {part_num}, page num: {page_num}, overall page num: {overall_page_num}, match: {match}")
                    exit()
                else:
                    if chapter_num != previous_chapter_num:
                        section_num = 1
                        unreadable_overall_page_num = None # Change later when logic can do this
                        sections = add_section(sections, section_num, chapter_num, part_num, chapter_start_page_num, unreadable_overall_page_num)
                
                # add first section of chapter if it's the first time encountering that chapter
                
                
                section_num += 1

                # add section
                sections = add_section(sections, section_num, chapter_num, part_num, page_num, overall_page_num)
                # section_num += 1


    else:
        print_in_yellow("No sections found in transcription text.")

    write_to_json_file(sections_json_file, sections)
    return sections
    

def get_aux_toc_items(chapters, mainspace_work_title):
    aux_toc_items = []
    spacing = ""
    is_subchapter = False
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
        else:
            spacing = ""
            is_subchapter = True
            # subchapters = chapter["subchapters"]
            # aux_subchapters = get_aux_toc_items(subchapters, mainspace_work_title, ":")
            # spacing = ":"
            # aux_subchapters = "\n".join(aux_subchapters)
        chapter_numbered_name = f"{chapter_prefix}{chapter_num}"

        chapter_title = chapter["title"]
        
        if chapter_title:
            # aux_toc_entry = f"* [[{mainspace_work_title}/|{chapter_title}]]"
            aux_toc_entry = f"{spacing}* [[{mainspace_work_title}/{chapter_numbered_name}|{chapter_numbered_name}: {chapter_title}]]"
        else:
            aux_toc_entry = f"{spacing}* [[{mainspace_work_title}/{chapter_numbered_name}|{chapter_numbered_name}]]"

        # if aux_subchapters:
        #     aux_toc_entry += "\n" + aux_subchapters

        aux_toc_items.append(aux_toc_entry)
    
    return aux_toc_items    

def generate_toc(chapters, mainspace_work_title, toc_format, toc_is_auxiliary, smallcaps=True, header=False):
    print("Generating TOC...")

    if toc_is_auxiliary:
        # toc_format = "auxiliary"
        aux_toc_beginning = "{{AuxTOC|\n"
        aux_toc_ending = "\n}}"
        # aux_toc_items = []
        aux_toc_items = get_aux_toc_items(chapters, mainspace_work_title)
        aux_toc_items = "\n".join(aux_toc_items)
        aux_toc = aux_toc_beginning + aux_toc_items + aux_toc_ending
        return aux_toc

    if smallcaps:
        smallcaps = "yes"
    else:
        smallcaps = "no"
    if header:
        header = f"\n{{{{TOC row 1-1-1|{{{{x-smaller|CHAPTER}}}}||{{{{x-smaller|PAGE}}}}}}"
    else:
        header = ""
    # WHY DOES
    toc_beginning = f"""c|{{{{larger|CONTENTS}}}}}}}}
{{{{TOC begin}}}}{header}
"""
    print(f"TOC BEGINNING IS {toc_beginning} BEFORE")
#     toc_beginning = f"""{{{{c|{{{{larger|CONTENTS}}}}}}}}
# <div class="toc-block">
# """
    toc_ending = """{{TOC end"""
    # toc_ending = "</div>"

    for chapter_num, chapter in enumerate(chapters):
        page_num = chapter["page_num"]
        chapter_title = chapter["title"]
        splice = chapter["splice"]
        chapter_num = chapter_num + 1 # 1-indexed rather than 0
        chapter_num_as_roman = roman.toRoman(chapter_num)
        toc_link = f"[[{mainspace_work_title}/Chapter {chapter_num}|{chapter_title}]]"

        if toc_format:
            toc_row = toc_format

            replacements = {
                "cnum": str(chapter_num_as_roman),
                "cnam": toc_link,
                "pnum": str(page_num),
            }
            
            toc_row = format_form_tag(toc_row, replacements)

            toc_beginning += toc_row + "\n"

            if splice:
                splice_tag = get_plain_tag("spl")
                toc_beginning += splice_tag + "\n"

        else:
            toc_beginning += f"{{{{TOC row 1-1-1|{chapter_num_as_roman}|{toc_link}|{page_num}}}}}\n"
    print(f"TOC BEGINNING IS {toc_beginning} AFTER")
    toc = toc_beginning + toc_ending
    print_in_green("TOC generated.")
    return toc

def format_chapter_beginning_to_smallcaps(page):
    content = page['content']

    if string_not_in_content(content, "/ch/", "Formatting chapter beginning to smallcaps"):
        return page
    
    quote_pattern = r"\"?\'?"
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

def format_chapter_beginning_to_drop_initial(page, drop_initials_float_quotes):

    content = page["content"]

    if string_not_in_content(content, "/ch/", "Formatting chapter beginning to drop initial"):
        return page
    
    quote_pattern = r"\"?\'?"
    chapter_beginning_pattern = rf"{chapter_pattern}(.)"

    chapter_beginning_pattern = rf"{chapter_pattern}(.)(.)"

    chapter_beginning = re.search(chapter_beginning_pattern, content)

    chapter_heading = chapter_beginning.group(1)
    first_letter = chapter_beginning.group(2)
    second_letter = chapter_beginning.group(3)

    drop_initial_quotes = [
        '"',
        "'",
    ]

    if first_letter in drop_initial_quotes:
        if drop_initials_float_quotes == "y":
            replacement = r"\1{{di|\3|fl=\2}}"
        else:
            replacement = r"\1{{di|\2\3}}"

        content = re.sub(chapter_beginning_pattern, replacement, content)
    else:
        replacement = r"\1{{di|\2}}\3"
        content = re.sub(chapter_beginning_pattern, replacement, content)
    
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
        start_template = "<div class=\"toc-block\">"
        end_template = "</div>"

        block_continuations, page = handle_block_continuations(page, toc_tag, block_continuations, start_template, end_template, split_list=toc_split)

        content = page["content"] # make sure to update content after handling formatting continuations

    else:
        content = convert_simple_markup(content, "toc", toc)


    page["content"] = content
    # page["header"] = header
    # page["footer"] = footer

    return block_continuations, page

def convert_chapter_headers(page, chapters, overall_chapter_num, chapter_format, chapter_type):
    # IF MULTIPLE CHAPTERS, THEY NEED TO BE SECTIONED OUT WITH ANCHORS!!!!!
    content = page["content"]

    ch_tag = get_plain_tag("ch")
    bk_tag = get_plain_tag("bk")
    pt_tag = get_plain_tag("pt")

    if string_not_in_content(content, ch_tag, "Converting chapter headings") and string_not_in_content(content, bk_tag, "Converting book headings") and string_not_in_content(content, pt_tag, "Converting part headings"):
        return overall_chapter_num, page


    chapters_in_page = get_string_from_lines(content, ch_tag)
    books_in_page = get_string_from_lines(content, bk_tag)
    parts_in_page = get_string_from_lines(content, pt_tag)

    if books_in_page:
        parts_in_page = books_in_page # they're the same, so make it the same standard

    for line_num, pt_tag in parts_in_page.items():

        overall_chapter_num += 1
        # part_num += 1

        overall_chapter_num_zero_indexed = overall_chapter_num - 1
        part = chapters[overall_chapter_num_zero_indexed]

        
        # chapter_num = 0 # resetting chapter_num to 0, because we're starting a new part. It won't actually display as 0 necessarily, because for displaying the chapter, the chapter_num in the data is used instead of the incremented value.
        part_num = part["chapter_num"]
        roman_part_num = roman.toRoman(part_num)
        part_prefix = part["prefix"]
        part_text = f"{{{{ph|class=part-header|{part_prefix} {roman_part_num}}}}}"

        content = replace_line(content, part_text, line_num)

    for line_num, ch_tag in chapters_in_page.items():
        # part_num_zero_indexed = part_num - 1
        # chapter = chapters[chapter_num]

        overall_chapter_num += 1

        overall_chapter_num_zero_indexed = overall_chapter_num - 1
        chapter = chapters[overall_chapter_num_zero_indexed]

        real_chapter_num = chapter["chapter_num"]
        roman_chapter_num = roman.toRoman(real_chapter_num)
        if chapter_type == "num":
            displayed_section_num = real_chapter_num
        else:
            displayed_section_num = roman_chapter_num
        
        chapter_prefix = chapter["prefix"]
        chapter_title = chapter["title"]
        chapter_has_sections = chapter["has_sections"]

        if chapter_format:
            if len(chapters_in_page) == 1:
                replacements = {
                    "cnam": chapter_title,
                    "cnum": roman_chapter_num,
                    "cpre": chapter_prefix,
                }

                chapter_text = format_form_tag(chapter_format, replacements)
            # else: handle section tags
        else:
            if chapter_title == None: # try this very verbose solution, but why on earth is it needed???
                chapter_text = f"{{{{ph|class=chapter|{chapter_prefix} {displayed_section_num}}}}}"
            else:
                # print(type(chapter_title))
                # print(chapter_title)
                chapter_text = f"{{{{ph|class=chapter num|{chapter_prefix} {displayed_section_num}}}}}\n{{{{ph|class=chapter title|{chapter_title}|level=2}}}}"
        
        if chapter_has_sections:
            chapter_text += "\n/sec/"

        content = replace_line(content, chapter_text, line_num)

        # chapter_num += 1

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
        section = sections[overall_section_num_zero_indexed]

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


########################## formatting ##########################









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

def convert_complex_dhr(page):
    content = page["content"]

    if string_not_in_content(content, "/d/2/", "Adding dhrs to transcription"): #fornow
        return page

    content = re.sub(r"\/d\/([0-9]+)\/", rf"{{{{dhr|\1}}}}", content) # replace /d/2/ with {{dhr|2}} for example

    page["content"] = content

    return page

def convert_title_headers(page, title):
    content = page["content"]

    if string_not_in_content(content, "/ti/", "Converting title headers"):
        return page

    title_header = f"ph|class=title|{title}"

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

    page["content"] = content

    return page

def convert_smallcaps(page):
    content = page["content"]

    if string_not_in_content(content, "/sc/", "Converting /sc/ to smallcaps in transcription"):
        return page

    content = re.sub(r"\/sc\//(.+?)\//sc\/", r"{{sc|\1}}", content)

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

def convert_block_element(page, abbreviation, template_name):
    content = page["content"]
    block_tag = get_plain_tag(abbreviation)

    if string_not_in_content(content, block_tag, f"Converting {block_tag} to {template_name} in transcription"):
        return page
    
    block_start_tag = get_noparams_start_tag(abbreviation)
    block_end_tag = get_end_tag(abbreviation)
    
    content = content.replace(block_start_tag, f"{{{{{template_name}|")
    content = content.replace(block_end_tag, "}}")

    page["content"] = content

    return page

def convert_block_elements(page, block_continuations):
    for abbreviation, template_name in block_elements.items():
        page = convert_block_element(page, abbreviation, template_name)
    return block_continuations, page

def convert_simple_markup(content, abbreviation, template):

    abbreviation = get_plain_tag(abbreviation)

    if string_not_in_content(content, abbreviation, f"Replacing {abbreviation} with {template} in transcription"):
        return content

    if abbreviation == "/-/":
        template = "/" + template + "/"
    else:
        template = "{{" + template + "}}"
    content = content.replace(abbreviation, template)

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
    non_quotation_symbols = [
        "'",
        "{{\" '}}",
        "{{' \"}}",
    ]
    text = text.replace(f"{pattern}\"", f"{pattern}{{{{fqm}}}}")
    for symbol in non_quotation_symbols:
        text = text.replace(f"{pattern}{symbol}", f"{pattern}{{{{fqm|{symbol}}}}}")
    return text

def handle_fqm(text):
    text = convert_fqms("{{ppoem|class=poem|\n", text)
    # print(text)
    # text = text.replace("{{ppoem|class=poem|\n\"", "{{ppoem|class=poem|\n{{fqm}}")
    # text = text.replace("{{ppoem|class=poem|\n\'", "{{ppoem|class=poem|\n{{fqm|'}}")
    poem_pattern = r'\{\{ppoem\|class=poem\|\n([.\s\S]*?)\n\}\}'
    poems = re.findall(poem_pattern, text)

    # remove poems from text so that they can be parsed

    # fix fqm in beginning of stanzas
    for poem in poems:
        fixed_poem = convert_fqms("\n\n", poem)
        text = text.replace(poem, fixed_poem)
    # print("Text after beginning fqm:" + text)
    
    # correct when italics are mistakenly converted to fqm
    text = text.replace("{{fqm|'}}'", "''")

    return text

def convert_poems(page, block_continuations, convert_fqms):
    # text = convert_block_element(text, "poem", "poem")
    content = page["content"]

    if string_not_in_content(content, "/po/", "Converting poems"):
        return block_continuations, page

    pattern = r"\/po\//([\s\S]+?)\//po\/"
    replacement = r"{{ppoem|class=poem|\1}}"
    content = re.sub(pattern, replacement, content)

    if convert_fqms != "n":
        content = handle_fqm(content)

    page["content"] = content
    return block_continuations, page




################################## images ##################################




def convert_images(page, image_data, img_num):
    content = page["content"]

    img_tag = get_plain_tag("img")

    if string_not_in_content(content, img_tag, "Converting images"):
        return img_num, page
    

    images_in_page = get_string_from_lines(content, img_tag)

    # pattern = r"\/img\/([0-9]+)\/"
    # images = re.findall(pattern, content)
    for line_num, image_tag in images_in_page.items():
        image = image_data[img_num]
        image_filename = get_image_filename(image)
        image_caption = image["caption"]
        if image_caption:
            caption_display = f"\n | caption = {image_caption}\n"
        else:
            caption_display = ""
        image_size = image["size"]

        image_text = f"""{{{{FreedImg
 | file = {image_filename}{caption_display}
 | width = {image_size}px
}}}}"""

        content = replace_line(content, image_text, line_num)

        img_num += 1

    # content = re.sub(pattern, r"{{img|\1}}", content)

    page["content"] = content

    return img_num, page













################################## parse pages ##################################

def parse_transcription_pages(page_data, image_data, transcription_text, chapters, sections, mainspace_work_title, title, toc, chapter_format, section_format, chapter_beginning_formatting, drop_initials_float_quotes, convert_fqms, page_break_string, chapter_type, section_type):
    print("Parsing QT markup into wiki markup...")
    new_page_data = []
    img_num = 0
    # chapter_num = 0
    # part_num = 0
    overall_chapter_num = 0
    overall_section_num = 0
    block_continuations = {} # dictionary because of TOC needing split indices, CHANGE THIS LATER NOT SEMANTICALLY CORRECT
    inline_continuations = []
    for page in page_data:
        page_num = page["page_num"]
        print(f"Parsing page {page_num}...")

        page = add_half_to_transcription(page, title)
        page = add_space_to_apostrophe_quotes(page)
        if chapter_beginning_formatting == "sc" or not chapter_beginning_formatting:
            page = format_chapter_beginning_to_smallcaps(page)
        elif chapter_beginning_formatting == "di":
            page = format_chapter_beginning_to_drop_initial(page, drop_initials_float_quotes)
        else:
            # page = format_chapter_beginning_to_large_initial(page)
            pass
        page = convert_complex_dhr(page)
        page = convert_basic_elements(page)
        page = convert_title_headers(page, title)
        block_continuations, page = convert_block_elements(page, block_continuations)
        block_continuations, page = convert_poems(page, block_continuations, convert_fqms) # done
        page = convert_italics(page)
        page = convert_smallcaps(page)
        page = convert_right(page)
        page, inline_continuations = convert_wikilinks(page, inline_continuations, page_data)
        page = convert_author_links(page)
        img_num, page = convert_images(page, image_data, img_num)
        page = handle_forced_page_breaks(page, page_break_string)

        block_continuations, page = add_toc_to_transcription(page, toc, block_continuations)
        overall_chapter_num, page = convert_chapter_headers(page, chapters, overall_chapter_num, chapter_format, chapter_type)
        overall_section_num, page = convert_section_headers(page, sections, overall_section_num, section_format, section_type)


        page = remove_split_tag(page)


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

def generate_marker_text(marker, quality):
    if quality == "0":
        marker_text = "—"
    else:
        marker_text = "-"
    
    if marker:
        marker_text += marker
    
    if quality != "0":
        marker_text += "\n\n"

    return marker_text

def insert_parsed_pages(page_data, transcription_text):
    print("Inserting parsed pages into transcription text...")
    transcription_header = get_transcription_header(transcription_text)

    transcription_text_pages = []

    for page in page_data:
        content = page["content"]
        header = page["header"]
        footer = page["footer"]
        marker = page["marker"]
        quality = page["page_quality"]

        marker_text = generate_marker_text(marker, quality)

        if quality == "0":
            page_text = marker_text
        else:
            header_text, footer_text = generate_header_footer_text(header, footer)
            page_text = marker_text + header_text + content + footer_text
        
        transcription_text_pages.append(page_text)
    
    transcription_text_pages = "\n\n".join(transcription_text_pages)
    transcription_text_pages = transcription_header + "\n\n" + transcription_text_pages

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