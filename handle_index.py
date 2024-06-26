#WS_collection

# Add TOC to index page, like this: {{Page:Jalna.pdf/11}}
# REDO THIS WHOLE SYSTEM, to include HANDLE_PAGES LOGIC rather than what we repeat here

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page, parse_list_with_commas
from cleanup import split_string_by_newline
from handle_wikidata import add_index_page_to_version_item
import pywikibot
import re

marker_definitions = {
    "ad": "adv",
    "bk": "book",
    "col": "coloph",
    "cov": "cover",
    "ded": "dedic",
    "fro": "frontis",
    "ha": "half",
    "i": "img",
    "i2": "img2", # add functionality for iteration later
    "i3": "img3",
    "ill": "illus",
    "li": "list",
    "no": "note",
    "not": "note",
    "po": "poem",
    "pt": "part",
    "quo": "quote",
    "ti": "title",
    "toc": "toc",
}

style_defaults = {
    "chapter": # IF NO STYLE IS SPECIFIED, USE THIS
    {
        "has_children":
        """	text-align: center;
	margin-bottom: 1.5em;""",

        "no_children":
        """	text-align: center;
	text-transform: uppercase;
	font-size: 120%;
	margin-bottom: 1.5em;""",
    },

    "chapter-half": # IF NO STYLE IS SPECIFIED, USE THIS
    {
        "has_children":
        """	text-align: center;
	margin-bottom: 1.5em;""",

        "no_children":
        """	text-align: center;
	text-transform: uppercase;
	font-size: 120%;
	margin-bottom: 1.5em;""",
    },

    "chapter num":
    """	text-transform: uppercase;
	font-size: 120%;
	margin-bottom: 1.5em;""",

    "chapter title":
    """	font-variant: all-small-caps;""",

    "chapter-half num":
    """	text-transform: uppercase;
	font-size: 120%;
	margin-bottom: 1.5em;""",

    "chapter-half title":
    """	font-style: italic;
    font-size: 120%;""",

    "chapter-subtitle":
    """	text-align: center;
	font-size: 92%;
	font-variant: all-small-caps;
    margin-bottom: 1.5em;""",

    "drop-initial-image img":
    """	width: 75px;
	height: auto;""",

    "envoi":
    """	text-align: center;
    font-size: 92%;
    font-variant: all-small-caps;""",

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

    "poem-italic":
    """	font-size: 92%;
	margin-top: 2em;
	margin-bottom: 2em;
    font-style: italic;""",

    "section":
    """	text-align: center;""",

    "title-header":
    """	text-align: center;
 	font-size: 144%;
    margin-bottom: 1.5em;
	text-transform: uppercase;""",

    "toc-block":
    """	max-width: 25em;
    margin-left: auto;
    margin-right: auto;""",

    "wst-block-center":
    """	max-width: 25em;""",

    "wst-blockquote":
    """	font-size: 92%;
	max-width: 25em;
    margin-bottom: 1.5em;
    margin-top: 1.5em;""",

    "wst-fine-block":
    """	margin-bottom: 2em;
	margin-top: 2em;""",

    "wst-freedimg-caption":
    """	font-size: 92%;""",

    # "wst-smaller-block":
    # """	margin-bottom: 2em;
	# margin-top: 2em;""",
 
    "wst-letter-message":
    """	margin-top: 2em;
    margin-bottom: 2em;""",

    "wst-the-end":
    """	margin-top: 5em;
    font-variant: all-small-caps;
    text-align: center;""",

    "wst-toc-table":
    """	font-variant: small-caps;
	max-width: 25em;
	font-size: 92%;"""
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

def generate_aux_toc_template(toc, site, mainspace_work_title, transcription_page_title):
    print("Auxiliary table of contents found. Generating auxiliary TOC template...")
    template_page_name = f"{mainspace_work_title}/TOC"
    template_page_title = "Template:" + template_page_name
    template_documentation_page_title = template_page_title + "/doc"
    template_page = pywikibot.Page(site, template_page_title)
    template_documentation_page = pywikibot.Page(site, template_documentation_page_title)
    template_page_text = f"""{toc}<noinclude>
{{{{documentation}}}}
</noinclude>"""
    template_documentation_page_text = f"""{{{{Documentation subpage}}}}

{{{{AuxTOC documentation|{mainspace_work_title}}}}}

<includeonly>
[[Category:Auxiliary table of contents templates]]
</includeonly>"""
    print(toc)
    save_page(template_page, site, template_page_text, "Creating auxiliary TOC template...", transcription_page_title)
    save_page(template_documentation_page, site, template_documentation_page_text, "Creating auxiliary TOC template documentation...", transcription_page_title)
    return "{{" + template_page_name + "}}"

def generate_toc_section(page_data, filename, toc_is_auxiliary, toc, site, mainspace_work_title, transcription_page_title):
    if toc_is_auxiliary:
        aux_toc_template = generate_aux_toc_template(toc, site, mainspace_work_title, transcription_page_title)
        return aux_toc_template
    else:
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

def get_roman_page_numbers(page_data):
    print("Getting roman page numbers...")
    roman_page_numbers = []
    for page in page_data:
        page_format = page["format"]
        page_num = page["page_num"]
        if page_format == "roman":
            roman_page_numbers.append(page_num)
    
    if roman_page_numbers:
        first_roman_page_num = roman_page_numbers[0]
        last_roman_page_num = roman_page_numbers[-1]

        # if after roman pages end, arabic page nums restart
        next_page_num = int(last_roman_page_num) + 1
        next_page_num_zero_indexed = int(last_roman_page_num)
        next_page = page_data[next_page_num_zero_indexed]
        next_page_marker = next_page["marker"]

        if next_page_marker == "1":
            next_page_display = f"\n{next_page_num}=1"
        else:
            next_page_display = ""

        roman_pagelist_line = f"{first_roman_page_num}to{last_roman_page_num}=roman{next_page_display}"
        return roman_pagelist_line
    else:
        return None

def create_index_pagelist(page_data):
    print("Generating index pagelist...")
    pagelist = "<pagelist\n"
    stored_marker = None
    stored_marker_pages = []

    for marker_num, page in enumerate(page_data):
        
        marker = page["marker"]
        marker_num += 1 # not zero-indexed

        # if marker == "1":
        #     # print("Marker was 1")
        #     pagelist += f"{marker_num}=1\n"
        #     continue

        if marker in marker_definitions:
            marker = marker_definitions[marker]

        if not stored_marker and marker.isdigit():
            continue
        
        if not marker:
            marker = "—"

        if marker != stored_marker and len(stored_marker_pages) > 0:
            first_stored_marker_page = stored_marker_pages[0]
            last_stored_marker_page = stored_marker_pages[-1]
            if len(stored_marker_pages) == 1:
                pagelist += f"{first_stored_marker_page}={stored_marker}\n"
            else:
                pagelist += f"{first_stored_marker_page}to{last_stored_marker_page}={stored_marker}\n"
            stored_marker_pages = []
            if marker.isdigit():
                pagelist += f"{marker_num}={marker}\n"
                stored_marker = None
            # continue


        if not marker.isdigit():
            stored_marker = marker
            stored_marker_pages.append(marker_num)
        
        # if back cover
        if marker_num == len(page_data) and len(stored_marker_pages) == 1:
            first_stored_marker_page = stored_marker_pages[0]
            pagelist += f"{first_stored_marker_page}={stored_marker}\n"

    roman_pagelist_line = get_roman_page_numbers(page_data)
    if roman_pagelist_line:
        pagelist = pagelist.replace("=1\n", f"=1\n{roman_pagelist_line}\n", 1)

    pagelist += "/>"

    print_in_green("Index pagelist generated.")

    print(pagelist)

    return pagelist

    # return index_pagelist

def get_title_page(page_data):
    for page_num, page in enumerate(page_data):
        page_num += 1 # not zero-indexed
        page_quality = page["page_quality"]
        page_marker = page["marker"]
        page_content = page["content"]
        if (page_quality != "0" and page_num == 1) or page_marker == "ti" or "/title/" in page_content:
            return page_num
    print_in_red("ERROR: No title page found. Please insert /title/ somewhere in the transcription to indicate which page is the title page.")
    exit()

def create_index_page(index_page_title, index_pagelist, transcription_text, mainspace_work_title, title, author_WS_name, illustrator_WS_name, editor_WS_name, translator_WS_name, publisher_name, year, file_extension, location_name, version_item, transcription_page_title, page_data, filename, toc_is_auxiliary, toc):
    print(f"In function: editor WS name: {editor_WS_name}, publisher name: {publisher_name}")
    # exit()
    summary = "Creating index page..."
    progress = "C"
    site = pywikibot.Site('en', 'wikisource')
    index_page = pywikibot.Page(site, index_page_title)
    location_name = parse_list_with_commas(location_name)
    toc_section = generate_toc_section(page_data, filename, toc_is_auxiliary, toc, site, mainspace_work_title, transcription_page_title)

    if illustrator_WS_name:
        illustrator_display = f"[[Author:{illustrator_WS_name}|]]"
    else:
        illustrator_display = ""
    
    if editor_WS_name:
        editor_display = f"[[Author:{editor_WS_name}|]]"
    else:
        editor_display = ""

    if translator_WS_name:
        translator_display = f"[[Author:{translator_WS_name}|]]"
    else:
        translator_display = ""


    publisher_display = f"[[Portal:{publisher_name}|{publisher_name}]]"
    if publisher_name == "self":
        publisher_display = "[[Portal:Self-published works|Self-published]]"

    title_page = get_title_page(page_data)
    index_page_text = f"""{{{{:MediaWiki:Proofreadpage_index_template
|Type=book
|Title=''[[{mainspace_work_title}|{title}]]''
|Language=en
|Volume=
|Author=[[Author:{author_WS_name}|]]
|Translator={translator_display}
|Editor={editor_display}
|Illustrator={illustrator_display}
|School=
|Publisher={publisher_display}
|Address={location_name}
|Year={year}
|Key=
|ISBN=
|OCLC=
|LCCN=
|BNF_ARK=
|ARC=
|Source={file_extension}
|Image={title_page}
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
    print(index_page_text)
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
    if "FreedImg" in transcription_text and " | caption = " in transcription_text:
        classes_used.append("wst-freedimg-caption")
    if "{{fine block" in transcription_text or "{{fb|" in transcription_text:
        classes_used.append("wst-fine-block")
    if "{{bc|" in transcription_text or "{{block center" in transcription_text:
        classes_used.append("wst-block-center")
    if "{{bquote|" in transcription_text or "{{blockquote" in transcription_text:
        classes_used.append("wst-blockquote")
    if "{{let|" in transcription_text or "{{letter/s}}" in transcription_text or "{{letter|" in transcription_text:
        classes_used.append("wst-letter-message")
    if "{{The End}}" in transcription_text or "{{Finis}}" in transcription_text or "{{finis}}" in transcription_text:
        classes_used.append("wst-the-end")
    if "{{TOC begin}}" in transcription_text:
        classes_used.append("wst-toc-table")
    if "|image=" in transcription_text and "{{di|" in transcription_text: # drop initial images
        classes_used.append("drop-initial-image img")
    
    classes_that_have_children = []
    # put parent class in too
    # for css_class in classes_used:
    for css_class in classes_used:
        if " " in css_class:
            css_parent_class = css_class.split(" ")[0]
            if css_parent_class not in classes_used:
                classes_used.append(css_parent_class)
                classes_that_have_children.append(css_parent_class)

    classes_used.sort()

    for css_class, default_style in style_defaults.items():
        if css_class in classes_used:
            css_class = css_class.replace(" ", ".")
            if type(default_style) == dict: # i.e. if it is a class that could be a parent class
                if css_class in classes_that_have_children:
                    default_style = default_style["has_children"]
                else:
                    default_style = default_style["no_children"]
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

def change_transclusion_progress(index_page_title, advertising_is_transcluded):
    site = pywikibot.Site('en', 'wikisource')
    index_page = pywikibot.Page(site, index_page_title)
    index_page_text = index_page.text
    if advertising_is_transcluded:
        transclusion_progress = "yes"
    else:
        transclusion_progress = "notadv"
    index_page_text = re.sub("Transclusion=no\n", f"Transclusion={transclusion_progress}\n", index_page_text)
    save_page(index_page, site, index_page_text, "Changing transclusion progress to \"fully transcluded\"...")