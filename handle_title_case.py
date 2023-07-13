# WS_collection

# Bugs:
# Handles "Wakefield Mandatory—The Title of Exexex" but not "Wakefield Mandatory: the Title of Exexex!!!!!!!!!!!!"
# "Jacob of the F.B.I. -> Jacob of the F."

import re
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break

beginning_punctuations_to_test = [
    '"',
    "(",
    "[",
    "{",
]

ending_punctuations_to_test = ["!", ".", ",", ";", ":", "?", ")", "]", "}" "\""]

title_case_exceptions = ['and', 'as', 'but', 'for', 'if', 'nor', 'or', 'so', 'yet',
                  'a', 'an', 'the',
                  'as', 'at', 'by', 'for', 'in', 'of', 'per', 'to', 'up', 'via',
                  # dubious
                  'on', 'off',
                  # abbreviations
                  'etc', 'cf', 'c.f', 'e.g', 'i.e', 'ie', 'vs', 'v', 'viz',
                  # pronunciation spelling
                  'an\'', 'o\'', '\'n\'', '\'n', 'n\'', 'fer',
]

conditional_exceptions = [
    'off',
    'on',
]

conditional_punctuation = [
    "\'"
]

punctuation_exceptions = [
    ": ",
    ". ",
    "! ",
    "? ",
    "—", # em dash
    "/",
]


word_before_ending_punctuation_pattern = r'[A-Za-z]+?'


def get_beginning_punctuation(word):
    first_letter = word[0]
    for punctuation in beginning_punctuations_to_test:
        if first_letter == punctuation:
            return first_letter
    return ""

def get_ending_punctuation(word):
    for punctuation in ending_punctuations_to_test:
        ending_punctuation_pattern = rf'{word_before_ending_punctuation_pattern}(\{punctuation}+)'
        ending_punctuation_matches = re.search(ending_punctuation_pattern, word)
        if ending_punctuation_matches:
            ending_punctuation = ending_punctuation_matches.group(1)
            return ending_punctuation
    return ""


def remove_beginning_punctuation(beginning_punctuation, text):
    if beginning_punctuation != "":
        text = text[1:]
    return text

def remove_ending_punctuation(ending_punctuation, word):
    if ending_punctuation != "":
        pattern = rf'({word_before_ending_punctuation_pattern}){re.escape(ending_punctuation)}'
        matches = re.search(pattern, word)
        if matches:
            # print("Matches")
            word = matches.group(1)
    return word


def convert_word_to_title_case(word_num, word, capitalize_all=False):
    beginning_punctuation = get_beginning_punctuation(word)
    word = remove_beginning_punctuation(beginning_punctuation, word)
    # print(f"Word after removed beginning punctuation: {word}")
    # ending_punctuation = get_ending_punctuation(word)
    # print(f"Ending punctuation: {word}")
    # word = remove_ending_punctuation(ending_punctuation, word)
    # print(f"Word after removed ending punctuation: {word}")
    # print(f"Word after removed ending punctuation: {word}")
    # for exception in conditional_exceptions:
    #     if exception.lower() == word:
    #         print_in_yellow(f"Conditional exception \"{exception}\" found. Do you want to lowercase it? (y/n)")
    #         answer = process_break()
    #         if answer == "" or answer == "y":
    #             word = beginning_punctuation + word + ending_punctuation
    #             return word.lower()
    # print(f"Ending punctuation of \"{word}\": {ending_punctuation}")
    if word_num == 0:
        word = word.capitalize()
    else:
        if word.lower() not in title_case_exceptions:
            if "." in word and word.upper() == word:
                pass # handling exceptions with abbreviations, like "U.S.", "F.B.I."
            else:
                word = word.capitalize()
        else:
            if capitalize_all:
                word = word.capitalize()
            else:
                word = word.lower()
    word = beginning_punctuation + word
    return word

def handle_apostrophes(word):
    apostrophe = "'"
    if word[0] == apostrophe:
        print_in_yellow(f"Apostrophes found in word \" {word} \". Do you want to lowercase it? (y/n)")
        answer = process_break()
        print(answer)
        if answer == "y":
            return word.lower()
        else:
            return f"{(word[0].upper() if word[0] is not apostrophe else word[0])}{word[1].upper() if word[0] is apostrophe else word[1]}{word[2:]}" # temporary messy solution
    return word

def handle_punctuation_exceptions(word):
    for punctuation in punctuation_exceptions:
        last_symbol_of_word = word[-1]
        if punctuation in word and last_symbol_of_word != punctuation:
            split_words = word.split(punctuation)
            new_words = []
            for split_word_num, split_word in enumerate(split_words):
                new_word = convert_word_to_title_case(split_word_num, split_word, capitalize_all=True)
                new_words.append(new_word)
            word = punctuation.join(new_words)
    return word

def convert_to_title_case(text):
    # Define the exceptions

    print(f"Converting {text} to title case...")

    # Initialize the result list
    result = []

    # Split the text into words
    words = text.split()

    # Iterate over the words
    for word_num, word in enumerate(words):
        word = convert_word_to_title_case(word_num, word)
        word = handle_punctuation_exceptions(word)
        word = handle_apostrophes(word)

        # Add the reconstructed word to the result list
        result.append(word)

    # Join the words back into a string
    title_case_text = ' '.join(result)
    print_in_green(f"Converted to title case! \"{text}\" -> \"{title_case_text}\"")
    return title_case_text





# print_in_blue(convert_to_title_case("THE RAKE'S PROGRESS"))
# print_in_blue(convert_to_title_case("'THE RAKE'S PROGRESS'"))
# print_in_blue(convert_to_title_case("\"THE RAKE'S PROGRESS\""))
# print_in_blue(convert_to_title_case("\"Over the hills and UNDER THE BRIDGE\""))
# print_in_blue(convert_to_title_case("LITTLE \"JOHN\""))
# print_in_blue(convert_to_title_case("Wakefield mandatory: the title of exexex!!!!!!!!!!!!"))
# print_in_blue(convert_to_title_case("Wakefield mandatory: title (Of) exexex"))
# print_in_blue(convert_to_title_case("Wakefield mandatory—the title Of exexex"))
# print_in_blue(convert_to_title_case("Wakefield mandatory—the title of!"))
# print_in_blue(convert_to_title_case("Poems, sonnets, e.g. daffodils"))
# print_in_blue(convert_to_title_case("Poems, sonnets, etc"))
# print_in_blue(convert_to_title_case("Poems, sonnets, etc."))
# print_in_blue(convert_to_title_case("Jacob of the F.B.I."))
# print_in_blue(convert_to_title_case("Jacob of the F. B. I."))
# print_in_blue(convert_to_title_case("Jacob on the F. B. I."))

