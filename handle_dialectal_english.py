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
    "kilometre": "kilometer",
    "litre": "liter",
    "lustre": "luster",
    "theatre": "theater",

    # miscellaneous

    "grey": "gray",
}

ise_ize_variants = {
    "analyse": "analyze",
    "anglicise": "anglicize",
    "apologise": "apologize",
    "catechise": "catechize",
    "civilisation": "civilization",
    "civilise": "civilize",
    "colonise": "colonize",
    "criticise": "criticize",
    "emphasise": "emphasize",
    "epitomise": "epitomize",
    "fertilise": "fertilize",
    "fraternise": "fraternize",
    "galvanise": "galvanize",
    "generalise": "generalize",
    "harmonise": "harmonize",
    "idealise": "idealize",
    "idolise": "idolize",
    "immobilise": "immobilize",
    "immortalise": "immortalize",
    "improvise": "improvize",
    "immunise": "immunize",
    "individualise": "individualize",
    "industrialise": "industrialize",
    "initialise": "initialize",
    "itemise": "itemize",
    "legalise": "legalize",
    "localise": "localize",
    "macadamise": "macadamize",
    "maximise": "maximize",
    "memorise": "memorize",
    "minimise": "minimize",
    "optimise": "optimize",
    "organise": "organize",
    "oxidise": "oxidize",
    "patronise": "patronize",
    "realise": "realize",
    "realising": "realizing",
    "recognise": "recognize",
    "recognising": "recognizing",
    "scrutinise": "scrutinize",
    "specialise": "specialize",
    "stigmatise": "stigmatize",
    "symbolise": "symbolize",
    "sympathise": "sympathize",
    "utilise": "utilize",
}

# site = pywikibot.Site("en", "wikisource")

# transcription_page = pywikibot.Page(site, transcription_page_title)

# transcription_text = transcription_page.text

# for key,value in ise_ize_variants.items():
#     transcription_text = transcription_text.replace(key, value)
#     root = key[:-2]
#     transcription_text = transcription_text.replace(f"{root}sing", f"{root}zing")
#     transcription_text = transcription_text.replace(f"{root}sation", f"{root}zation")

# save_page(transcription_page, site, transcription_text, "Replacing certain British English words with American English in Gutenberg-based transcription layer...")