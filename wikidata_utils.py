# WS_collection
# Temporary solution to circular import between handle_wikidata and handle_wikisource_conf

from debug import print_in_red, print_in_green, print_in_yellow

def is_wikidata_item(value):
    print(f"Determining if value \"{value}\" is a Wikidata item...")
    value_id = value[1:]
    if value.startswith('Q') and value_id.isdigit():
        print_in_green(f"Value {value} is a Wikidata item.")
        return True
    else:
        print_in_yellow(f"Value {value} is not a Wikidata item.")
        return False

def get_common_wikidata_item(key, dictionary):
    if not is_wikidata_item(key):
        print("Looking for commonly used Wikidata item value in dictionary...")
        try:
            item = dictionary[key]
            print_in_green(f"Found basic value in dictionary: {item}")
            return item
        except KeyError:
            print_in_red(f"Couldn't find basic value in dictionary.")
            return None
    else:
        return key