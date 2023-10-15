# WS_collection
import pywikibot
from config import mainspace_work_title
import roman
from debug import print_in_green, print_in_red, print_in_yellow
from edit_mw import save_page, edit_summary
pywikibot.config.base_dir = ('/Users/bobbybumps/Downloads/code_folder/core_stable_2/pywikibot')


site = pywikibot.Site('en', 'wikisource')

for attr, value in site.__dict__.items():
    print(f"{attr}: {value}")
# exit()

commons_site = pywikibot.Site('commons', 'commons')

wikidata_site = pywikibot.Site('wikidata', 'wikidata')

# transcription_text = transcription_page.text

chapter_num = 3

# Print the titles of the subpages
while 1:
    roman_chapter_num = roman.toRoman(chapter_num)
    subpage_title = f"{mainspace_work_title}/Chapter {roman_chapter_num}"
    subpage = pywikibot.Page(site, subpage_title)
    move_summary = edit_summary(f"Migrating roman chapter nums to arabic, to modernize titles and prepare for transclusion")
    if subpage.exists():
        new_subpage_title = f"{mainspace_work_title}/Chapter {chapter_num}"
        print(f"{subpage_title} -> {new_subpage_title}")
        subpage.move(new_subpage_title, reason=move_summary)
        chapter_num += 1
        continue
    print_in_green(f"All done!")
    break