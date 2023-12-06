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
from handle_title_case import convert_to_title_case
from handle_dialectal_english import british_english_words, ise_ize_variants
import inflect

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

british_english_words = [[us.capitalize(), uk.capitalize()] for us, uk in british_english_words.items()]
ise_ize_variants = [[us.capitalize(), uk.capitalize()] for us, uk in ise_ize_variants.items()]

british_english_words += ise_ize_variants

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

ordinals = {
    'First': '1st',
    'Second': '2nd',
    'Third': '3rd',
    'Fourth': '4th',
    'Fifth': '5th',
    'Sixth': '6th',
    'Seventh': '7th',
    'Eighth': '8th',
    'Ninth': '9th',
    'Tenth': '10th',
    'Eleventh': '11th',
    'Twelfth': '12th',
    'Thirteenth': '13th',
    'Fourteenth': '14th',
    'Fifteenth': '15th',
    'Sixteenth': '16th',
    'Seventeenth': '17th',
    'Eighteenth': '18th',
    'Nineteenth': '19th',
    'Twentieth': '20th',
    'Twenty-first': '21st',
    'Twenty-second': '22nd',
    'Twenty-third': '23rd',
    'Twenty-fourth': '24th',
    'Twenty-fifth': '25th',
    'Twenty-sixth': '26th',
    'Twenty-seventh': '27th',
    'Twenty-eighth': '28th',
    'Twenty-ninth': '29th',
    'Thirtieth': '30th',
    'Thirty-first': '31st',
    'Thirty-second': '32nd',
    'Thirty-third': '33rd',
    'Thirty-fourth': '34th',
    'Thirty-fifth': '35th',
    'Thirty-sixth': '36th',
    'Thirty-seventh': '37th',
    'Thirty-eighth': '38th',
    'Thirty-ninth': '39th',
    'Fortieth': '40th',
    'Forty-first': '41st',
    'Forty-second': '42nd',
    'Forty-third': '43rd',
    'Forty-fourth': '44th',
    'Forty-fifth': '45th',
    'Forty-sixth': '46th',
    'Forty-seventh': '47th',
    'Forty-eighth': '48th',
    'Forty-ninth': '49th',
    'Fiftieth': '50th',
    'Fifty-first': '51st',
    'Fifty-second': '52nd',
    'Fifty-third': '53rd',
    'Fifty-fourth': '54th',
    'Fifty-fifth': '55th',
    'Fifty-sixth': '56th',
    'Fifty-seventh': '57th',
    'Fifty-eighth': '58th',
    'Fifty-ninth': '59th',
    'Sixtieth': '60th',
    'Sixty-first': '61st',
    'Sixty-second': '62nd',
    'Sixty-third': '63rd',
    'Sixty-fourth': '64th',
    'Sixty-fifth': '65th',
    'Sixty-sixth': '66th',
    'Sixty-seventh': '67th',
    'Sixty-eighth': '68th',
    'Sixty-ninth': '69th',
    'Seventieth': '70th',
    'Seventy-first': '71st',
    'Seventy-second': '72nd',
    'Seventy-third': '73rd',
    'Seventy-fourth': '74th',
    'Seventy-fifth': '75th',
    'Seventy-sixth': '76th',
    'Seventy-seventh': '77th',
    'Seventy-eighth': '78th',
    'Seventy-ninth': '79th',
    'Eightieth': '80th',
    'Eighty-first': '81st',
    'Eighty-second': '82nd',
    'Eighty-third': '83rd',
    'Eighty-fourth': '84th',
    'Eighty-fifth': '85th',
    'Eighty-sixth': '86th',
    'Eighty-seventh': '87th',
    'Eighty-eighth': '88th',
    'Eighty-ninth': '89th',
    'Ninetieth': '90th',
    'Ninety-first': '91st',
    'Ninety-second': '92nd',
    'Ninety-third': '93rd',
    'Ninety-fourth': '94th',
    'Ninety-fifth': '95th',
    'Ninety-sixth': '96th',
    'Ninety-seventh': '97th',
    'Ninety-eighth': '98th',
    'Ninety-ninth': '99th',
}

words_often_lowercased = [
    "about",
    "am",
    "are",
    "into",
    "is",
    "onto",
    "was",
    "were",
    "with",
    "within",
    "without",
    "when",
    "where",
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
    
    inflect_engine = inflect.engine()

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
        
        # british english
        for british_english_combo in british_english_words:
            for item in british_english_combo:
                if item in word:
                    variants_of_word += british_english_combo

        # turn sixth into 6th
        for ordinal, cardinal in ordinals.items():
            if word == ordinal:
                variants_of_word.append(cardinal)

        # try:
        #     chapter_num_as_cardinal = inflect_engine.ordinal(word.lower()).capitalize()
        # except:
        #     chapter_num_as_cardinal = None

        # if chapter_num_as_cardinal:
        #     variants_of_word.append(chapter_num_as_cardinal)

        # print(new_word)  # Output: 6th
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
    site = pywikibot.Site("en", "wikisource")
    page_to_check = pywikibot.Page(site, page_title_to_parse)
    if "(" in page_title_to_parse and not page_to_check.exists():
        combinations = [page_title_to_parse]
    else:
        words = page_title_to_parse.split(" ")
        defaultsort_prefix, words = get_defaultsort_prefixes(words)
        title_with_variants = generate_title_with_variants(words)
        print(title_with_variants)
        combinations = generate_combinations(title_with_variants, defaultsort_prefix)
        combinations.remove(page_title_to_parse)
    if combinations == "":
        combinations = []
    combination_length = len(combinations)
    print_in_green(f"Successfully generated {combination_length} variant titles.")
    return combinations

def create_redirect(redirect_title, redirect_target, site, edit_summary):
    redirect_page = pywikibot.Page(site, redirect_title)
    redirect_text = f"#REDIRECT [[{redirect_target}]]"
    print(redirect_text)
    save_page(redirect_page, site, redirect_text, edit_summary)

def generate_subtitle_variants(page_title_to_parse, subtitle, second_subtitle, variant_titles):
    if subtitle:
        if "(" in page_title_to_parse:
            page_title_to_parse = page_title_to_parse.split(" (")[0]
        colon_subtitle_form = f"{page_title_to_parse}: {subtitle}"
        comma_subtitle_form = convert_to_title_case(f"{page_title_to_parse}, {subtitle}")
        variant_titles.append(colon_subtitle_form)
        variant_titles.append(comma_subtitle_form)

        if second_subtitle: # such as Jungle Joe: <Pride of the Circus>, <the Story of a Trick Elephant>
            variant_titles = generate_subtitle_variants(colon_subtitle_form, second_subtitle, None, variant_titles)
            variant_titles = generate_subtitle_variants(comma_subtitle_form, second_subtitle, None, variant_titles)
    return variant_titles


def create_redirects(page_title_to_parse, alternative_title=None, subtitle=None, second_subtitle=None, redirect_target=None):
    if "(" in page_title_to_parse and not subtitle:
        if not redirect_target:
            print("Page title contains parentheses. Skipping redirects...")
            return
        else:
            print("Page title contains parentheses. Creating sole redirect...")

    site = pywikibot.Site("en", "wikisource")
    variant_titles = generate_variant_titles(page_title_to_parse)
    if alternative_title:
        alias_variant_titles = generate_variant_titles(alternative_title)
        variant_titles.append(alternative_title)
        variant_titles += alias_variant_titles
    else:
        alias_variant_titles = None
    
    if redirect_target:
        if page_title_to_parse not in variant_titles:
            variant_titles += [page_title_to_parse]
    else:
        redirect_target = page_title_to_parse

    variant_titles = generate_subtitle_variants(page_title_to_parse, subtitle, second_subtitle, variant_titles)
    
    number_of_variants = len(variant_titles)
    if number_of_variants == 0 and not redirect_target:
        print("No variant titles to create redirects for. Skipping redirects...")
    
    print(f"Creating redirects to {redirect_target}...")
    print(variant_titles)
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