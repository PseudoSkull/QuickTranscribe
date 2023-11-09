# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
import requests
import json


# sample link https://openlibrary.org/api/volumes/brief/json/oclc:16520708

def get_openlibrary_data(openlibrary_version_id, oclc):
    if not openlibrary_version_id:
        print("Downloading Open Library data...")
        openlibrary_folder = "projectfiles/openlibrary"

        # Download and append JSON data
        openlibrary_data_filename = "openlibrary_data"
        # open html page

        openlibrary_data_url = f"https://openlibrary.org/api/volumes/brief/json/oclc:{oclc}"

        response = requests.get(openlibrary_data_url)
        openlibrary_data = response.json()

        lccn = None
        openlibrary_work_id = None

        if len(str(openlibrary_data)) > 2:

            records_data = openlibrary_data[list(openlibrary_data.keys())[0]]["records"]
            unparsed_version_id = list(records_data.keys())[0]

            records_data = records_data[unparsed_version_id]

            identifiers = records_data["data"]["identifiers"]
            lccn = None

            if "lccn" in identifiers:
                lccn = identifiers["lccn"]

            # openlibrary_data = json.loads()


            openlibrary_version_id = unparsed_version_id.split("/")[-1]
            # openlibrary_data["openlibrary_version_id"] = openlibrary_version_id
            openlibrary_work_id = records_data["details"]["details"]["works"][0]["key"].split("/")[-1]

            print_in_green("Finished downloading Open Library data!")

        return openlibrary_version_id, openlibrary_work_id, lccn
    return openlibrary_version_id, None, None