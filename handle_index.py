#WS_collection

# Add TOC to index page, like this: {{Page:Jalna.pdf/11}}
# REDO THIS WHOLE SYSTEM, to include HANDLE_PAGES LOGIC rather than what we repeat here

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page
from cleanup import split_string_by_newline
from handle_wikidata import add_index_page_to_version_item
import pywikibot
import re

marker_definitions = {
    "ad": "adv",
    "col": "coloph",
    "cov": "cover",
    "ded": "dedic",
    "fro": "frontis",
    "ha": "half",
    "i": "img",
    "ti": "title",
    "toc": "toc",
}

style_defaults = {
    "chapter":
    """	text-align: center;
	margin-bottom: 0.75em;""",
    
    "chapter.num":
    """	text-transform: uppercase;
    font-size: 120%;
    margin-bottom: 1em;""",

    "chapter.title":
    """	font-variant: all-small-caps;""",

    "half":
    """	text-align: center;
	text-transform: uppercase;
	font-size: 120%;""",

    "part-header":
    """	text-align: center;
    font-size: 120%;
    text-transform: uppercase;""",

    "poem": 
    """	font-size: 92%;
	margin-top: 2em;
    margin-bottom: 2em;""",

    "title":
    """	text-align: center;
    font-size: 144%;
	text-transform: uppercase;
    margin-bottom: 1em;""",

    "toc-block":
    """	max-width: 25em;
    margin-left: auto;
    margin-right: auto;
    """,

    "wst-freedimg-caption":
    """	font-size: 92%;""",
}

def extract_file_extension(filename):
    # Split the file name by the dot (.) character
    print(f"Extracting file extension of {filename}...")
    parts = filename.split(".")
    
    # If there is at least one dot and the last part is not empty
    if len(parts) > 1 and parts[-1] != "":
        # Return the last part (extension)
        print_in_green(f"File extension found: {parts[-1]}.")
        return parts[-1]
    else:
        print_in_red(f"No extension found on {filename}.")
        return None


def get_page_markers(text):
    print("Getting page markers...")
    text_parsed = split_string_by_newline(text)
    page_markers = []
    for line in text_parsed:
        line_prefix = line[:1]
        line_length = len(line)
        if line_length <= 4 and (line_prefix == "-" or line_prefix == "—"):
            page_markers.append(line)
    return page_markers

def generate_toc_section(page_data, filename):
    toc_pages = []
    for page in page_data:
        page_type = page["type"]
        page_num = page["page_num"]
        if page_type == "toc":
            toc_pages.append(page_num)

    toc_templates = []
    for toc_page in toc_pages:
        toc_templates.append(f"{{{{Page:{filename}/{toc_page}}}}}")

    toc_templates = "\n".join(toc_templates)

    return toc_templates

def create_index_pagelist(text):
    print("Generating index pagelist...")
    page_markers = get_page_markers(text)
    pagelist = "<pagelist\n"
    total_page_number = 0
    content_page_number = 0
    emdash_mode = False
    emdash_start = 0
    emdash_end = 0

    for marker in page_markers:
        total_page_number += 1
        marker_prefix = marker[:1]
        marker_suffix = marker[1:]
        marker_length = len(marker)
        # handle em dashes
        if emdash_mode:
            if marker != "—":
                emdash_mode = False
                emdash_end = total_page_number - 1
                if emdash_start == emdash_end:
                    pagelist += f"{emdash_start}=—\n"
                else:
                    pagelist += f"{emdash_start}to{emdash_end}=—\n"
                emdash_mode = False
                emdash_start = 0
                emdash_end = 0
            else:
                continue
        if marker == "—":
            emdash_mode = True
            emdash_start = total_page_number
            continue
        # handle others
        if marker_suffix in marker_definitions:
            marker_definition = marker_definitions[marker_suffix]
            pagelist += f"{total_page_number}={marker_definition}\n"
        if marker_suffix == "1":
            pagelist += f"{total_page_number}=1\n"

    pagelist += "/>"

    print_in_green("Index pagelist generated.")

    return pagelist

    # return index_pagelist

def create_index_page(index_page_title, index_pagelist, transcription_text, mainspace_work_title, title, author_WS_name, publisher_name, year, file_extension, location_name, version_item, transcription_page_title, page_data, filename):
    summary = "Creating index page..."
    progress = "C"
    site = pywikibot.Site('en', 'wikisource')
    index_page = pywikibot.Page(site, index_page_title)
    toc_section = generate_toc_section(page_data, filename)
    index_page_text = f"""{{{{:MediaWiki:Proofreadpage_index_template
|Type=book
|Title=''[[{mainspace_work_title}|{title}]]''
|Language=en
|Volume=
|Author=[[Author:{author_WS_name}|]]
|Translator=
|Editor=
|Illustrator=
|School=
|Publisher=[[Portal:{publisher_name}|{publisher_name}]]
|Address={location_name}
|Year={year}
|Key=
|ISBN=
|OCLC=
|LCCN=
|BNF_ARK=
|ARC=
|Source={file_extension}
|Image=1
|Progress={progress}
|Pages={index_pagelist}
|Volumes=
|Remarks={toc_section}
|Width=
|Css=
|Header=
|Footer=
|Transclusion=no
}}}}"""
    save_page(index_page, site, index_page_text, summary, transcription_page_title)
    add_index_page_to_version_item(version_item, index_page_title)
    create_index_styles(transcription_text, index_page_title, transcription_page_title)
 
def create_index_styles(transcription_text, index_page_title, transcription_page_title):
    # SORT CSS CLASSES

    site = pywikibot.Site('en', 'wikisource')
    index_styles = f"{index_page_title}/styles.css"
    index_styles_page = pywikibot.Page(site, index_styles)
    index_styles_text = ""
    classes_used = list(set(re.findall((rf"\|class=([\s\S]+?)\|"), transcription_text)))
    classes_used_in_html_tags = list(set(re.findall((rf" class=\"(.+?)\""), transcription_text)))
    
    classes_used += classes_used_in_html_tags

    # include captions
    if "FreedImg" in transcription_text:
        classes_used.append("wst-freedimg-caption")
    
    # put parent class in too
    for css_class in classes_used:
        if "." in css_class:
            css_parent_class = css_class.split(".")[0]
            if css_parent_class not in classes_used:
                classes_used.append(css_parent_class)

    classes_used.sort()

    for css_class, default_style in style_defaults.items():
        if css_class in classes_used:
            index_styles_text += f".{css_class} {{\n{default_style}\n}}\n\n"

    save_page(index_styles_page, site, index_styles_text, "Creating index style sheet with some default styles...", transcription_page_title)

def get_first_page(index_pagelist):
    first_page = re.findall(r"([0-9]+?)=1", index_pagelist)[0]
    return int(first_page)

def change_proofread_progress(index_page_title):
    site = pywikibot.Site('en', 'wikisource')
    index_page = pywikibot.Page(site, index_page_title)
    index_page_text = index_page.text
    progress = "V"
    index_page_text = re.sub(r"Progress=C", f"Progress={progress}", index_page_text)
    save_page(index_page, site, index_page_text, "Changing index progress to Proofread...")

def change_transclusion_progress(index_page_title):
    site = pywikibot.Site('en', 'wikisource')
    index_page = pywikibot.Page(site, index_page_title)
    index_page_text = index_page.text
    index_page_text = re.sub("Transclusion=no", "Transclusion=yes", index_page_text)
    save_page(index_page, site, index_page_text, "Changing transclusion progress to \"fully transcluded\"...")