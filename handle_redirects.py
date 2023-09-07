# WS_collection

# Handle combinations of different variations:

# Example: "Calm, Passive, & Gentle!"
### With exclamation variants ###
#* "Calm, Passive, and Gentle!" (oxford comma, no symbol)
#* "Calm, Passive and Gentle!" (no oxford comma)
#* "Calm, Passive & Gentle!" (no oxford comma, symbol)
### Without exclamation variants ###
#* "Calm, Passive, and Gentle" (oxford comma, no symbol)
#* "Calm, Passive and Gentle" (no oxford comma)
#* "Calm, Passive & Gentle" (no oxford comma, symbol)
#* "Calm, Passive, & Gentle" (oxford comma, symbol)


# Oxford comma
#* and
#* or
#* nor


# Ok so here's a plan for the combos:
{
    "prefix": None,
    "contains_replaceable_strings": [
        "&",
    ],
    "contains_end_symbol_combos": [],
    "ends_with_symbols": "!", # if "!!!", then redirect to "!" form
    "contains_oxford_comma": True,
}


# VARIANTS WITH OR WITHOUT OXFORD COMMAS
# Handle names like "To ————— of ————" -> "To — of —"
# [ HANDLE THIS TOO
    #     "...",
    #     " . . ."
    # ]
# [a-z]...[a-z] -> [a-z] . . . [a-z]
# [a-z] . . . [a-z] -> [a-z]...[a-z]
# [a-z] . . .$ -> [a-z]...$
# [a-z]...$ -> [a-z] . . .$
# ^... -> ^. . . 



import itertools
import pywikibot
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from edit_mw import save_page


defaultsort_prefixes = [
    # English
    "The",
    "A",
    "An",

    # # French
    # "Le ",
    # "La ",
    # "Les ",
    # "L'",

    # # Spanish
    # "El ",
    # "Los ",
    # "Las ",
]

redirect_words = [
    [
        "&",
        "and",
    ],
    [
        "Mr.",
        "Mr",
        "Mister",
    ],
    [
        "Mrs.",
        "Mrs",
    ],
    [
        "Ms.",
        "Ms",
    ],
    [
        "Dr.",
        "Dr",
        "Doctor",
    ],
    [
        "Prof.",
        "Prof",
        "Professor",
    ],
    [
        "Rev.",
        "Rev",
        "Reverend",
    ],
    [
        "Hon.",
        "Hon",
        "Honorable",
    ],
    [
        "Jr.",
        "Jr",
        "Junior",
    ],
    [
        "Sr.",
        "Sr",
        "Senior",
    ],
    [
        "St.",
        "St",
        "Saint",
    ],

    [
        "Grey",
        "Gray",
    ],
]

one_way_redirects = [
    [
        "O",
        "Oh",
    ],
    [
        "'n'",
        "and",
    ],
    [
        "o'",
        "of",
    ],
    [
        "an'",
        "and",
    ],
    [
        "Li'l",
        "Little",
    ],
]

end_symbol_combos = [
    ["?!", "?"],
]

ending_symbols = [
    ".",
    "!",
    "?",
    # "...",
    # ". . .",
    "—",
]




page_title_to_parse = "O Genteel Lady!"
redirect_target = page_title_to_parse # later, when dealing with disambig etc., this will be changed


def get_defaultsort_prefixes(words):
    defaultsort_prefix = ""

    for prefix in defaultsort_prefixes:
        if words[0] == prefix:
            # title_with_variants.append(words[1:])
            defaultsort_prefix = prefix
            words = words[1:]
            break
    
    return defaultsort_prefix, words

def generate_title_with_variants(words):
    title_with_variants = []

    # handle defaultsort prefixes
    

    for word_num, word in enumerate(words):
        variants_of_word = []
        last_word_index = len(words) - 1

        # one way redirects
        for redirect_combo in one_way_redirects:
            word_to_change = redirect_combo[0]
            variant_word = redirect_combo[1]
            if word == word_to_change:
                variants_of_word += redirect_combo

        for redirect_combo in redirect_words:
            if word in redirect_combo:
                variants_of_word += redirect_combo

        if word_num == last_word_index:
            # ending symbols
            for symbol in ending_symbols:
                if word.endswith(symbol):
                    variants_of_word.append(word[:-len(symbol)])
                    break

        if len(variants_of_word) == 0:
            title_with_variants.append(word)
        else:
            first_variant = variants_of_word[0]
            if first_variant != word and word not in variants_of_word:
                variants_of_word.insert(0, word)
            # remove duplicate values
            title_with_variants.append(variants_of_word)

    return title_with_variants

    # if isinstance(lst, str):
    #     return [lst]

    # combinations = []

    # if isinstance(lst, list):
    #     for item in lst:
    #         sub_combinations = generate_combinations(item)
    #         for sub_combination in sub_combinations:
    #             if combinations:
    #                 combinations = [comb + ' ' + sub_combination for comb in combinations]
    #             else:
    #                 combinations.append(sub_combination)
    # else:
    #     combinations.append(str(lst))

    # return combinations

def generate_combinations(title_with_variants, defaultsort_prefix):
    combinations = []

    title_with_variants = [p if type(p) == list else [p] for p in title_with_variants]

    for result in itertools.product(*title_with_variants):
        variant = " ".join(result)
        combinations.append(variant)
    
    if defaultsort_prefix:
        combinations += [defaultsort_prefix + " " + combination for combination in combinations]

    for title in combinations:
        if title.startswith("\"") and title.endswith("\""):
            combinations.append(title[1:-1])

    return combinations
 

    

    # for i in range(max_length):
    #     combo = []
    #     for sublist in sublists:
    #         if i < len(sublist):
    #             combo.append(str(sublist[i]))
    #     if combo:
    #         combinations.append(", ".join(combo))
    
    # return combinations

# sublists = [[1, 2, 8], [3, 4], [5, 6, 4, 2]]
# combinations = generate_combinations(sublists)

# for combination in combinations:
#     print(combination)

# exit()

def generate_variant_titles(page_title_to_parse):
    print(f"Generating variant titles for: {page_title_to_parse}")
    if "(" in page_title_to_parse:
        combinations = [page_title_to_parse]
    else:
        words = page_title_to_parse.split(" ")
        defaultsort_prefix, words = get_defaultsort_prefixes(words)
        title_with_variants = generate_title_with_variants(words)
        print(title_with_variants)
        combinations = generate_combinations(title_with_variants, defaultsort_prefix)
        combinations.remove(page_title_to_parse)
    combination_length = len(combinations)
    print_in_green(f"Successfully generated {combination_length} variant titles.")
    return combinations

def create_redirect(redirect_title, redirect_target, site, edit_summary):
    redirect_page = pywikibot.Page(site, redirect_title)
    redirect_text = f"#REDIRECT [[{redirect_target}]]"
    print(redirect_text)
    save_page(redirect_page, site, redirect_text, edit_summary)

def create_redirects(page_title_to_parse, redirect_target=None):
    if "(" in page_title_to_parse:
        if not redirect_target:
            print("Page title contains parentheses. Skipping redirects...")
            return
        else:
            print("Page title contains parentheses. Creating sole redirect...")

    variant_titles = generate_variant_titles(page_title_to_parse)
    
    if redirect_target:
        if page_title_to_parse not in variant_titles:
            variant_titles += [page_title_to_parse]
    else:
        redirect_target = page_title_to_parse
    
    number_of_variants = len(variant_titles)
    if number_of_variants == 0 and not redirect_target:
        print("No variant titles to create redirects for. Skipping redirects...")
    
    print(f"Creating redirects to {redirect_target}...")
    site = pywikibot.Site("en", "wikisource")
    for title_num, title in enumerate(variant_titles):
        title_num += 1
        print(f"Redirect {title_num} (of {number_of_variants}): {title}")
        
        if page_title_to_parse in variant_titles and len(variant_titles) == 1 and "(" in page_title_to_parse:
            edit_summary = "Creating disambiguating redirect (only one is needed because it contains parentheses)..."
        else:
            edit_summary = f"Creating redirect to {redirect_target} (variant {title_num} of {number_of_variants})"

        create_redirect(title, redirect_target, site, edit_summary)
    print_in_green("All redirect pages successfully created!")

# create_redirects("The Ifs of History")