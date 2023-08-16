# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from handle_wikidata import get_value_from_property


dedication_mapping = {
        "my mother": [
            "mother",
        ],

        "my father": [
            "father",
        ],

        "my sister": [
            "sister",
        ],

        "my brother": [
            "brother",
        ],

        "my mother and father": [
            "mother",
            "father",
        ],

        "my father and mother": [
            "mother",
            "father",
        ],

        "my wife": [
            "wife",
        ],

        "my husband": [
            "husband",
        ],

        # "my children": [
        #     "children",
        # ],

        "my son": [
            "son",
        ],

        "my daughter": [
            "daughter",
        ],
    }

dedication_properties = {
    "mother": "P25",
    "father": "P22",
    "wife": "P26",
    "husband": "P27",
}

def get_dedication_page(page_data):
    for page in page_data:
        content = page["content"]
        marker = page["marker"]
        if marker == 'ded' or "/dedic/" in content:
            return page
    return None

def get_dedications(page_data, author_item):
    print("Retrieving dedications...")
    dedication_page = get_dedication_page(page_data)
    if not dedication_page:
        print_in_yellow("No dedication page found. Skipping step...")
        return None
    
    content = dedication_page["content"]
    content = content.lower()

    content = content.replace("\n\n", " ")
    content = content.replace("\n", " ")
    content = content.replace("<br>", " ")
    content = content.replace("<br />", " ")

    

    dedications_in_english = []

    for dedication in dedication_mapping:
        if dedication in content:
            # dedications_in_english.append(dedication)
            for name in dedication_mapping[dedication]:
                # if name in content:
                dedications_in_english.append(name)

    dedication_items = []

    for dedication in dedications_in_english:
        if dedication in dedication_properties:
            print_in_green(f"Found dedication: {dedication}")
            dedication_property = dedication_properties[dedication]
            dedication_item = get_value_from_property(author_item, dedication_property)
            dedication_items.append(dedication_item)
    
    # print(dedication_items)
    # exit()

    if len(dedication_items) == 0:
        print_in_yellow("No usable dedications found. Skipping step...")
        return None

    return dedication_items