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

from edit_mw import save_page, is_even
from handle_wikidata import handle_file
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from spellchecker import SpellChecker

consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 't', 'v', 'w', 'x', 'z']

consonants_that_should_never_combine = [
    'j',
    'k',
    'q',
    'z',
]

named_chapter_pattern = r"\/ch\/.+?\n\n"
named_chapter_pattern_with_settings = r"\/ch\/.+?\/.+?\n\n"
empty_chapter_pattern = r"\/ch\/\n\n"

chapter_pattern = rf"({named_chapter_pattern}|{named_chapter_pattern_with_settings}|{empty_chapter_pattern})"

def use_spellchecker(text):
    print("Using spellchecker...")
    spell_checker = SpellChecker()
    misspelled = spell_checker.unknown(text.split(" "))
    if len(misspelled) == 0:
        print_in_green("No misspelled words found.")
    else:
        print_in_yellow("Misspelled words found:")
        print_in_yellow(misspelled)
        return misspelled

def remove_triple_newlines(text):
    while 1:
        if "\n\n\n" in text:
            text = re.sub(r"\n\n\n", r"\n\n", text)
        else:
            break
    return text

def initial_text_cleanup(text, work_type_name):
# do regex replacements on page.text. Make sure it replaces all instances of string pattern.
    # text = page.text
    print("Doing some initial text cleanup...")

    # Replace instances of —t3 with "—\n\n—\n\n—" for example, shorthand for multiple non-proofreadable pages
    text = re.sub(r'—t(\d+?)\n', lambda m: '—\n\n' * int(m.group(1)), text)

    text = remove_triple_newlines(text)
    text = re.sub(r"\n ", r"\n", text)
    text = re.sub(r" \n", r"\n", text)
    text = text.replace("\nm\n", "\nn\n")
    text = text.replace("\nnb\n", "\nn\n")
    text = text.replace("\nnm\n", "\nn\n")
    text = text.replace("\nmn\n", "\nn\n")
    text = text.replace("=\n\n-\n\n", "-\n\n-\n\n")
    text = text.replace("\nb\n", "\nn\n")
    text = text.replace("\nh\n", "\nn\n")
    text = text.replace("<br>", "<br />")
    text = text.replace("{{hr|", "{{rule|")
    text = text.replace("{{hr}}", "{{rule}}")
    text = text.replace("/oe/", "œ")
    text = text.replace("/brp/", "£")
    text = text.replace("/x/", "×")
    text = text.replace("/OE/", "Œ")
    text = text.replace("/ss/", "§")

    # fractions
    text = text.replace("/1/4/", "¼")
    text = text.replace("/1/2/", "½")
    text = text.replace("/3/4/", "¾")
    text = text.replace("/1/5/", "⅕")
    text = text.replace("/1/6/", "⅙")
    text = text.replace("/5/6/", "⅚")
    text = text.replace("/1/7/", "⅐")
    
    text = text.replace("/1/8/", "⅛")
    text = text.replace("/1/9/", "⅑")
    text = text.replace("/1/10/", "⅒")
    text = text.replace("/1/3/", "⅓")
    text = text.replace("/2/3/", "⅔")
    
    text = text.replace("\nd\n", "\n/d/\n")
    text = text.replace("\n/d/\n-", "\n/d/\n\n-")
    text = text.replace("\ns\n", "\n\n/sec/\n\n")
    text = text.replace("\n/s/\n", "\n/sec/\n")
    text = re.sub(r"\n\n-\n\nn\n\n", r"\n/n/\n\n-\n\n", text)
    text = re.sub(r"(.)\nn", r"\1\n/n/", text)
    text = re.sub(r"(.)\nn", r"\1\n/n/", text)
    text = re.sub(r"(.)\n/n/\n([- —])", r"\1\n/n/\n\n\2", text)
    if work_type_name != "poetry collection":
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
        if line_suffix == "1n":
            count = 0
        page_num_format = ""
        line_prefix = line[:1]
        line_length = len(line)
        if line_length <= 4 and (line_prefix == "-" or line_prefix == "—"):
            if line_suffix.isdigit() or (line_suffix == "" and line_prefix == "-") or (line_suffix == "p" and line_prefix == "—") or line_suffix.endswith("r") or line_suffix.endswith("n"):
                can_count_number = True
                if line_suffix.endswith("r") or line_suffix.endswith("n"):
                    page_num_format = line_suffix[-1]
            elif (line_prefix == "—" and line_suffix != "p") or not line_suffix.isdigit() or line_suffix != "":
                can_count_number = False
            # replace line with count                
            if can_count_number:
                count += 1
                new_text_to_parse.append(f"{line_prefix}{count}{page_num_format}")
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
    repeated_characters_pattern = r'(.)\1{2,}'  # Matches any character (.) repeated three or more times (\1{3,})
    repeated_characters = re.findall(repeated_characters_pattern, text)

    if len(repeated_characters) == 0:
        print_in_green("No repeated characters, 3 or more, patterns found.")
    else:
        print_in_yellow("Repeated characters, 3 or more, patterns found:")
        print_in_yellow(repeated_characters)

    return repeated_characters

def find_uneven_quotations(text):
    text = text.split("\n\n")

    lines_with_odd_double_quotes = []

    for line_num, line in enumerate(text):
        number_of_double_quotes = line.count("\"")
        try:
            previous_line = text[line_num-1]
        except IndexError:
            previous_line = ""

        try:
            next_line = text[line_num+1]
        except IndexError:
            next_line = ""
        
        if not is_even(number_of_double_quotes):
            # print_in_yellow(f"Uneven quotations found: {line}")
            if next_line.startswith("-") or next_line.startswith("—") or previous_line.startswith("-") or previous_line.startswith("—"):
                continue

            # continued quotations across paragraphs

            ## He said, <">Well, I don't know.\n\n"Here's an explanation: ...\n\n"Here's a continued explanation..."
            if not previous_line.endswith("\"") and "\"" in previous_line and line.startswith("\"") and number_of_double_quotes == 1:
                continue
            ## He said, "Well, I don't know.\n\n<">Here's an explanation: ...
            if next_line.startswith("\"") and line.startswith("\"") and number_of_double_quotes == 1:
                continue

            lines_with_odd_double_quotes.append(line)
    
    if len(lines_with_odd_double_quotes) == 0:
        print_in_green("No potentially problematic odd numbers of quotes found.")
    else:
        print_in_yellow("Potentially problematic odd numbers of quotes found:")
        for paragraph_num, paragraph in enumerate(lines_with_odd_double_quotes):
            print_in_yellow(f"{paragraph_num}: {paragraph}")
    
    return lines_with_odd_double_quotes



def find_long_substrings(text):
    long_substrings = []
    current_substring = ""

    for char in text:
        if char.isalpha() or char == "'":
            current_substring += char
        else:
            if len(current_substring) >= 10:
                long_substrings.append(current_substring)
            current_substring = ""

    # if len(current_substring) > 10:
    #     long_substrings.append(current_substring)

    long_substrings = list(set(long_substrings))

    long_substrings.sort(key=len, reverse=True)

    if len(long_substrings) == 0:
        print_in_green("No long words of 10 or more letters found.")
    else:
        print_in_yellow("Long words of 10 or more letters found:")
        print_in_yellow(long_substrings)

    return long_substrings

def find_consonant_combos(text):
    consonant_combos = []
    current_substring = ""

    for char in text:
        if char in consonants:
            current_substring += char
        else:
            if len(current_substring) >= 4:
                consonant_combos.append(current_substring)
            current_substring = ""
    
    consonant_combos = list(set(consonant_combos))
    consonant_combos.sort(key=len, reverse=True)

    if len(consonant_combos) == 0:
        print_in_green("No likely problematic consonant combos found.")
    else:
        print_in_yellow("Likely problematic consonant combos found:")
        print_in_yellow(consonant_combos)




## DROP INITIALS ##

def get_drop_initial_letter(content):
    quote_pattern = r"\"?\'?"

    chapter_beginning_pattern = rf"{chapter_pattern}(.)(.)"

    chapter_beginning = re.search(chapter_beginning_pattern, content)

    chapter_heading = chapter_beginning.group(1)
    first_letter = chapter_beginning.group(2)
    second_letter = chapter_beginning.group(3)
    
    if first_letter == "\"" or first_letter == "'":
        return second_letter
    
    return first_letter

def modify_drop_initial_data(drop_initials, marker, drop_initial_letter):
    new_drop_initials = []
    drop_initial_exists = False
    for drop_initial in drop_initials:
        if drop_initial["letter"] == drop_initial_letter:
            drop_initial["pages"].append(marker)
            drop_initial_exists = True
        new_drop_initials.append(drop_initial)
    
    if not drop_initial_exists:
        drop_initial = {
            "pages": [marker],
            "letter": drop_initial_letter,
        }
        new_drop_initials.append(drop_initial)
    
    drop_initials = new_drop_initials

    return drop_initials

def find_drop_initial_letters(page_data, chapter_beginning_formatting):
    if chapter_beginning_formatting != "dii":
        print_in_green("No drop initial images in page.")
        return
    drop_initials = []
    for page in page_data:
        content = page["content"]
        marker = page["marker"]
        if "/ch/" not in content:
            continue
        drop_initial_letter = get_drop_initial_letter(content)
        
        drop_initials = modify_drop_initial_data(drop_initials, marker, drop_initial_letter)
    
    drop_initials = sorted(drop_initials, key=lambda x: x["letter"])

    print_in_green("Drop initial images start each chapter. Initials found:")

    for drop_initial in drop_initials:
        letter = drop_initial["letter"]
        pages = drop_initial["pages"]
        pages = ", ".join(pages)
        print_in_green(f"{letter}: {pages}")

    # process_break()
    return drop_initials














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



