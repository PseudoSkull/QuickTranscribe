# WS_collection

import pywikibot
import mwparserfromhell
from debug import print_in_red, print_in_green, print_in_yellow

def edit_summary(summary, transcription_page_title=None):
    if transcription_page_title:
        return f"{summary} (semi-automated, imported from QT transcription project [[s:en:{transcription_page_title}]])"
    else:
        return f"{summary} (semi-automated)"

def save_page(page, site, text, summary, transcription_page_title=None):
    print(f"{summary} ({page} at {site})")
    if text == page.text:
        print_in_yellow("WARNING: No difference between what's already on the page and your edit. Not saved.")
        return
    else:
        page.text = text
        page.save(edit_summary(summary, transcription_page_title), minor=False)

def linkify(text):
    return f"[[{text}]]"

def delinkify(text):
    return text.replace("[[", "").replace("]]", "")

def remove_template_markup(text):
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates()

    for template in reversed(templates):
        params = template.params
        if len(params) > 0:
            last_param = params[-1].value.strip()
            extracted_text = str(last_param)
            wikicode.replace(template, extracted_text)
            break

    return str(wikicode)

def parse_list_with_commas(list_of_words):
    if type(list_of_words) != list:
        return list_of_words
    if len(list_of_words) == 0:
        print_in_red("ERROR: Empty list of words passed to handle_list_as_commas()")
        return
    elif len(list_of_words) == 1:
        first_word = list_of_words[0]
        return list_of_words[0]
    elif len(list_of_words) == 2:
        first_word = list_of_words[0]
        second_word = list_of_words[1]
        return f"{first_word} and {second_word}"
    else:
        last_word = list_of_words[-1]
        words_except_last_word = list_of_words[:-1]
        words_with_commas = ', '.join(words_except_last_word)
        return f"{words_with_commas}, and {last_word}"
    

def remove_all_instances(lst, value_to_remove):
    new_list = []
    for item in lst:
        if item != value_to_remove:
            new_list.append(item)
    return new_list

def remove_bad_symbols_from_filename(filename):
    bad_symbols = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for symbol in bad_symbols:
        filename = filename.replace(symbol, "")
    return filename

def page_exists(page_title, site):
    page = pywikibot.Page(site, page_title)
    return page.exists()


def filter_existing_pages(pages, site):
    valid_pages = []
    for page_title in pages:
        page_title_delinkified = delinkify(page_title)
        if page_exists(page_title_delinkified, site):
            valid_pages.append(page_title)
        else:
            print_in_yellow(f"Page \"{page_title}\" that was checked does not exist... That link will not be used.")
    return valid_pages


def get_english_plural(word):
    es_endings = [
        "ch",
        "sh",
        "s",
        "x",
        "z",
    ]

    for ending in es_endings:
        if word.endswith(ending):
            return f"{word}es"
    return f"{word}s"


def get_author_page_title(author_name):
    if type(author_name) != list:
        author_name = [author_name,]

    author_names = []
    for name in author_name:
        author_names.append("Author:" + name)
    
    if len(author_names) == 1:
        return author_names[0]
    else:
        return author_names