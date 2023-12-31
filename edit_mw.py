# WS_collection

import pywikibot
from pywikibot import pagegenerators
import mwparserfromhell
from debug import print_in_red, print_in_green, print_in_yellow
import datetime
import re

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

    ies_endings = [
        "y",
    ]

    for ending in es_endings:
        if word.endswith(ending):
            return f"{word}es"
    
    for ending in ies_endings:
        if word.endswith(ending):
            return f"{word[:-1]}ies"
    
    return f"{word}s"


def get_author_page_title(author_name):
    if author_name:
        if type(author_name) != list:
            author_name = [author_name,]

        author_names = []
        for name in author_name:
            author_names.append("Author:" + name)
        
        if len(author_names) == 1:
            return author_names[0]
        else:
            return author_names


def has_digits(input_string):
    return any(char.isdigit() for char in input_string)

def is_even(number):
    return number % 2 == 0




def get_category_items(site, category_name):
    if category_name.startswith("Category:"):
        category_name = category_name[9:]
    
    category = pywikibot.Category(site, f'Category:{category_name}')

    # Get the page generator for all items in the category
    item_generator = pagegenerators.CategorizedPageGenerator(category)
    
    # Iterate through the generator and print item titles

    category_items = []

    for item in item_generator:
        category_items.append(item.title())

    print(category_items)
    return category_items

def get_backlinks(site, page_title):
    page = pywikibot.Page(site, page_title)

    backlinks = list(page.backlinks())

    backlink_titles = []

    for backlink in backlinks:
        backlink_titles.append(backlink.title())

    return backlink_titles

def remove_esl_and_ssl_from_backlinks(mainspace_work_title):
    site = pywikibot.Site("en", "wikisource")

    backlinks = get_backlinks(site, mainspace_work_title)

    for backlink in backlinks:
        page = pywikibot.Page(site, backlink)
        page_text = page.text

        templates_to_remove = [
            "esl",
            "ssl",
            "small scan link",
            "external scan link",
            "ext scan link",
            "scn",
            "scan needed",
            "ia small link",
        ]

        new_page_text = []

        found_template = ""

        for line in page_text.split("\n"):
            if mainspace_work_title in line:
                for template in templates_to_remove:
                    if template in line.lower():
                        # Example: "* ''[[Along the Trail (Yates)|Along the Trail]]'' (1912) {{esl|The Life of Samuel Johnson, LL.D. (1791).djvu}}"
                        # Remove everything after " {{esl|"

                        line = re.sub(rf" {{{{{template}\|.*?}}}}", "", line, flags=re.IGNORECASE)
                        line = re.sub(rf" {{{{{template}}}}}", "", line, flags=re.IGNORECASE)
                        found_template = template
                        break

            new_page_text.append(line)
        
        new_page_text = "\n".join(new_page_text)

        if found_template != "":
            save_page(page, site, new_page_text, f"Removing [[Template:{found_template}]] template for completed work, [[{mainspace_work_title}]]")


def fix_backlinks(site, page_title, new_page_title):
    backlinks = get_backlinks(site, page_title)
    if page_title.startswith("Category:"):
        backlinks += get_category_items(site, page_title)

    print(backlinks)
    for backlink in backlinks:
        print(f"Fixing page {backlink}")
        page = pywikibot.Page(site, backlink)
        page_text = page.text

        page_text = page_text.replace(f"[[{page_title}", f"[[{new_page_title}")
        page_text = page_text.replace(f"[[:{page_title}", f"[[:{new_page_title}")
    
        save_page(page, site, page_text, f"Removing link to deleted/moved page")


def get_title_hierarchy(page_title, translator):
    if translator:
        translator_surname = translator.split(" ")[-1]
    else:
        translator_surname = "No surname"
    if "(" in page_title:
        parens = page_title.split("(")[1][:-1]
        if "," in parens or "." in parens or "&" in parens or "Company" in parens or parens.isdigit() or translator_surname in parens:
            return "version"
        return "disambig"
    return "work"

def follow_redirect(page_title):
    site = pywikibot.Site("en", "wikisource")
    page = pywikibot.Page(site, page_title)
    if page.isRedirectPage():
        redirect_title = page.getRedirectTarget().title()
        print(f"Page was a redirect. Going to {redirect_title}...")
        return redirect_title
    print("Page was not a redirect.")
    return page_title

def get_current_pd_cutoff_year():
    current_year = datetime.datetime.now().year
    return current_year - 96
