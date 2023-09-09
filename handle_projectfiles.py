# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break

import os
import shutil
import json
import img2pdf
import xml.etree.ElementTree as ET


def rename_and_copy_text_file():
    folder_path = "projectfiles"
    original_file_name = "text_original.txt"
    copy_file_name = "text_changeable.txt"

    # Find the .txt file in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            original_file_path = os.path.join(folder_path, file_name)
            # print_in_green(f"File {file_name} was found!")
            # Rename the file to "text_original.txt"
            renamed_file_path = os.path.join(folder_path, original_file_name)
            os.rename(original_file_path, renamed_file_path)
            print_in_green(f"File {file_name} renamed to '{original_file_name}'.")

            # Create a copy of the renamed file
            copy_file_path = os.path.join(folder_path, copy_file_name)
            shutil.copy(renamed_file_path, copy_file_path)
            print_in_green(f"File '{original_file_name}' copied and saved as '{copy_file_name}'.")
            return
    print_in_red("No .txt file found in the folder.")
    return

def find_scan_file_to_upload(scan_source):
    print("Looking for the correct scan file in the folder to upload...")
    folder_path = "projectfiles"
    for file in os.listdir(folder_path):
        if scan_source == "ia" and file.endswith(".djvu"):
                scan_file_path = os.path.join(folder_path, file)
                print_in_green(f"DJVU file {file} was found!")
                return scan_file_path
        elif "hathi.pdf" in file and scan_source == "ht":
            scan_file_path = os.path.join(folder_path, file)
            print_in_green(f"Hathi PDF file {file} was found!")
            return scan_file_path
        elif "gb.pdf" in file and scan_source == "gb":
            scan_file_path = os.path.join(folder_path, file)
            print_in_green(f"Google Books PDF file {file} was found!")
            return scan_file_path
    
    for file in os.listdir(folder_path): # because DJVU is superior, we do it again
        if scan_source == "ia" and file.endswith(".pdf") and "_bw" not in file and file != "hathi.pdf":
            # folder_path = "projectfiles3"
            # scan_file_path = os.path.join(folder_path, "hathi.pdf")
            scan_file_path = os.path.join(folder_path, file)
            print_in_green(f"PDF file {file} was found!")
            return scan_file_path
    
    print_in_red("No scan file found in the folder.")
    return None

def write_to_json_file(json_filename, data):
    folder_path = "projectfiles/json_data"
    json_file_path = os.path.join(folder_path, json_filename)
    print(f"Writing data to JSON file at {json_file_path}...")
    with open(json_file_path, "w+") as json_file:
        json.dump(data, json_file)
    print_in_green(f"Data written to {json_file_path}!")
    return

def get_json_data(json_filename):
    folder_path = "projectfiles/json_data"
    json_file_path = os.path.join(folder_path, json_filename)
    print(f"Attempting to retrieve data from JSON file at {json_file_path}...")
    json_file_exists = os.path.exists(json_file_path)
    # if json_file_path_exists

    # if json file path exists:
    if json_file_exists:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
        print_in_green(f"Data retrieved from {json_file_path}!")
        return data
    else:
        print_in_yellow(f"No JSON file found at {json_file_path}.")
        return None


def compare_image_counts(image_data):
    folder_path = "projectfiles/processed_files"
    print(f"Comparing number of images in image_data against number of images in {folder_path}...")
    image_count = len(image_data)
    image_file_count = len(os.listdir(folder_path))
    if ".DS_Store" in os.listdir(folder_path):
        image_file_count -= 1
    if image_count == image_file_count:
        print_in_green(f"Number of images in image_data matches number of images in folder. Image number: {image_count}")
        # return True
    else:
        print_in_red(f"Number of images in image_data does not match number of images in folder.\nImage count: {image_count}\nImage file count: {image_file_count}")
        exit()
        # return False

def get_images_to_upload():
    folder_path = "projectfiles/processed_files"
    # print(f"Comparing number of images in image_data against number of images in {folder_path}...")
    image_files = os.listdir(folder_path)
    image_files.sort()
    return image_files

def create_folder(folder_path_to_create):
    if not os.path.exists(folder_path_to_create):
        os.mkdir(folder_path_to_create)
        print_in_green(f"Folder {folder_path_to_create} created.")
    else:
        print_in_yellow(f"Folder {folder_path_to_create} already exists.")

def create_projectfiles_folders():
    print("Creating projectfiles folder structure...")
    folder_path = "projectfiles"
    folder_names = [
        "files_to_process",
        "gutenberg",
        "json_data",
        "librivox",
        "librivox/audio_tracks",
        "processed_files",
    ]

    # create parent folder
    create_folder(folder_path)

    # if not os.path.exists(folder_path_to_create):
    for folder_name in folder_names:
        subfolder = os.path.join(folder_path, folder_name)
        create_folder(subfolder)
    print("Folder structure created.")

# def assemble_pdf(folder_path):
    # print(f"Assembling PDF from images in {folder_path}...")
    # os.chdir(folder_path)
    # os.system("convert *.jpg ../hathi.pdf")
    # print_in_green("PDF assembled!")

def get_digital_value(string):
    # Custom function to extract the digital value from a string
    return int(''.join(filter(str.isdigit, string)))

def sort_by_digital_values(list_to_sort):
    sorted_list = sorted(list_to_sort, key=get_digital_value)
    return sorted_list

def assemble_pdf(folder_path, output_path=None):
    print(f"Assembling PDF from images in {folder_path}...")
    if not output_path:
        output_path = "projectfiles/hathi.pdf"
    with open(output_path, "wb") as f:
        images = [os.path.join(folder_path, img) for img in os.listdir(folder_path) if img.endswith(".jpg")]

        # sort by digital values, because otherwise it comes out of order. .sort() function sorts by ASCII values, not digital values
        images = sort_by_digital_values(images)

        f.write(img2pdf.convert(images))
    
    print_in_green("PDF assembled!")

def get_lccn_from_xml():
    folder_path = "projectfiles"
    for file in os.listdir(folder_path):
        if file.endswith("_meta.xml"):
            xml_file_path = os.path.join(folder_path, file)
            print(f"XML file found at {xml_file_path}.")
            with open(xml_file_path, "r") as xml_file:
                try:
                    tree = ET.parse(xml_file_path)
                    root = tree.getroot()

                    # Assuming <lccn> is a direct child of the root element
                    lccn_element = root.find('lccn')

                    if lccn_element is not None:
                        lccn = lccn_element.text
                        print_in_green(f"LCCN found: {lccn}")
                        return lccn
                    else:
                        print("No <lccn> element found in the XML.")
                        return None
                except ET.ParseError as e:
                    print(f"Error parsing XML: {str(e)}")
                    return None
    print_in_red("No XML file found in the folder.")
    return None