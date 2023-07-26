#WS_collection
"""
\n\n\n -> \n\n (twice)
\n\n-\n\nn\n\n -> /n/\n\n-\n\n
(.)—\n\n- -> $1{{peh|—}}\n\n-
(.)\n\n-\n\n—(.) -> $1{{peh|}}\n\n-\n\n—$2
"\n " -> "\n"
" \n" -> "\n"


# Look for " f " or " H ", things like that
# Look for sentences not ending in periods
# Look for obvious words starting a page, that should be hyphenated beforehand. Such as "ing", "ed".
# Look for symbols that should really never be in the text, such as "►" or "■"
# list instances of " 1 "









\n\n-\n\n

"""

import pywikibot
import re

from edit_mw import save_page
from handle_wikidata import handle_file
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break

def initial_text_cleanup(text):
# do regex replacements on page.text. Make sure it replaces all instances of string pattern.
    # text = page.text
    print("Doing some initial text cleanup...")
    while 1:
        if "\n\n\n" in text:
            text = re.sub(r"\n\n\n", r"\n\n", text)
        else:
            break
    text = re.sub(r"\n ", r"\n", text)
    text = re.sub(r" \n", r"\n", text)
    text = text.replace("<br>", "<br />")
    text = text.replace("{{hr|", "{{rule|")
    text = text.replace("{{hr}}", "{{rule}}")
    text = text.replace("/oe/", "œ")
    text = text.replace("\nd\n", "\n/d/\n")
    text = re.sub(r"\n\n-\n\nn\n\n", r"\n/n/\n\n-\n\n", text)
    text = re.sub(r"(.)\nn", r"\1\n/n/", text)
    text = re.sub(r"(.)\n/n/\n([- —])", r"\1\n/n/\n\n\2", text)
    text = re.sub(r"(.)\n\n-\n\n—(.)", r"\1{{upe}}\n\n-\n\n—\2", text) #check back up on this one later
    text = re.sub(r"(.)—\n\n-", r"\1{{peh|—}}\n\n-", text)
    text = re.sub(r"\n\n—\n\n([A-Za-z])", r"\n\n—\n\n-\n\n\1", text) # fix page quality 0 with content
    text = re.sub(r"\n\n—p\n\n([A-Za-z])", r"\n\n—p\n\n-\n\n\1", text) # fix page quality 0 with content


    # save page.text

    # save_page(page, site, text, "Doing initial bare text cleanup.")
    return text

def deconstruct(list):
    # for deconstructing nested lists
    return [word for sublist in list for word in sublist]

def doublesplit(str, list):
    # for splitting a list of strings by a string
    return deconstruct([item.split(str) for item in list])

def remove_non_alphabetic_chars(word_list):
    cleaned_list = []
    for word in word_list:
        cleaned_word = ''.join(c for c in word if c.isalpha() or c in ["'", "-"])
        cleaned_list.append(cleaned_word)
    return cleaned_list

def remove_wiki_markup(word_list):
    filtered_list = []
    for word in word_list:
        if ("{" in word or
            "}" in word or
            "[" in word or
            "]" in word or
            "|" in word or
            "/" in word or
            "=" in word
        ):
            continue
        filtered_list.append(word)
    return(filtered_list)

def remove_short_characters_and_page_nums(word_list):
    filtered_list = []
    for word in word_list:
        if (len(word) > 2 and
            not word.startswith("-") and
            not word.startswith("—") and
            not word.endswith("-") and
            not word.endswith("—")
        ):
            filtered_list.append(word)
    return filtered_list

def remove_duplicates(word_list):
    return list(set(word_list))

def get_all_words(text, lower=True, can_remove_NAC=True):
    # Split by newline character
    print("Generating a list of all words...")
    if lower:
        text = text.lower()
    lines = text.split("\n")
    # Split each line by space character as well
    words_without_spaces = doublesplit(" ", lines)
    words_without_emdashes = doublesplit("—", words_without_spaces)
    words_without_wiki_markup = remove_wiki_markup(words_without_emdashes)
    if can_remove_NAC:
        words_without_non_alphabetic_chars = remove_non_alphabetic_chars(words_without_wiki_markup)
    else:
        words_without_non_alphabetic_chars = words_without_wiki_markup
    words_without_short_characters_and_page_nums = remove_short_characters_and_page_nums(words_without_non_alphabetic_chars)
    words_without_duplicates = remove_duplicates(words_without_short_characters_and_page_nums)
    print_in_green("List of all words generated.")
    return words_without_duplicates

def find_hyphenation_inconsistencies(text):
    words = get_all_words(text)
    print("Checking for hyphenation inconsistencies...")
    hyphenation_inconsistencies = []
    for word in words:
        if "-" in word:
            non_hyphenated_word = word.replace('-', '')
            if non_hyphenated_word in words:
                hyphenation_inconsistencies.append(word)
    hyphenation_inconsistencies.sort()
    if len(hyphenation_inconsistencies) == 0:
        print_in_green("No hyphenation inconsistencies found.")
    else:
        print_in_yellow("Hyphenation inconsistencies found:")
        print_in_yellow(hyphenation_inconsistencies)
        return hyphenation_inconsistencies

def print_scanno_message(word, letter, letter_num, condition):
    print_in_yellow(f"Found probable scanno \"{word}\" at letter \"{letter}\" (position {letter_num}) because of condition \"{condition}\"...")
    # scannos.append(word)

def find_probable_scannos(text):
    print("Checking for probable scannos...")

    words = get_all_words(text, lower=False, can_remove_NAC=False)

    # scanno_patterns = [
    #     r'[A-Za-z][a-z]+([A-Z]+)[a-z]+', # Unusual capitalization
    #     r'[A-Za-z][A-Za-z]+([^A-Za-z|—|-|\']+)[A-Za-z]+', # Unwanted symbol in middle of word
    #     r'([^A-Za-z|—|-|"|\']+)[A-Za-z]+', # Unwanted symbol at beginning of word
    # ]
    
    scannos = []
    for word in words:
        full_word_uppercase = (word.upper() == word)
        for letter_num, letter in enumerate(word):
            
            if letter_num == 0: # checking first letter conditions
                if (not letter.isalpha()) and letter != "\"" and letter != "'" and letter != "-" and letter != "—" and letter != "(":
                # if letter.isascii():
                    print_scanno_message(word, letter, letter_num, "first letter issues")
                    scannos.append(word)
                    break
                continue
            # print(f"Did I get to 1 {word}")
            previous_letter = word[letter_num-1]

            next_letter = ""
            if letter_num < len(word)-1:
                next_letter = word[letter_num+1]

            two_letters_down = ""
            if letter_num < len(word)-2:
                two_letters_down = word[letter_num+1]

            if letter.isupper() and (previous_letter == "'" or previous_letter == "\"" or previous_letter == "-" or previous_letter == "—"):
                continue

            if (letter == "?" or letter == "," or letter == "." or letter == ";" or letter == ":" or letter == "!") and next_letter == "'" and two_letters_down == "'":
                continue

            if not full_word_uppercase:
                if letter.isupper():
                    # if not previous_letter == "-" and not previous_letter == "—":
                    print_scanno_message(word, letter, letter_num, "uppercase letter in middle of word")

                    scannos.append(word)
                    # print("isuppercase")
                    break
            
            if letter_num == len(word)-1:
                if letter.isdigit():
                    print_scanno_message(word, letter, letter_num, "last letter digit")
                    scannos.append(word)
                break

            if letter != "'" and letter != "-" and letter != "—":
                if next_letter == "\"":
                    if letter == "?" or letter == "," or letter == "." or letter == ";" or letter == ":" or letter == "!":
                        continue
                if not letter.isalpha():
                    print_scanno_message(word, letter, letter_num, "non-alphabetic character")
                    scannos.append(word)
                    break

    # Create a new list to store the filtered elements
    filtered_scannos = []

    take_out_contains = [
        "<br",
        "...",
    ]

    take_out_endswith = [
        ",\"",
        ".\"",
        "!\"",
        "?\"",

        ",'",
        ".'",
        "!'",
        "?'",
    ]

    # Iterate over the original list
    for scanno in scannos:
        # Check if "<br" or "..." is present in the element
        to_continue_function = False
        for symbol in take_out_contains:
            if symbol in scanno:
                # filtered_scannos.append(scanno)
                to_continue_function = True
                break
        if to_continue_function:
            continue
        for symbol in take_out_endswith:
            if scanno.endswith(symbol):
                # filtered_scannos.append(scanno)
                to_continue_function = True
                break
        if to_continue_function:
            continue
        filtered_scannos.append(scanno)

    scannos = filtered_scannos
    
    print("\n\n\n")
    if len(scannos) == 0:
        print_in_green("No scannos were detected with the used patterns.")
    else:
        print_in_yellow("Probable scannos found:")
        print_in_yellow(scannos)
        return scannos


def split_string_by_newline(string):
    return string.split("\n\n")

def check_transcription_page_count(text):
    print("Checking total page count...")
    text_parsed = split_string_by_newline(text)
    count = 0
    for line in text_parsed:
        line_prefix = line[:1]
        line_length = len(line)
        if line_prefix == "-" or line_prefix == "—":
            if line_length <= 4:
                count += 1
    return count

# import pywikibot


def get_commons_file_page_count(file_title):
    print("Checking page count of scan file on Commons...")
    file_page = handle_file(file_title)
    file_metadata = file_page.latest_file_info
    if file_metadata['mime'] in ['application/pdf', 'image/vnd.djvu']:
        page_count = file_metadata['pagecount']
        if page_count is not None:
            print_in_green("Page count of original scan file retrieved.")
            return page_count
        else:
            print_in_red(f"Unable to determine page count for file: {file_title}")
    else:
        print_in_red(f"File {file_title} is not a PDF or DjVu file.")
    return None

def compare_page_counts(transcription_text, filename):
    transcription_page_count = check_transcription_page_count(transcription_text)
    scan_page_count = get_commons_file_page_count(filename)

    print("\n\n\n")

    numbers_being_compared = "Total page counts on original scan and transcription document"
    if transcription_page_count == scan_page_count:
        print_in_green(f"{numbers_being_compared} match! Count: {transcription_page_count}")
    else:
        print_in_red(f"{numbers_being_compared} DO NOT MATCH, PLEASE FIX!\nScan: {scan_page_count}\nTranscription: {transcription_page_count}")
        exit()

# Example usage
# if page_count is not None:
#     print(f"Page count: {page_count}")

def place_page_numbers(text):
    print("Modifying page text with the page numbers...")
    text_parsed = split_string_by_newline(text)
    new_text_to_parse = []
    count = 0
    can_count_number = False
    for line in text_parsed:
        line_suffix = line[1:]
        line_prefix = line[:1]
        line_length = len(line)
        if line_length <= 4 and (line_prefix == "-" or line_prefix == "—"):
            if line_suffix.isdigit() or (line_suffix == "" and line_prefix == "-") or (line_suffix == "p" and line_prefix == "—"):
                can_count_number = True
            elif (line_prefix == "—" and line_suffix != "p") or not line_suffix.isdigit() or line_suffix != "":
                can_count_number = False
            # replace line with count                
            if can_count_number:
                count += 1
                new_text_to_parse.append(f"{line_prefix}{count}")
                continue
        new_text_to_parse.append(line)
    print_in_blue(f"Numbered page count: {count}")
    return "\n\n".join(new_text_to_parse)


def find_paragraphs_without_ending_punctuation(text):
    print("Finding paragraphs without ending punctuation...")
    paragraphs = text.split("\n\n")
    paragraphs_without_ending_punctuation = []
    for paragraph_num, paragraph in enumerate(paragraphs):
        try:
            next_paragraph = paragraphs[paragraph_num+1]
        except IndexError:
            next_paragraph = ""

        if len(paragraph) > 4 and "/po/" not in paragraph and "\n:" not in paragraph and "=" not in paragraph and not next_paragraph.startswith("-") and not next_paragraph.startswith("—"):
            last_letter = paragraph[-1]
            if last_letter.isalpha():
                paragraphs_without_ending_punctuation.append(paragraph)
    
    if len(paragraphs_without_ending_punctuation) == 0:
        print_in_green("No paragraphs found missing ending punctuation.")
    else:
        print_in_yellow("Paragraphs found missing ending punctuation:")
        for paragraph_num, paragraph in enumerate(paragraphs_without_ending_punctuation):
            print_in_yellow(f"{paragraph_num}: {paragraph}")

    return paragraphs_without_ending_punctuation

def find_irregular_single_symbols(text):
    print("Finding irregular single symbols...")
    acceptable_single_symbols = [
        "a",
        "A",
        "I",
        "O",
        "à",
        ".",
        "&",
    ]

    single_symbols_with_spaces = re.findall(r" (.) ", text)

    single_symbols_with_spaces = list(set(single_symbols_with_spaces))

    bad_symbols_with_spaces = []

    for letter in single_symbols_with_spaces:
        if letter not in acceptable_single_symbols:
            bad_symbols_with_spaces.append(letter)
    
    if len(bad_symbols_with_spaces) == 0:
        print_in_green("No bad individual spaced symbols found.")
    else:
        print_in_yellow("Bad individual spaced symbols found:")
        print_in_yellow(bad_symbols_with_spaces)
    
    return bad_symbols_with_spaces


def find_possible_bad_quotation_spacing(text):
    bad_quotation_spacing_pattern = r"([^\/n\/]\n\n-(.+?)\n\n\")"
    bad_quotation_spacing = re.findall(bad_quotation_spacing_pattern, text)

    if "\" \"" in text:
        # print_in_yellow("Found \" \" pattern.")
        bad_quotation_spacing.append("\" \"")

    if len(bad_quotation_spacing) == 0:
        print_in_green("No bad quotation spacing patterns found.")
    else:
        print_in_yellow("Bad quotation spacing patterns found:")
        print_in_yellow(bad_quotation_spacing)
    
    return bad_quotation_spacing

def find_repeated_characters(text):
    repeated_characters_pattern = r'(.)\1{3,}'  # Matches any character (.) repeated three or more times (\1{3,})
    repeated_characters = re.findall(repeated_characters_pattern, text)

    if len(repeated_characters) == 0:
        print_in_green("No repeated characters, 3 or more, patterns found.")
    else:
        print_in_yellow("Repeated characters, 3 or more, patterns found:")
        print_in_yellow(repeated_characters)

    return repeated_characters


# checking total pages against the Commons scan file
# filename = 'Jalna.pdf'

# commons_page_count = get_commons_file_page_count(filename)
# site = pywikibot.Site('en', 'wikisource')
# total_page_count = check_total_page_count(page.text)
# compare_page_counts(total_page_count, commons_page_count)

# process_break()

# # place page numbers and check numbered page count

# transcription_with_page_numbers = place_page_numbers(page.text)
# save_page(page, site, transcription_with_page_numbers, "Placing page numbers...")

# check_numbered_page_count(page.text)



