# WS_collection

import pywikibot
from handle_web_downloads import download_file
from debug import print_in_red, print_in_green, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page

# https://ws-export.wmcloud.org/?format=pdf&lang=en&page=Firecrackers

def test_pdf_export(mainspace_work_title):
    # THE DOWNLOAD PART OF THIS CURRENTLY DOESN'T ACTUALLY WORK, but it does remind me to click the link in my browser at least, and makes adding the category easy.
    print("Testing PDF export...")

    pdf_export_prefix = "http://ws-export.wmcloud.org/?format=pdf&lang=en&page="

    url_title = mainspace_work_title.replace(" ", "%20")
    
    pdf_export_url = pdf_export_prefix + url_title
    
    folder = "projectfiles"
    filename = "export_test.pdf"

    download_file(pdf_export_url, folder, filename)


    print_in_green("Download successful!")
    export_status = input("Did the export work? ")

    if export_status == "n":
        print_in_yellow("Export failed. Skipping step...")
        return
    else:
        print_in_green("Export successful! Adding category [[Category:Ready for export]] to mainspace work page...s")

        site = pywikibot.Site("en", "wikisource")
        mainspace_work_page = pywikibot.Page(site, mainspace_work_title)
        mainspace_work_page_text = mainspace_work_page.text
        mainspace_work_page_text += "\n[[Category:Ready for export]]"

        save_page(mainspace_work_page, site, mainspace_work_page_text, "Export tested: adding category [[Category:Ready for export]] to mainspace work page...")
