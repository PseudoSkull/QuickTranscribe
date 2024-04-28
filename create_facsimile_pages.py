# WS_collection

import pywikibot
from edit_mw import save_page

starting_page_original = 48
starting_page_facsimile = 48
end_page_facsimile = 319
site = pywikibot.Site('en', 'wikisource')

original_index = "Early Autumn (1926).pdf"
facsimile_index = "Early Autumn by Louis Bromfield.pdf"

username = "SnowyCinema"


current_page_on_original = starting_page_original

for i in range(starting_page_facsimile, end_page_facsimile+1):
    page_title = f"Page:{facsimile_index}/{i}"
    page = pywikibot.Page(site, page_title)
    page_text = page.text

    redirect_text = f"#REDIRECT [[Page:{original_index}/{current_page_on_original}]]\n{{{{facsimile page}}}}"

    page_text = f"<noinclude><pagequality level=\"0\" user=\"{username}\" /></noinclude>{redirect_text}<noinclude></noinclude>"

    save_page(page, site, page_text, "Redirecting facsimile page to page from earlier edition")

    current_page_on_original += 1