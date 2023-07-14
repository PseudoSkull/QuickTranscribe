# WS_collection

import pywikibot
from config import username, mainspace_work_title, transcription_page_title
from debug import print_in_red, print_in_green, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page
from hathi import get_hathitrust_full_text_id, get_hathitrust_images
from handle_projectfiles import rename_and_copy_text_file, create_projectfiles_folders, assemble_pdf
from handle_wikisource_conf import get_conf_values, check_QT_progress, update_QT_progress, update_conf_value, create_boilerplate, get_work_data
from ia import get_IA_files, unzip_jp2_folder
from waylaid import correct_text

prep_progresses = [
]

site = pywikibot.Site('en', 'wikisource')
transcription_page = pywikibot.Page(site, transcription_page_title)


transcription_text = transcription_page.text
expected_progress = "boilerplate_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)


if not at_expected_progress:
    transcription_text = create_boilerplate()

    save_page(transcription_page, site, transcription_text, f"Creating boilerplate for QT project {mainspace_work_title}...")

    print_in_blue("NOW GO AND ADD SOME BASIC INFORMATION TO THE BOILERPLATE!!!")
    exit()

transcription_text = transcription_page.text
expected_progress = "projectfiles_folders_created"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    create_projectfiles_folders()

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that projectfiles folders have been created...")



work_data = get_conf_values(transcription_page_title)

# put logic here to check whether dlt and dl is from IA or Hathi or Books or WS
IA_id = get_work_data(work_data, "Internet Archive ID")
hathitrust_catalog_id = get_work_data(work_data, "HathiTrust catalog ID")
hathitrust_full_text_id = get_work_data(work_data, "HathiTrust full text ID")

transcription_text = transcription_page.text
expected_progress = "ia_files_downloaded"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    IA_files = get_IA_files(IA_id)
    unzip_jp2_folder(IA_files)
    rename_and_copy_text_file()

    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that IA files have been downloaded...")

transcription_text = transcription_page.text
expected_progress = "hathi_files_downloaded"
at_expected_progress = check_QT_progress(transcription_text, expected_progress)

if not at_expected_progress:
    if hathitrust_catalog_id or hathitrust_full_text_id:
        if not hathitrust_full_text_id:
            hathitrust_full_text_id = get_hathitrust_full_text_id(hathitrust_catalog_id)
        hathi_folder = get_hathitrust_images(hathitrust_full_text_id)

        assemble_pdf(hathi_folder)
    else:
        print_in_yellow("No HathiTrust information was given. No downloads were made.")
    transcription_text = update_QT_progress(transcription_text, expected_progress)
    save_page(transcription_page, site, transcription_text, "Noting that Hathi files have been downloaded...")

    print_in_blue("NOW GO TO THE IA TEXT FILE AND TAKE OUT THE FRONT MATTER OCR!!!")

    exit()


# exit()

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
