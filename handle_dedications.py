# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break

def get_dedication_page(page_data):
    for page in page_data:
        content = page["content"]
        marker = page["marker"]
        if marker == 'ded' or "/dedic/" in content:
            return page
    return None

def get_dedications(page_data):
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

    dedications_in_english = []

    for dedication in dedication_mapping:
        if dedication in content:
            # dedications_in_english.append(dedication)
            for name in dedication_mapping[dedication]:
                # if name in content:
                dedications_in_english.append(name)
    print(dedications_in_english)
    return dedications_in_english