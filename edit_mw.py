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
