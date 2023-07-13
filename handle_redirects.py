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


defaultsort_prefixes = [
    # English
    "The ",
    "A ",
    "An ",

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



def generate_title_with_variants(words):
    title_with_variants = []
    for word_num, word in enumerate(words):
        variants_of_word = []
        last_word_index = len(words) - 1

        # one way redirects
        for redirect_combo in one_way_redirects:
            word_to_change = redirect_combo[0]
            variant_word = redirect_combo[1]
            if word == word_to_change:
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
            if first_variant != word:
                variants_of_word.insert(0, word)
            # remove duplicate values
            title_with_variants.append(variants_of_word)

    return title_with_variants

def generate_combinations(title_with_variants):
    return
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

def generate_variant_titles(page_title_to_parse, redirect_target):
    redirects = []
    words = page_title_to_parse.split(" ")
    title_with_variants = generate_title_with_variants(words)
    # print(title_with_variants)
    combinations = generate_combinations(title_with_variants)
    print(combinations)


print(generate_variant_titles(page_title_to_parse, redirect_target))