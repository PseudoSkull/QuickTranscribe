# WS_collection

import pywikibot
from edit_mw import save_page

site = pywikibot.Site('en', 'wikisource')

original_work = "Thunder on the Left (1925)"
facsimile_work = "Thunder on the Left (1926)"

original_index = "Thunder on the Left (1925).djvu"
facsimile_index = "Thunder on the left (IA thunderonleft0000morl).pdf"

username = "SnowyCinema"

original_work_and_subpages = list(site.allpages(prefix=original_work))

original_work_and_subpages.append(pywikibot.Page(site, original_work))

# print(original_work_and_subpages)

for original_page in original_work_and_subpages:
    original_title = original_page.title()
    original_text = original_page.text

    facsimile_title = original_title.replace("1925", "1926")
    facsimile_text = original_text.replace(original_index, facsimile_index)
    facsimile_text = facsimile_text.replace("1925", "1926")

    facsimile_page = pywikibot.Page(site, facsimile_title)

    save_page(facsimile_page, site, facsimile_text, "Transcluding facsimile edition")


# for i in range(starting_page_facsimile, end_page_facsimile+1):
#     page_title = f"Page:{facsimile_index}/{i}"
#     page = pywikibot.Page(site, page_title)
#     page_text = page.text

#     redirect_text = f"#REDIRECT [[Page:{original_index}/{current_page_on_original}]]\n{{{{facsimile page}}}}"

#     page_text = f"<noinclude><pagequality level=\"0\" user=\"{username}\" /></noinclude>{redirect_text}<noinclude></noinclude>"

#     save_page(page, site, page_text, "Redirecting facsimile page to page from earlier edition")

#     current_page_on_original += 1