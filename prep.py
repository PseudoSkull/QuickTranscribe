# WS_collection

import pywikibot
from config import mainspace_work_title, transcription_page_title
from debug import print_in_red, print_in_green, print_in_yellow
from edit_mw import save_page
from hathi import get_hathitrust_full_text_id, get_hathitrust_images
from handle_projectfiles import rename_and_copy_text_file
from handle_wikisource_conf import get_conf_variables
from ia import get_IA_files, unzip_jp2_folder
from waylaid import correct_text

site = pywikibot.Site('en', 'wikisource')
transcription_page = pywikibot.Page(site, transcription_page_title)

work_data = get_conf_variables(transcription_page_title)

# put logic here to check whether dlt and dl is from IA or Hathi or Books or WS
IA_id = work_data["Internet Archive ID"]
hathitrust_catalog_id = work_data["HathiTrust catalog ID"]

rename_and_copy_text_file()

ocr_file_path = "projectfiles/text_changeable.txt"

ocr_file = open(ocr_file_path, "r")

corrected_ocr = correct_text("projectfiles/text_changeable.txt")

# print(corrected_ocr)

ocr_file.close()

corrected_ocr_file_path = "projectfiles/text_corrected.txt"

corrected_ocr_file = open(corrected_ocr_file_path, "w+")

corrected_ocr_file.write(corrected_ocr)

corrected_ocr_file.close()




# print(corrected_ocr)
# print_in_green(corrected_ocr)

# IA_files = get_IA_files(IA_id)

# unzip_jp2_folder(IA_files)

# hathitrust_full_text_id = get_hathitrust_full_text_id(hathitrust_catalog_id)

# get_hathitrust_images(hathitrust_full_text_id)

