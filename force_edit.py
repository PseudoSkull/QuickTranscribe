# WS_collection

import pywikibot
from edit_mw import save_page

site = pywikibot.Site('en', 'wikisource')

page_title = "Index:Thunder on the left (IA thunderonleft0000morl).pdf/styles.css"

page = pywikibot.Page(site, page_title)

page_text = "#REDIRECT [[Index:Thunder on the Left (1925).djvu/styles.css]]"

save_page(page, site, page_text, "Force page save, to try and see if redirecting style sheet could work even in theory")