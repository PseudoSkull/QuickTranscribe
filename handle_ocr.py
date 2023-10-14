# WS_collection

import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io  # Import io module
import os
from waylaid import correct_text



def generate_ocr():

    if "GB.pdf" in os.listdir("projectfiles"):
        pdf_path = 'projectfiles/GB.pdf'
    elif "hathi.pdf" in os.listdir("projectfiles"):
        pdf_path = 'projectfiles/hathi.pdf'
    else:
        # pdf_path = input("Enter the name of the PDF file: ")
        # pdf_path = f"projectfiles/{pdf_path}"
        print("Got here specifically")
        text_path = "projectfiles/text_original.txt"
        with open(text_path, "r") as file:
            original_ocr = file.read()
        return original_ocr
    original_ocr_file_path = "projectfiles/original_ocr.txt"
    # qt_page_separator = "\n\n-\n\n"
    qt_page_separator = "\n\n\n\n"
    if os.path.exists(original_ocr_file_path):
        # open file
        with open(original_ocr_file_path, "r") as file:
            # read file
            original_ocr = file.read()
        page_list = original_ocr.split(qt_page_separator)
    else:
        # open(original_ocr_file_path, "x")
        pdf_document = fitz.open(pdf_path)

        page_list = []

        # Loop through all pages in the document
        for page_number in range(pdf_document.page_count):
            print(f"Collecting OCR from page {page_number+1} of {pdf_document.page_count} in {pdf_path}...")
            pdf_page = pdf_document[page_number]

            # Get the images from the page
            images = pdf_page.get_images(full=True)

            # Loop through the images on the page
            for img_index, img in enumerate(images):
                xref = img[0]  # Get the image's XREF (reference)
                base_image = pdf_document.extract_image(xref)
                
                image_data = base_image["image"]
                # image_width = base_image["width"]
                # image_height = base_image["height"]
                
                # Create a PIL image using io.BytesIO
                image = Image.open(io.BytesIO(image_data))
                
                # Perform OCR on the image
                text = pytesseract.image_to_string(image)
                
                # Print the extracted text
                print("Text was: ", text)
                page_list.append(text)
                

        # Close the PDF document
        pdf_document.close()

        original_ocr = qt_page_separator.join(page_list)

        with open("projectfiles/original_ocr.txt", "w+") as file:
            file.write(original_ocr)
    # return page_list, original_ocr
    return original_ocr

# page_list, original_ocr = generate_ocr(pdf_path)

# corrected_ocr_pages = []

# for page_num, page in enumerate(page_list):
#     print(f"Correcting OCR of page {page_num+1}...")
#     corrected_page = correct_text(page)
#     corrected_ocr_pages.append(corrected_page)

# corrected_ocr = qt_page_separator.join(corrected_ocr_pages)

# print(corrected_ocr)