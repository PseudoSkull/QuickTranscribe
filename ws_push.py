# WS_collection

import pywikibot
from config import transcription_page_title
from edit_mw import save_page

site = pywikibot.Site("en", "wikisource")

page = pywikibot.Page(site, transcription_page_title)

with open("waylaid.txt", "r") as f:
    page_text = f.read()

save_page(page, site, page_text, "Force page save for very large page")