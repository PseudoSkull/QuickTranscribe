# WS_collection

import pywikibot
import re
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from handle_wikisource_conf import get_regex_match
from parse_transcription import get_plain_tag, get_noparams_start_tag, get_end_tag
from edit_mw import save_page

"""<noinclude><pagequality level="{page_quality}" user="PseudoSkull" />{header}</noinclude>{content}<noinclude>{footer}</noinclude>"""

# site = pywikibot.Site("en", "wikisource")
# page = pywikibot.Page(site, "Page:Jalna.pdf/5")

# print(page.text)

# get the content and data of pages in the transcription

def add_data_item(page_data, page_num, header, footer, content, page_quality, marker, page_type):
    data_item = {}
    data_item["page_num"] = page_num
    data_item["header"] = header
    data_item["footer"] = footer
    data_item["content"] = content
    data_item["page_quality"] = page_quality
    data_item["marker"] = marker
    data_item["type"] = page_type
    page_data.append(data_item)
    return data_item

def get_header_and_footer(content):
    header = ""
    footer = ""

    header_tag = "head"
    footer_tag = "foot"

    header_start_tag = get_noparams_start_tag(header_tag)
    footer_start_tag = get_noparams_start_tag(footer_tag)
    header_end_tag = get_end_tag(header_tag)
    footer_end_tag = get_end_tag(footer_tag)

    if header_start_tag in content:
        header = get_regex_match(content, rf"{header_start_tag}\n(.+?)\n{header_end_tag}", "header tag")
        content = content.split(header_end_tag + "\n\n")[1]

    if footer_start_tag in content:
        footer = get_regex_match(content, rf"{footer_start_tag}\n(.+?)\n{footer_end_tag}", "footer tag")
        content = content.split("\n\n" + footer_start_tag)[0]

    return header, footer, content

def get_page_data(transcription_text, page_break_string=None):
    print("Retrieving page data...")
    page_data = []
    content = []
    content_as_string = ""
    page_num = 0
    read_page = False
    data_item = {}
    transcription_lines = transcription_text.split("\n\n")
    for line_num, line in enumerate(transcription_lines):
        page_type = ""
        header = ""
        footer = ""
        line_prefix = line[:1]
        line_suffix = line[1:]
        line_length = len(line)
        if line_length <= 4 and (line.startswith("-") or line.startswith("—")):
            # read_page = False
            # print(marker)
            if read_page: # i.e. if it's not the first page we're talking about
                content_as_string = "\n\n".join(content)
                if content_as_string == "/ign/":
                    page_quality = "i"
                if "/toc/" in content_as_string or 'class="toc-block"' in content_as_string or "{{TOC " in content_as_string:
                    if marker != "ill":
                        page_type = "toc"
                elif page_break_string and page_break_string in content_as_string:
                    page_type = "break"
                elif "/begin/" in content_as_string:
                    page_type = "begin"
                elif "/last/" in content_as_string:
                    page_type = "last"
                header, footer, content_as_string = get_header_and_footer(content_as_string)

                # if len(content) < 100:
                #     print(f"Marker is {marker} and page_num is {page_num} and content is {content}")
                add_data_item(page_data, page_num, header, footer, content_as_string, page_quality, marker, page_type)
                page_type = "" # temporary solution, because it happens again above, dunno why this helps
                data_item = {}
                read_page = False
            page_num += 1
            if line_prefix == "—":
                # page does not need to be proofread
                marker = line_suffix
                read_page = False
                page_quality = "0"
                content_as_string = ""
                add_data_item(page_data, page_num, header, footer, content_as_string, page_quality, marker, page_type)
                data_item = {}
                continue
            elif line_prefix == "-":
                marker = line_suffix
                # page is proofreadable
                page_quality = "3"
                content = []
                read_page = True
                # add_data_item(page_data, page_num, header, footer, content, page_quality)
                continue
        else:
            # this is content of a page
            content.append(line)
            print(line)

            # if it's the VERY LAST line and it's part of the content
            try:
                next_line = transcription_lines[line_num + 1]
                # print(f"Next line: '{next_line}'")
            except IndexError:
                if page_quality == "3":
                    content_as_string = "\n\n".join(content)
                    add_data_item(page_data, page_num, header, footer, content_as_string, page_quality, marker, page_type)
            continue

    print_in_green("Page data retrieved!")
    return page_data

def create_pages(page_data, filename, transcription_page_title, username, page_break_string):
    for page_data_item in page_data:
        page_num = page_data_item["page_num"]
        print(f"Adding page {page_num}...")
        page_quality = page_data_item["page_quality"]
        header = page_data_item["header"]
        footer = page_data_item["footer"]
        content = page_data_item["content"]

        content = content.replace(f"\n{page_break_string}", "") # remove page break comment from content, since it's not needed anymore
        content = content.replace(f"\n/begin/", "") # remove page break comment from content, since it's not needed anymore
        content = content.replace(f"/begin/", "") # remove page break comment from content, since it's not needed anymore
        content = content.replace(f"\n/last/", "") # remove page break comment from content, since it's not needed anymore
        content = content.replace(f"/last/", "") # remove page break comment from content, since it's not needed anymore
        content = content.replace(f"\n/title/", "") # remove page break comment from content, since it's not needed anymore
        content = content.replace(f"/title/", "") # remove page break comment from content, since it's not needed anymore
    

        site = pywikibot.Site("en", "wikisource")
        page_title = f"Page:{filename}/{page_num}"
        page = pywikibot.Page(site, page_title)

        if page_quality == "i":
            print("Page quality is 'i'. Ignoring page...")
            continue
        else:
            page_text = f"""<noinclude><pagequality level="{page_quality}" user="{username}" />{header}</noinclude>{content}<noinclude>{footer}</noinclude>"""
            save_page(page, site, page_text, f"Creating page {page_num} in Page namespace...", transcription_page_title)
    print_in_green("All pages added!")


# def get_cover_image(page_data, filename, index_pagelist):
#     print("Retrieving cover image...")
#     if page_data[0]["page_quality"] == "0" or "1=cover" not in index_pagelist:
#         print_in_yellow("No cover image found.")
#         return None
#     else:
#         site = pywikibot.Site('en', 'wikisource')
#         page = pywikibot.Page(site, f"Page:{filename}/1")
#         text = page.text
#         cover_pattern = r"\[\[File:([^|\]\]]+)(?:\||\]\])"
#         cover_match = re.search(cover_pattern, text)
#         if cover_match:
#             cover_filename = cover_match.group(1)
#             print_in_green(f"Cover image found! Filename: {cover_filename}")
#             return cover_filename