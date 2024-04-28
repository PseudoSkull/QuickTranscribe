# WS_collection

import pywikibot
from config import transcription_page_title

site = pywikibot.Site("en", "wikisource")

page = pywikibot.Page(site, transcription_page_title)

with open("waylaid.txt", "w+") as f:
    f.write(page.text)