# WS_collection

from debug import print_in_red, print_in_green, print_in_yellow, process_break

import os
import shutil
import json


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

def find_scan_file_to_upload():
    print("Looking for the correct scan file in the folder to upload...")
    folder_path = "projectfiles"
    for file in os.listdir(folder_path):
        if file.endswith(".djvu"):
            scan_file_path = os.path.join(folder_path, file)
            print_in_green(f"File {file} was found!")
            return scan_file_path
    print_in_red("No scan file found in the folder.")
    return

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