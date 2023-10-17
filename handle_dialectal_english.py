# WS_collection

import pywikibot
from config import transcription_page_title

from edit_mw import save_page


british_english_words = {
    # our -> or variants
    "colour": "colour",
    "flavour": "flavor",
    "favour": "favor",
    "honour": "honor",
    "humour": "humor",
    "labour": "labor",
    "neighbour": "neighbor",
    "odour": "odor",
    "rigour": "rigor",

    # re -> er variants
    "centre": "center",
    "fibre": "fiber",
    # "kilometre": "kilometer",
    # "litre": "liter",
    # "lustre": "luster",
    # "theatre": "theater",

    # ise -> ize variants
    "analyse": "analyze",
    "catechise": "catechize",
    "criticise": "criticize",
    "emphasise": "emphasize",
    "epitomise": "epitomize",
    "fertilise": "fertilize",
    "fraternise": "fraternize",
    "generalise": "generalize",
    "harmonise": "harmonize",
    "idolise": "idolize",
    "itemise": "itemize",
    "legalise": "legalize",
    "localise": "localize",
    "maximise": "maximize",
    "memorise": "memorize",
    "minimise": "minimize",
    "optimise": "optimize",
    "organise": "organize",
    "patronise": "patronize",
    "realise": "realize",
    "recognise": "recognize",
    "specialise": "specialize",
    "stigmatise": "stigmatize",
    "sympathise": "sympathize",
    "utilise": "utilize",

    # miscellaneous

    "grey": "gray",
}

site = pywikibot.Site("en", "wikisource")

transcription_page = pywikibot.Page(site, transcription_page_title)

transcription_text = transcription_page.text

for key,value in british_english_words.items():
    transcription_text = transcription_text.replace(key, value)

save_page(transcription_page, site, transcription_text, "Replacing British English with American English in Gutenberg-based transcription...")