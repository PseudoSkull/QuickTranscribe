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