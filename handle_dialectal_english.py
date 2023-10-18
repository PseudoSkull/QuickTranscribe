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

    # miscellaneous

    "grey": "gray",
}

ise_ize_variants = {
    "analyse": "analyze",
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
    "idolise": "idolize",
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
    "recognise": "recognize",
    "scrutinise": "scrutinize",
    "specialise": "specialize",
    "stigmatise": "stigmatize",
    "sympathise": "sympathize",
    "utilise": "utilize",
}

site = pywikibot.Site("en", "wikisource")

transcription_page = pywikibot.Page(site, transcription_page_title)

transcription_text = transcription_page.text

for key,value in ise_ize_variants.items():
    transcription_text = transcription_text.replace(key, value)

save_page(transcription_page, site, transcription_text, "Replacing certain British English words with American English in Gutenberg-based transcription layer...")