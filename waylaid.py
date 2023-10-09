# WS_collection

# -*- coding: utf-8 -*-
print("Importing pywikibot...")
import pywikibot
print("Imported!")
import re
import sys
import time
import random
from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
# T'll WAS STILL IN THE TEXT AFTER BEING SUPPOSEDLY CORRECTED. WHAT HAPPENED THIS TIME?????

def correct_text(text_file, work_type):
    print("Parsing OCR...")

    poetry = False

    if work_type == "pc":
        poetry = True

    y = open(text_file, "r")

    y = y.read()
    x=y

    # add templates to beginning

    y = y.splitlines()

    c = 0

    l = []
    # FOR WILD GOOSE CHASE
    secondline = []

    for line in y:
        if line == "":
            line = "\n\n"
        # line = line.rstrip()
        if line.endswith("-") or line.endswith("¬"):
            line = line[:-1]
        else:
            line = line + " "
        # c += 1
        # if c == 1:
        #     print(line)
        #     i = "{{c|{{larger|" + line + "}}}}"
        #     l.append(i)
        # elif c == 3:
        #     print(line)
        #     i = "{{c|{{smaller|" + line + "}}}}"
        #     l.append(i)
        # elif c == 5:
        #     print(line)
        #     i = "{{di|" + line
        #     l.append(i)
        # elif c == 5:
        #     listline = list(line)
        #     listline.insert(1, "}}")
        #     listline = "".join(listline)
        #     i = "{{di|" + listline
        #     secondline.append(i)
        #     # l.append(i)
        # # ALL BELOW TO else IS FOR A WILD-GOOSE CHASE
        # elif c == 6:
        #     pass
        # elif c == 7:
        #     line = line.replace("1 ", "")
        #     line = line.replace("U ", "")
        #     line = line.replace("V ", "")
        #     secondline.append(line)
        #     i = " ".join(secondline)
        #     l.append(i)
        # else:
        # if not line.endswith("STELLA DALLAS"):
        l.append(line)

    x = "".join(l)

    # print(x)

    x = x.replace("‘“‘", "\"")
    x = x.replace("Go gle", "")
    x = x.replace("”", "\"")
    x = x.replace("“", "\"")
    x = x.replace("’", "'")
    x = x.replace("‘", "'")
    if poetry == False:
        x = x.replace("\n", " ")
        x = x.replace("\n\n\n\n", " ")
    x = x.replace("-  ", "")
    x = x.replace("- ", "")
    # x = x.replace("  ", "\n\n")
    x = x.replace("   ", "\n\n")
    x = x.replace("  ", " ")
    x = x.replace("™™", "™")
    x = x.replace(" bow!", " bowl")
    x = x.replace(" arc ", " are ")
    x = x.replace(" > ", " ")
    x = x.replace(" > ", " ")
    x = x.replace("''", "\"")
    x = x.replace("/ \n", ".\"")


    def italicize(item, x):
        # global x
        newitem = item.replace(f"''", "")
        x = x.replace(f"{item}", f"''{newitem}''")
        x = x.replace(f"''{item}''?", f"''{newitem}?''")
        x = x.replace(f"''{item}''!", f"''{newitem}!''")
        x = x.replace(f"''{item}''.", f"''{newitem}.''")
        x = x.replace(f"''{item}'',", f"''{newitem},''")
        x = x.replace(f"''{item}'';", f"''{newitem};''")
        x = x.replace(f"''{item}'':", f"''{newitem}:''")
        x = x.replace(f"''{item}'''s", f"''{newitem}'s''")
        x = x.replace(f"''{item},''\"", f"''{newitem},\"''")
        x = x.replace(f"''{item}.''\"", f"''{newitem}.\"''")
        x = x.replace(f"''{item}?''\"", f"''{newitem}?\"''")
        x = x.replace(f"''{item}!''\"", f"''{newitem}!\"''")
        x = x.replace(f"\"''{item}", f"''\"{newitem}")

    # IA-only

    x = x.replace("\n\nSTELLA DALLAS\n\n", "")
    x = x.replace("^", "'")
    x = x.replace(" \n", "\n")
    x = x.replace(".-", ".—")
    x = x.replace("'*", "\"")

    # Else
    x = x.replace("”", "\"")
    x = x.replace("“", "\"")
    x = x.replace("’", "'")
    x = x.replace("‘", "'")
    x = x.replace("ʻ", "'")
    x = x.replace("`", "'")
    x = x.replace(".\".", ".\"")
    x = x.replace(" .\n", "\n")
    # x = x.replace("\"\n\"", "\"\n\n\"")
    # x = x.replace(".\n\"", ".\n\n\"")
    if poetry == False:
        x = re.sub(r"(.)\n(.)", r"\1\n\n\2", x)
        x = re.sub(r"\n\n.\n\n", r" ", x)
        x = re.sub(r"\n\n..\n\n", r" ", x)
        x = re.sub(r"\n\n...\n\n", r" ", x)
        x = re.sub(r"\n\n....\n\n", r" ", x)
    x = re.sub(r"(.)\. ([a-z])", r"\1 \2", x)
    x = x.replace("\" \"", "\"\n\n\"")
    x = x.replace(" · ", "\n\n") #For A Wild-Goose Chase
    x = x.replace(" !", "!")
    x = x.replace(" :", ":")
    x = x.replace("\"!", "\"")
    x = x.replace("–", "—")
    x = x.replace(" — ", "—")
    x = x.replace(" —", "—")
    x = x.replace("— ", "—")
    x = x.replace(" --", "—")
    x = x.replace("-- ", "—")
    x = x.replace("--", "—")
    x = x.replace(" - ", "—")
    x = x.replace(" -", "—")
    x = x.replace("- ", "—")
    x = x.replace("-\"", "—\"")
    x = x.replace("—\".\n", "—\"\n")
    x = x.replace("-—", "—")
    x = x.replace("—-", "—")
    
    x = x.replace("'11", "'ll")
    x = x.replace("we 11", "we'll")
    x = x.replace("you 11", "we'll")
    x = x.replace(" ^11", "'ll")
    x = x.replace("^11", "'ll")
    x = x.replace("A11", "All")
    x = x.replace("* *", "\"")
    x = x.replace("**", "\"")
    x = x.replace(" *s", "'s")
    x = x.replace(" ^s", "'s")
    x = x.replace("^ *", "\"")
    x = x.replace("* ^", "\"")
    x = x.replace("'*", "\"")
    x = x.replace("' *", "\"")
    x = x.replace("* '", "\"")

    x = x.replace("*^", "\"")
    x = x.replace("*'", "\"")
    x = x.replace("^^", "\"")
    x = x.replace("^ ^", "\"")
    x = x.replace("^ '", "\"")
    x = x.replace("^'", "\"")
    x = x.replace("'^", "\"")
    x = x.replace("' ^", "\"")
    
    x = x.replace("0h", "Oh")
    x = x.replace("n*t", "n't")
    x = x.replace("n^t", "n't")
    x = x.replace("\"udge", "judge")

    

    # x = x.replace("*", "")
    x = x.replace("aesthetic", "æsthetic")
    x = x.replace("nästhetic", "næsthetic")
    x = x.replace("personae", "personæ")
    x = x.replace("anoeuv", "anœuv") #manoeuvre
    x = x.replace("ncyclopaedi", "ncyclopædi")
    x = x.replace(" anv ", " any ")
    x = x.replace(" vou ", " you ")
    x = x.replace(" vou.", " you.")
    x = x.replace("eacVi", "each")
    x = x.replace("'J", "\"")
    x = x.replace("iDg", "ing")
    x = x.replace("J'\n", "\"")

    dashes = [
    "all-restrictive",
    "arc-light",
    "awe-struck",
    "babel-town",
    "bathing-suit",
    "bell-button",
    "billiard-room",
    "broad-shouldered",
    "broad-spreading",
    "bunk-room",
    "bushy-haired",
    "business-like",
    "cartridge-belt",
    "chair-back",
    "city-bred",
    "clear-cut",
    "close-clipped",
    "cold-blooded",
    "co-oper",
    "counter-charge",
    "crimson-striped",
    "dagger-knife",
    "dark-skinned",
    "daughter-in",
    "deep-set",
    "dining-room",
    "distinguished-looking",
    "dressing-room",
    "eating-table",
    "efficient-corporated",
    "electric-light",
    "electro-magnet",
    "fan-shaped",
    "fire-fighter",
    "five-story",
    "flat-topped",
    "four-post",
    "frock-coat",
    "full-blooded",
    "gas-lamp",
    "get-rich", #for get-rich-quick
    "ood-bye", #g
    "ood-night", #g
    "gray-blue",
    "gray-green",
    "great-pulsating",
    "green-gray",
    "ground-glass",
    "gun-case",
    "half-blind",
    "half-clad",
    "half-past",
    "half-respectful",
    "half-serious",
    "half-suspicious",
    "half-year",
    "high-pitched",
    "house-wall",
    "hundred-year",
    "ice-box",
    "ice-covered",
    "ice-crusted",
    "ill-fated",
    "income-bearing",
    "in-law",
    # "match-box",
    "machine-driven"
    "man-controlled",
    "mess-room",
    "metal-patched",
    "mild-eyed",
    "morning-room",
    "morning-service",
    "mountain-climb",
    "narrow-skirted",
    "newel-post",
    "office-building",
    "one-cell",
    " one-fi",
    " one-fo",
    "one-story",
    "one-tenth",
    "one-twelfth",
    "one-twentieth",
    "open-mouthed",
    # "out-loud", # DON'T ADD THIS
    "paste-board",
    "pitch-dark",
    "plain-cloth",
    "plate-glass",
    "power-printing",
    "power-produc",
    "pre-eminent",
    "public-school",
    "racing-car",
    "re-building",
    "reception-room",
    "red-haired",
    "re-cross",
    "re-examin",
    "rich-quick", #for get-rich-quick
    "roly-poly",
    "round-faced",
    "sallow-skinned",
    "sauce-dish",
    "Schleswig-Holstein",
    "secret-service",
    "self-compounding",
    "self-confidence",
    "self-control",
    "self-defense",
    "self-possess",
    "semi-circle",
    "shooting-coat"
    "shooting-mate",
    "silver-mounted",
    "sitting-room",
    "six-inch",
    "sixty-o",
    "sixty-t",
    "sixty-f",
    "sixty-s"
    "sixty-e",
    "sixty-n",
    "smoking-jacket",
    "smoking-room",
    "so-called",
    "soft-nosed",
    " son-in"
    "spindle-legged",
    "stage-setting",
    "state-line",
    "steel-patched",
    "step-daughter",
    "stump-tailed",
    "summer-resort",
    "sun-bleached",
    "swimming-pool",
    "swimming-suit",
    "telegraph-pole",
    "ten-story"
    "tenth-story",
    "thousand-year",
    "toe-danc", #toe-dancing
    "traffic-laden",
    "tucked-away",
    "twenty-one",
    "twenty-dollar",
    "twenty-e",
    "twenty-f",
    "twenty-n",
    "twenty-s",
    "twenty-t",
    "two-cylinder"
    "two-story"
    "o-day", #t
    "o-morrow", #t
    "tongue-tied",
    "o-night", #t
    "trap-shoot",
    "trophy-room",
    "two-cent",
    "unknown-quality",
    "wagon-wheel",
    "waste-basket",
    "weasel-eyed",
    "weasel-faced",
    "wedding-ring",
    "well-advertised",
    "well-furnished",
    "well-known",
    "window-sill",
    "world-old",
    "white-draped",
    "white-faced",
    "white-haired",
    "white-robed",
    "writing-desk",
    "year-old",
    ]

    # tomorrow at 8
    # he files
    # billysm64

    for item in dashes:
        parseitem = item.split("-")
        parsed = "".join(parseitem)
        if parsed in x:
            x = x.replace(parsed, item)

    # dash THINGS

    x = x.replace(" | ", "")
    x = x.replace("| ", "")
    x = x.replace("»", "\"")
    x = x.replace("«", "\"")
    x = x.replace(",-", ",—")
    x = x.replace("_", "—")
    x = x.replace("á", "a")
    x = x.replace("а", "a")
    x = x.replace("å", "a")
    x = x.replace("é", "e")
    x = x.replace("í", "i")
    x = x.replace("Į", "I")
    x = x.replace("ģ", "g")
    x = x.replace("ø", "o")
    x = x.replace("ó", "o")
    x = x.replace("ş", "s")
    x = x.replace("ť", "t")
    x = x.replace("cafe ", "café ")
    x = x.replace(" coupe", " coupé")
    x = x.replace("coupe ", "coupé ")
    x = x.replace(" fiance", " fiancé")
    x = x.replace("fiance ", "fiancé ")
    x = x.replace("defiancé", "defiance")
    x = x.replace("debris", "débris")
    x = x.replace("debut", "début")
    x = x.replace("preempt", "preëmpt")
    # x = x.replace("coopera", "coöpera")
    x = x.replace(" regime.", " régime.")
    x = x.replace(" regime,", " régime,")
    x = x.replace(" regime ", " régime ")
    x = x.replace("reestablish", "reëstablish")
    x = x.replace("reenter", "reënter")
    x = x.replace("reenforc", "reënforc")
    x = x.replace("naive", "naïve")
    x = x.replace("naivite", "naïvité")
    x = x.replace("naïvite", "naïvité")
    x = x.replace(" seance", " séance")
    x = x.replace("cortege", "cortège")
    x = x.replace("Kleber", "Kléber") #Ruth of the USA
    x = x.replace("Solferino", "Solférino")
    x = x.replace("Geroud", "Géroud")
    x = x.replace("Recamier", "Récamier")
    x = x.replace(" role ", " rôle ")
    x = x.replace(" role.", " rôle.")
    x = x.replace(" role,", " rôle,")
    x = x.replace(" role:", " rôle:")
    x = x.replace(" role;", " rôle;")
    x = x.replace(" role–", " rôle–")
    x = x.replace(" role-", " rôle-")
    x = x.replace(" roles ", " rôles ")
    x = x.replace(" roles.", " rôles.")
    x = x.replace(" roles,", " rôles,")
    x = x.replace(" roles:", " rôles:")
    x = x.replace(" roles;", " rôles;")
    x = x.replace(" roles–", " rôles–")
    x = x.replace(" roles-", " rôles-")
    x = x.replace("Wurtemburg", "Würtemburg")
    x = x.replace("Armentiere", "Armentière")
    x = x.replace("on\"t", "on't")
    #Ruth of the USA
    x = x.replace("scholastiQ", "scholastic")
    x = x.replace("#", "")
    x = x.replace("\n ", "\n")
    x = x.replace(" n't", "n't")
    x = x.replace(" 've ", "'ve ")
    x = x.replace(" 'd ", "'d ")
    x = x.replace(" 's ", "'s ")
    x = x.replace(" 's.", "'s.")
    x = x.replace(" 's?", "'s?")
    x = x.replace(" 's,", "'s,")
    x = x.replace(" 's!", "'s!")
    x = x.replace(" 'm ", "'m ")
    x = x.replace(" 'll ", "'ll ")
    x = x.replace(" ll ", "'ll ")
    x = x.replace(" d ", "'d ")
    x = x.replace(" 're ", "'re ")
    x = x.replace("I ve ", "I've ")
    x = x.replace("hey ve ", "hey've ")
    x = x.replace("ou ve ", "ou've ")
    x = x.replace(" mav ", " may ")
    x = x.replace(" t ", "'t ")
    x = x.replace(" ' ", " '")
    x = x.replace("''", "\"") # IMPORTANT
    x = x.replace("\" '", "\"") # IMPORTANT
    # x = x.replace("/", "''I''")
    x = x.replace(" 1\n", "!")
    x = x.replace("1\"", "!\"")
    x = x.replace(" rn", " m")
    x = x.replace("(natter", "matter")
    x = x.replace("lii", "hi")
    x = x.replace(" 'I'll", "'ll")
    x = x.replace("jii", "hi")
    x = x.replace("tii", "th")
    x = x.replace("cii", "ch")
    x = x.replace("ortwo", "or two")
    x = x.replace("priee", "price")
    x = x.replace(" 'T", " T") # IN MOST CASES THIS IS WHAT YOU WANT
    x = x.replace("fii", "ffi")
    x = x.replace("nii", "mi")
    x = x.replace(" owii ", " own ")
    x = x.replace(" iiot ", " not ")
    x = x.replace(" iier ", " her ")
    x = x.replace("oiight", "ought")
    x = x.replace("eaveii", "eaven")
    x = x.replace(" iis ", " us ")
    x = x.replace("toiigue", "tongue")
    x = x.replace(" iis ", " us ")
    x = x.replace("heii", "hen")
    x = x.replace("iid", "nd")
    x = x.replace("iised", "used")
    x = x.replace("busjness", "business")
    x = x.replace("iien ", "hen ")
    x = x.replace(" fiill", " full")
    x = x.replace("iig ", "ing ")
    x = x.replace("biit", "but")
    x = x.replace("biit", "but")
    x = x.replace("iiere", "here")
    x = x.replace("qiiite", "quite")
    x = x.replace("stiii", "still")
    x = x.replace("beliind", "behind")
    x = x.replace("iit", "nt")
    x = x.replace("iin", "un")
    # x = x.replace("ii", "\"\"\"\"\"ii\"\"\"\"\"\"")

    x = x.replace("£", "'")
    # x = x.replace("''I'''", ",\"")
    # x = x.replace("''I''\n", ".\"\n\n")
    x = x.replace(",5", ",\"")
    x = x.replace(".5", ".\"")
    x = x.replace("°", "o")
    # REGEX STUFF
    x = re.sub("''I'' ([a-z])", r"""," \1""", x)
    x = re.sub("''I'' ([A-Z])", r"""." \1""", x)
    # x = re.sub("[[a-z]|[A-Z]] \. \. [[a-z]|[A-Z]]", r"""." \1""", x)
    # print(x)



    #clean up weird apostrophe-quote combinations
    # x = x.replace("\"' ", "\"'")
    x = x.replace(" '\"", "'\"")
    x = x.replace("\"'\" ", "\"'\"")
    x = x.replace(" \"'\"", "\"'\"")
    x = x.replace(" '\"'", "'\"'")
    x = x.replace("'\"' ", "'\"'")
    #convert to templates
    # x = x.replace("\"'\"", "{{\" ' \"}}")
    # x = x.replace("'\"'", "{{' \" '}}")
    x = x.replace("\"'", "{{\" '}}")
    x = x.replace("'\"", "{{' \"}}")
    # x = x.replace("\"'\"", "\"")
    # x = x.replace("'\"'", "\"")
    # x = x.replace("\"'", "\"")
    # x = x.replace("'\"", "\"")

    x = x.replace("\n\" ", "\n\"")
    x = x.replace(" \" ", " \"")
    x = x.replace(" \"said ", "\" said ")
    x = x.replace("—' ", "—'")
    x = x.replace("\n\n—", "—")
    x = x.replace(",—\" ", ",—\"")
    x = x.replace("\n\n'", "\n\n\"")
    x = x.replace(" \":", "\":")
    x = x.replace(" ?", "?")
    x = x.replace(" !", "!")
    x = x.replace(" .\"", ".\"")
    x = x.replace(" ,", ",")
    x = x.replace("? \" ", "?\" ")
    x = x.replace(", \" ", ",\" ")
    x = x.replace(". \" ", ".\" ")
    x = x.replace("! \" ", "!\" ")
    x = x.replace("? \"\n", "?\"\n")
    x = x.replace(". \"\n", ".\"\n")
    x = x.replace("! \"\n", "!\"\n")
    x = x.replace("!\".", "!\"")
    x = x.replace("?\".", "?\"")


    # A WILD-GOOSE CHASE
    # italicize("Aurora", x)
    # italicize("Cabot", x)
    # italicize("Gjoa", x)
    # italicize("Graphic", x)
    # italicize("Inca", x)
    # italicize("Kadiack", x)
    # italicize("Laeso", x)
    # italicize("Nares", x)
    # italicize("Viborg", x)

    italicize("kabluna", x)
    italicize("Kabluna", x)

    # THE ACHIEVEMENTS OF LUTHER TRANT
    # italicize("Covallo", x)
    # italicize("Elizabethan Age", x)
    # italicize("Gladstone", x)
    italicize("News", x)
    italicize("Lusitania", x)

    # THE INDIAN DRUM
    # italicize("Alabama", x)
    # italicize("Anna S. Solwerk", x)
    # italicize("Benton", x)
    # italicize("Chippewa", x)
    # italicize("Grant", x)
    # italicize("H. C. Richardson", x)
    # italicize("Martha Corvet", x)
    # italicize("Marvin Halch", x)
    # italicize("Miwaka", x)
    # italicize("Oscoda", x)
    # italicize("Pontiac", x)
    # italicize("Richardson", x)
    # italicize("Solwerk", x)
    # italicize("St. Ignace", x)
    # italicize("Ste. Marie", x)
    # italicize("Stoughton", x)
    # italicize("Susan Hart", x)
    # italicize("Wenota", x)
    # italicize("Winnebago", x)

    # Ruth of the U. S. A.
    # italicize("Adriatic", x)
    # italicize("Croix de Guerre", x)
    # italicize("gnädiges Fräulein", x)
    # italicize("Gothas", x)
    # italicize("Invincible", x)
    # italicize("liebchen", x)
    # italicize("Liebchen", x)
    # italicize("Marseillaise", x)
    # italicize("Medaille Militaire", x)
    # italicize("pension", x)
    # italicize("Ribot", x)
    # italicize("schloss", x)
    # italicize("Starke", x)
    # italicize("U. S. S. Starke", x)
    # italicize("Tuscania", x)


    # Resurrection Rock
    # italicize("manedos", x)
    # italicize("Gallantic", x)
    # italicize("Lampoon", x)
    # italicize("Nibanaba", x)
    # italicize("Rigoletto", x)

    # The Breath of Scandal
    italicize("Aquitania", x)

    # Keeban
    italicize("Hesperus", x)
    # italicize("Majestic", x)

    # Fidelia
    # italicize("I'll Show You", x)
    # x = x.replace("Bradford", "Brailford")


    x = x.replace("Fm", "I'm")
    x = x.replace("Fd", "I'd")
    x = x.replace("Pm", "I'm")
    x = x.replace(", 'Til ", ", \"I'll ")
    x = x.replace("Fll", "I'll")
    x = x.replace("T'm", "I'm")
    x = x.replace("T've", "I've")
    x = x.replace("T'll", "I'll")
    x = x.replace("Tt's", "It's")
    x = x.replace("\"T ", "\"I ")
    x = x.replace(" f\n", "\n")
    x = x.replace(" plano", " piano")
    x = x.replace(" ail ", " all ")
    x = x.replace(" |", "")
    x = x.replace(" T ", " I ")
    x = x.replace("['ll", "I'll")
    x = x.replace("\"Vou ", "\"You ")
    x = x.replace("\"Vour ", "\"Your ")
    x = x.replace("\"Vou're ", "\"You're ")
    x = x.replace("\"Vou'll ", "\"You'll ")
    x = x.replace("9o ", "So ")
    x = x.replace("cne", "one")
    x = x.replace("1s", "is")
    x = x.replace(" cf", " of")
    x = x.replace("\"Ves,", "\"Yes,")
    x = x.replace("Ves,", "\"Yes,")
    x = x.replace("Tl ", "I'll ")
    x = x.replace("Il ", "I'll ")
    x = x.replace("Ill ", "I'll ")
    x = x.replace(" Jaw", " law")
    x = x.replace("Jaw ", "law ")
    x = x.replace("actuaily", "actually")
    x = x.replace("\"ll ", "\"I'll ")
    x = x.replace("Tf ", "If ")
    x = x.replace("\"TI ", "\"I ")
    x = x.replace("NIy", "My")
    x = x.replace("Tt", "It")
    x = x.replace("Youre", "You're")
    x = x.replace("lie asked", "he asked")
    x = x.replace("Ves.", "\"Yes.")
    x = x.replace("\"Vl ", "\"I'll ")
    x = x.replace(" teld ", " told ")
    x = x.replace("ouw're", "ou're")
    x = x.replace("ow re ", "ou're ")
    x = x.replace("'rea ", "'re a ")
    x = x.replace(" [ ", " I ")
    x = x.replace(" ] ", " I ")
    x = x.replace("\"TY ", "\"I ")
    x = x.replace("\"IT ", "\"I ")
    x = x.replace("\"Yes,\"\n\n", "\"Yes.\"\n\n")
    x = x.replace("theyll", "they'll")
    x = x.replace("\"Whate\"", "\"What?\"")
    x = x.replace("''", "\"")
    x = x.replace("\"fam ", "\"I am ")
    x = x.replace(" wp ", " up ")
    x = x.replace(" wita ", " with ")
    x = x.replace("Iam ", "I am ")
    x = x.replace("\"T ", "\"I ")
    x = x.replace(" todo", " to do")
    x = x.replace("\"NO.\"", "\"No.\"")
    x = x.replace("{{\" '}}\n\n", "\"\n\n")
    x = x.replace("\"J?\"", "\"I?\"")
    x = x.replace("..", ".")
    x = x.replace("Pll", "I'll")
    x = x.replace("IT'l", "I'll")
    x = x.replace("youll", "you'll")
    x = x.replace("Youll", "You'll")
    x = x.replace("whoe\"", "who?\"")
    x = x.replace("thate\"", "that?\"")
    x = x.replace("Id ", "I'd ")
    x = x.replace(" J ", " I ")
    x = x.replace(" T ", " I ")
    x = x.replace(" your\"", " you?\"")
    x = x.replace(" ke ", " he ")
    x = x.replace("hey'il ", "hey'll ")
    x = x.replace("Y'm", "I'm")
    x = x.replace(" Jast ", " last ")
    x = x.replace("hatis ", "hat is ")
    x = x.replace("JI ", "I ")
    x = x.replace("JT ", "I ")
    x = x.replace("YT ", "I ")
    x = x.replace(" ing ", "ing ")
    x = x.replace("~ ", "")
    x = x.replace("\"Ts ", "\"Is ")
    x = x.replace("T'd", "I'd")
    x = x.replace("1'm", "I'm")
    x = x.replace("Tm ", "I'm ")
    x = x.replace("Ym ", "I'm ")
    x = x.replace("Tll ", "I'll ")
    x = x.replace("Dll ", "I'll ")
    x = x.replace("iF", "f")
    x = x.replace("efifort", "effort")
    x = x.replace(" fuil", " full")
    x = x.replace("\"f ", "\"I ")
    x = x.replace("P\"\n\n", "?\"\n\n")
    x = x.replace("youcan", "you can")
    x = x.replace("\"T? ", "\"I? ")
    x = x.replace("Y've ", "I've ")
    x = x.replace("fT ", "I ")
    x = x.replace("Vou'd ", "You'd ")
    x = x.replace("Vou're ", "You're ")
    x = x.replace(" youe\"", " you?\"")
    x = x.replace("J'm ", "I'm ")
    x = x.replace("J'll ", "I'll ")
    x = x.replace("J'd ", "I'd ")
    x = x.replace("J've ", "I've ")
    x = x.replace("&c ", "&c. ")
    x = x.replace("Cliristian", "Christian")
    x = x.replace("aflect", "affect")
    x = x.replace("wliich", "which")
    x = x.replace("3I", "M")
    x = x.replace("httle", "little")
    x = x.replace(" comer", " corner")
    x = x.replace(" bom ", " bom ")
    x = x.replace(" bom,", " bom,")
    x = x.replace(" bom.", " bom.")
    x = x.replace(" lier ", " her ")
    x = x.replace(" liis ", " his ")
    x = x.replace(" nou'", " now ")
    x = x.replace(" bis ", " his ")
    x = x.replace(" ot ", " of ")
    x = x.replace(" aea ", " aea ")
    x = x.replace(" wiord", " word")
    x = x.replace(" wiord ", " word ")
    x = x.replace(", Who", ", who")
    x = x.replace("Pate ", "Fate ")
    x = x.replace(" emigre ", " emigré ")
    x = x.replace(" emigres ", " emigrés ")
    x = x.replace("(e g.", "(e. g.")
    x = x.replace(" e g.", " e. g.")
    x = x.replace("Pie ", "He ")
    x = x.replace(", u ", ", \"")
    x = x.replace(" dubhed ", " dubbed ")
    x = x.replace("wcrth", "worth")
    x = x.replace(" hy ", " by ")
    x = x.replace(" bv ", " by ")
    x = x.replace(" s ", "'s ")
    x = x.replace("I m ", "I'm ")
    x = x.replace("per cent, ", "per cent. ")
    x = x.replace(" Fie ", " He ")
    x = x.replace(" tlie ", " the ")
    x = x.replace("Tli", "Th")
    x = x.replace("tli ", "th ")
    x = x.replace("tliat", "that")
    x = x.replace(" bum ", " burn ")
    x = x.replace("buming", "burning")
    x = x.replace("bumed", "burned")
    x = x.replace("bumt", "burnt")
    x = x.replace("sli ", "sh ")
    x = x.replace(" tli", " th")
    x = x.replace("Slie ", "She ")
    x = x.replace("Slie ", "She ")
    x = x.replace(" slie ", " she ")
    x = x.replace("\ntlie ", "\nthe ")
    x = x.replace("\ntliis ", "\nthis ")
    x = x.replace(" tji", " th")
    x = x.replace("atlier", "ather")
    x = x.replace("lF", "f")
    x = x.replace("h'im", "him")
    x = x.replace("Ji", "h")
    x = x.replace("youtli", "youth")
    x = x.replace("soutli", "south")
    x = x.replace("witli", "with")
    x = x.replace(" tho ", " the ")
    x = x.replace("entliusi", "enthusi")
    x = x.replace("togetlier", "together")
    x = x.replace("patli", "path")
    x = x.replace("otlier", "other")
    x = x.replace("nortli", "north")
    x = x.replace("whetlier", "whether")
    x = x.replace(" largo ", " large ")
    x = x.replace("30 that", "so that")
    x = x.replace(" sh$ ", " she ")
    x = x.replace(" wa$ ", " was ")
    x = x.replace("CF", "ff")
    x = x.replace("jB", "f")
    x = x.replace("fiuence", "fluence")
    x = x.replace("ouJd", "ould")
    x = x.replace("&", "s")
    x = x.replace(" s ", " & ")
    x = x.replace(" wo ", " we ")
    x = x.replace("1 think", "I think")
    x = x.replace(" 1 wh", "! wh")
    x = x.replace("Oh 1", "Oh!")
    x = x.replace("nd 1 ", "nd I ")
    x = x.replace("1 sh", "I sh")
    x = x.replace("1 would", "I would")
    x = x.replace("\"K ", "\"If ")
    x = x.replace(" 60 ", " so ")
    x = x.replace("1 c", "I c")
    x = x.replace("mg ", "ng ")
    x = x.replace("mg,", "ng,")
    x = x.replace("mg.", "ng.")
    x = x.replace("mg;", "ng;")
    x = x.replace("mg:", "ng:")
    x = x.replace("mg-", "ng-")
    x = x.replace("mg—", "ng—")
    x = x.replace("flf", "ff")
    x = x.replace(" m ", " in ")
    x = x.replace("afiect", "affect")
    x = x.replace(" liad ", " had ")
    x = x.replace("spumed", "spurned")
    x = x.replace(" bo ", " be ")
    x = x.replace(" theni", " them")
    x = x.replace("liarvest", "harvest")
    x = x.replace("1y ", "ly ")
    x = x.replace("h6r", "her")
    x = x.replace(" 's", "'s")
    x = x.replace(" 't", "'t")
    x = x.replace("Wliat", "What")
    x = x.replace("Uke ", "like ")
    x = x.replace("Uttle", "little")
    x = x.replace("\"Ves;", "\"Yes;")
    x = x.replace("\"Gh,", "\"Oh;")
    x = x.replace("tothem", "to them")
    x = x.replace("Ee", "Re")
    x = re.sub(r"([a-z]) The", r"\1\. The", x)
    x = re.sub(r"([a-z]) That", r"\1\. That", x)
    x = re.sub(r"([a-z]) This", r"\1\. This", x)
    x = re.sub(r"([a-z]) But ", r"\1\. But ", x)
    x = re.sub(r"([a-z]) So ", r"\1\. So ", x)
    x = re.sub(r"([a-z]) So,", r"\1\. So,", x)
    x = re.sub(r"([a-z]) Why", r"\1\. Why", x)
    x = re.sub(r"([a-z]) What", r"\1\. What", x)
    x = re.sub(r"([a-z][a-z])I", r"\1 I", x)
    x = x.replace("/'", ".\"")
    x = x.replace("AU ", "All ")
    x = x.replace(" I\"", "!\"")
    x = x.replace(" I I", "! I")
    x = x.replace(" r\"", "?\"")
    x = x.replace(" caU", " call")
    x = x.replace("bnt ", "but ")
    x = x.replace("yonng", "young")





    # x = x.replace(", a ", ", \"")

    # " " ... cried. " "
    # " " ... said. " "
    # " " ... declared. " "
    # " " ... commended. " "

    x = x.replace(" § ", "")
    x = x.replace("S.O.S.", "S. O. S.")
    x = x.replace(" .. ", " . . . ")
    x = x.replace(" ... ", " . . . ")
    x = x.replace("....", ". . . .")
    x = x.replace("...\"", " . . .\"")

    # WAYLAID BY WIRELESS
    # italicize("Britannia", x)
    # italicize("Hibernia", x)
    italicize("Mayflower", x)
    italicize("Morning ''News", x)
    # italicize("Bahia", x)
    # italicize("Salvadore", x)
    # italicize("St. Petersburg", x)
    # italicize("alibi", x)
    # italicize("alibis", x)
    # italicize("entente", x)
    # italicize("ennui", x)
    # italicize("bona fide", x)
    # x = x.replace("Thome", "Thorne")

    # LUTHER TRANT
    # x = x.replace("lectroplat", "lectro-plat")
    x = x.replace("\n[ocr errors]", "")
    x = x.replace(" [ocr errors]", "")
    x = x.replace("[ocr errors]", "")
    x = x.replace("\n[merged small]", "")
    x = x.replace(" [merged small]", "")
    x = x.replace("[merged small]", "")
    x = x.replace("\n[graphic]", "")
    x = x.replace(" [graphic]", "")
    x = x.replace("[graphic]", "")
    x = x.replace("\n[subsumed]", "")
    x = x.replace(" [subsumed]", "")
    x = x.replace("[subsumed]", "")
    x = x.replace("■", "")
    x = x.replace("\n[blocks in formation]", "")
    x = x.replace(" [blocks in formation]", "")
    x = x.replace("[blocks in formation]", "")
    x = x.replace("P. S.", "P.S.")
    x = x.replace("Co ", "Co. ")
    x = x.replace("Mr ", "Mr. ")
    x = x.replace("Mr, ", "Mr. ")
    x = x.replace("Mrs ", "Mrs. ")
    x = x.replace("Mrs, ", "Mrs. ")
    x = x.replace("stilling", "stifling")
    x = x.replace("•", "")
    x = x.replace("\n\n\n", "\n\n")
    x = x.replace("\n\n\n", "\n\n")
    x = x.replace("  ", " ")
    x = x.replace(" ;", ";")
    # print("Well, I got here")
    x = x.replace("THE END", "\n{{c|{{smaller|THE END}}}}")
    x = x.replace("— ", "—")
    x = x.replace("A.M.", "{{sc|a.m.}}")
    x = x.replace("P.M.", "{{sc|p.m.}}")
    x = x.replace("A. M.", "{{sc|a. m.}}")
    x = x.replace("P. M.", "{{sc|p. m.}}")
    x = x.replace("rlv", "rly")
    x = x.replace("lv ", "ly ")
    x = x.replace("cornin", "comin")
    x = x.replace("Cornin", "Comin")
    x = x.replace("Phoebe", "Phœbe")
    x = x.replace("Phcebe", "Phœbe")
    x = x.replace("' 7", "\"")
    x = x.replace(", 77", ",\"")
    x = x.replace(" 7 s ", "'s ")
    x = x.replace("hae", "hæ")
    x = x.replace(" hæ ", " hae ")
    x = x.replace("Michæl", "Michael")
    x = x.replace("Dobeln", "Döbeln")
    x = x.replace("Putz", "Pütz")
    x = x.replace("cnly", "only")
    x = x.replace(" c0me ", " come ")
    x = x.replace("atioii", "ation")
    x = x.replace(" pMn", " pain")
    # x = x.replace(" * ", " ")

    italicize("The Masses", x)
    italicize("Novoye Vremya", x)

    def ireplace(input, x):
        # global x
        x = x.replace(f" I{input} ", f" i{input} ")
        x = x.replace(f" I{input},", f" i{input},")
        x = x.replace(f" I{input}.", f" i{input}.")
        x = x.replace(f". i{input} ", f". I{input} ")
        x = x.replace(f"! i{input} ", f"! I{input} ")
        x = x.replace(f"? i{input} ", f"? I{input} ")
        x = x.replace(f"\" i{input} ", f"\" I{input} ")
        x = x.replace(f",\" I{input} ", f",\" i{input} ")

    ireplace("f", x)
    ireplace("mportance", x)
    ireplace("mportant", x)
    ireplace("mpression", x)
    ireplace("n", x)
    ireplace("ndent", x)
    ireplace("ndentation", x)
    ireplace("ndentations", x)
    ireplace("ndented", x)
    ireplace("ndenting", x)
    ireplace("ndents", x)
    ireplace("nexperienced", x)
    ireplace("nnocence", x)
    ireplace("nnocent", x)
    ireplace("nnocently", x)
    ireplace("nside", x)
    ireplace("nsist", x)
    ireplace("nsisted", x)
    ireplace("nsistent", x)
    ireplace("nsisting", x)
    ireplace("nsists", x)
    ireplace("nstead", x)
    ireplace("nto", x)
    ireplace("ntend", x)
    ireplace("ntention", x)
    ireplace("ntentional", x)
    ireplace("nterested", x)
    ireplace("nvestigate", x)
    ireplace("nvestigated", x)
    ireplace("nvestigates", x)
    ireplace("nvestigating", x)
    ireplace("nvestigation", x)
    ireplace("nvitation", x)
    ireplace("nvite", x)
    ireplace("nvited", x)
    ireplace("nvites", x)
    ireplace("nviting", x)
    ireplace("nvoluntarily", x)
    ireplace("s", x)
    ireplace("ssue", x)
    ireplace("ssued", x)
    ireplace("ssues", x)
    ireplace("ssuing", x)
    ireplace("t", x)
    ireplace("ts", x)

    x = x.replace(". Laurel", ", Laurel")
    x = x.replace(" Ve ", "'ve ")
    x = x.replace("\\", "")

    x = x.replace("-a ", "—a ")
    x = x.replace("-and ", "—and ")
    x = x.replace("-he ", "—he ")
    x = x.replace("-he'", "—he'")
    x = x.replace("-her ", "—her ")
    x = x.replace("-herself", "—herself")
    x = x.replace("-him", "—him")
    x = x.replace("-me?", "—me?")
    x = x.replace("-me!", "—me!")
    x = x.replace("-his ", "—his ")
    x = x.replace("-we ", "—we ")
    x = x.replace("-was ", "—was ")
    x = x.replace("-but ", "—but ")
    x = x.replace("-I'", "—I'")
    x = x.replace("-I ", "—I ")
    x = x.replace("-of ", "—of ")
    x = x.replace("-or ", "—or ")
    x = x.replace("-she ", "—she ")
    x = x.replace("-that", "—that")
    x = x.replace("-the ", "—the ")
    x = x.replace("-they ", "—they ")
    x = x.replace("-them", "—them")
    x = x.replace("-their", "—their")
    x = x.replace("-just ", "—just ")
    x = x.replace("-you", "—you")
    x = x.replace("-may", "—may")
    x = x.replace(" me-", " me—")
    x = x.replace("-Mr", "—Mr")
    x = x.replace("-after ", "—after ")
    x = x.replace("-can't", "can't")
    x = x.replace("-can ", "can ")
    x = x.replace("O. K ", "O. K. ")
    x = x.replace("$lipuld", "should")
    x = x.replace(" i'orld", " world")

    x = x.replace(" thc ", " the ")
    x = x.replace(" tne ", " the ")

    x = x.replace("\"\"", "\"")
    x = x.replace(",,", ",")
    x = x.replace("\n ", "\n")
    x = x.replace("66 ", "\"")
    x = x.replace("\n6 ", "\n\"")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("  ", " ")
    x = x.replace("\n ", "\n")
    x = x.replace(",\n", ".\n")
    x = x.replace("\n\n. ", "\n\n")
    x = x.replace("{{' \"}}\"", "\"")
    x = x.replace("{{' \"}}{{\" '}}", "\"")
    x = x.replace("{{' \"'}}", "\" ")
    x = x.replace("\n\n{{' \"}}", "\n\n\"")
    x = x.replace("\"'", "{{\" '}}")
    x = x.replace("{{\" '}}", "\"")
    x = x.replace("{{' \"}}", "\"")



    x = x.replace("\"* ", "\"")
    x = x.replace("\"*", "\"")
    x = x.replace("*\"", "\"")
    x = x.replace("\n\" ", "\n\"")
    x = x.replace("1''I''2", "½")
    x = x.replace("1''I''4", "¼")
    x = x.replace(" 'also  ", " also ")
    x = x.replace(" i ", " ")
    x = x.replace(" C ", " ")
    x = x.replace("hmmy", "Jimmy")
    x = x.replace("hmmie", "Jimmie")
    x = x.replace(" hm ", " Jim ")
    x = x.replace(" hm.", " Jim.")
    x = x.replace(" hm,", " Jim,")
    x = x.replace(" '\n", "'\n")
    x = x.replace(" 'said", "\" said")
    x = x.replace(" \"said", "\" said")
    x = x.replace("\"1 ", "\"I ")
    x = x.replace("1 do ", "I do ")
    x = x.replace(" 'I asked", "\" I asked")
    x = x.replace(" 'I said", "\" I said")
    x = x.replace(" 'I cried", "\" I cried")
    x = x.replace(" 'he asked", "\" he asked")
    x = x.replace(" 'he said", "\" he said")
    x = x.replace(" 'he cried", "\" he cried")
    x = x.replace(" 'asked", "\" asked")
    x = x.replace(" 'said", "\" said")
    x = x.replace(" 'growled", "\" growled")
    x = x.replace(" 'moaned", "\" moaned")
    x = x.replace(" 'cried", "\" cried")
    x = x.replace(" \"I asked", "\" I asked")
    x = x.replace(" \"I said", "\" I said")
    x = x.replace(" \"I cried", "\" I cried")
    x = x.replace(" \"he ", "\" he ")
    x = x.replace(" \"she ", "\" she ")
    x = x.replace(" \"asked", "\" asked")
    x = x.replace(" \"said", "\" said")
    x = x.replace(" \"growled", "\" growled")
    x = x.replace(" \"moaned", "\" moaned")
    x = x.replace(" \"cried", "\" cried")
    x = x.replace(", \"he ", ",\" he ")
    x = x.replace(", \"she ", ",\" she ")
    # x = x.replace(", \"I ", ",\" he ")
    x = x.replace(", 'he ", ",\" he ")
    x = x.replace(", 'she ", ",\" she ")
    x = x.replace(" I I ", "! I ")
    x = re.sub(r" I ([A-Z])", r"! \1", x)
    x = re.sub(r"\"(\S+?) \"", r"\"\1\" ", x)
    x = x.replace("\\", "")
    x = x.replace("vllle", "ville")
    x = x.replace("¬ ", "")
    x = x.replace("¬", "")
    x = x.replace(" lias ", " has ")
    x = x.replace("Avere ", "were ")
    x = x.replace("Avith ", "with ")
    x = x.replace(", hut ", ", but ")
    x = x.replace("; hut ", "; but ")
    x = x.replace(" bnt ", " but ")
    x = x.replace("lIy", "lly")
    x = x.replace("/*\n\n", ".\"\n\n")
    x = x.replace("/* ", ",\" ")
    x = x.replace("Mr*", "Mr.")
    x = x.replace("Mrs*", "Mrs.")
    x = x.replace(" j \"", ", \"")
    x = x.replace("dj \"", "d, \"")
    x = x.replace("\"hm", "\"Jim")
    x = x.replace(" hm", " Jim")
    x = x.replace("\nhm", "\nJim")
    x = x.replace("\"hm", "\"Jim")
    x = x.replace(" bom ", " born ")
    x = x.replace(" yon ", " you ")
    x = x.replace("Hke", "like")
    x = x.replace("\"0", "\"O")
    x = re.sub(r"\.\" ([a-z])", r",\" \1", x) #MAKE MORE SPECIFIC CHANGES THAN THIS PLEASE
    x = re.sub(r"([a-z])\*s", r"\1's", x)
    x = re.sub(r"([a-z])\*d", r"\1'd", x)
    x = x.replace("\\", "")
    x = x.replace("*ve", "'ve")
    x = x.replace("Vm", "I'm")
    x = x.replace("I*m", "I'm")
    x = x.replace(" f\"", "?\"")
    x = x.replace(" f*", "?\"")
    x = x.replace("Fve", "I've")
    x = x.replace("Tve", "I've")
    x = x.replace(" I\n\n", "!\n\n")
    x = x.replace(",\"\n\n", ".\"\n\n")
    x = x.replace(", lie was ", ", he was ")
    x = x.replace(", lie is ", ", he is ")
    x = x.replace("gentie ", "gentle ")




    x = x.replace("Avas ", "was")
    x = x.replace("Avater", "water")
    x = x.replace(" coining ", " coming ")
    x = x.replace("\" '", "\"")
    x = x.replace("\n\" ", "\n\"")
    x = replace_bad_quote_spaces(x)
    x = x.replace(" @ ", " a ")
    x = x.replace("Korth", "North")
    x = x.replace("Eiv", "Riv") # River
    x = x.replace("Biv", "Riv") # River
    x = x.replace("Buth", "Ruth") # River
    x = x.replace("Eic", "Ric") # Richard
    x = x.replace("Bep", "Rep") # Republican, Representative
    x = x.replace(" abont", " about")
    x = x.replace(" nse", " use")
    x = x.replace("I)", "p")
    x = x.replace("Osbom", "Osborn")
    x = x.replace("Eob", "Rob") #Robinson
    x = x.replace("Yirgin", "Virgin") #Virginia
    x = x.replace(" tbe ", " the ")
    x = x.replace(" lie said", " he said")
    x = x.replace(" aud ", " and ")
    x = x.replace(" bom;", " born;")
    x = x.replace(" Jet ", " let ")
    x = x.replace("\n\n\"u", "\n\n\"Ju")
    x = x.replace(" ona ", " on a ")
    x = x.replace(" ina ", " in a ")
    x = x.replace("Ina ", "In a ")
    x = x.replace(" ata ", " at a ")
    x = x.replace("Iam", "I am")
    x = x.replace(" inthe ", " in the ")
    x = x.replace("Whata ", "What a ")
    x = x.replace("whata ", "what a ")
    x = x.replace(" fora ", " for a ")
    x = x.replace("Ido", "I do")
    x = re.sub(r"([a-z])\.\"([A-Z])", r"\1. \"\2", x)
    x = x.replace("\\", "")
    x = x.replace(",\" asked ", "?\" asked ")
    x = x.replace(",\" he asked", "?\" he asked")
    x = x.replace(",\" she asked", "?\" she asked")
    x = x.replace(", he said", ",\" he said")
    x = x.replace(", she said", ",\" she said")
    x = x.replace(" —", " ")
    x = x.replace(", The", ". The")
    x = x.replace(", But ", ". But ")
    x = x.replace(", And", ". And")
    x = x.replace(", He's", ". He's")
    x = x.replace(", He ", ". He ")
    x = x.replace(", She ", ". She ")
    x = x.replace(", She's", ". She's")
    x = x.replace(", Tha", ". Tha")
    x = x.replace(", Not", ". Not")
    x = x.replace(", Are", ". Are")
    x = x.replace(", Is ", ". Is ")
    x = x.replace(", Isn't", ". Isn't")
    x = x.replace(" hin ", " him ")
    x = x.replace("Asit ", "As it ")
    x = x.replace(" hin, ", " him, ")
    x = x.replace("\"Yd ", "\"I'd ")
    x = x.replace("tete-a-tete", "tête-à-tête")
    x = x.replace("negligee", "negligée")
    x = x.replace("matinee", "matinée")
    x = x.replace("?' ", "?\" ")
    x = x.replace("?'\n\n", "?\"\n\n")
    x = x.replace("?\".", "?\"")
    x = x.replace("\"?", "\"")
    x = x.replace("said. '", "said. \"")
    x = x.replace(" 'To ", " To ")
    x = x.replace("said, '", "said, \"")
    x = x.replace("' he said", "\" he said")
    x = x.replace("' she said", "\" she said")
    x = x.replace("\"Gh!", "\"Oh!")
    x = x.replace("\"Gh,", "\"Oh,")
    x = x.replace("\"Gh—", "\"Oh—")
    x = x.replace(" )\n", ")\n")
    x = x.replace("['m", "I'm")

    x = x.replace("T\"m", "I'm")
    x = x.replace("TI'", "I'")
    x = x.replace("—TI ", "—I ")
    x = x.replace("TIT", "I")
    x = x.replace("TIT ", "I ")
    x = x.replace("TIT ", "I ")
    x = x.replace("\"T ", "\"I ")
    x = x.replace("Tn ", "In ")


    
    x = x.replace("\"T\"I", "\"I")
    x = x.replace(" V'", " I'")
    x = x.replace(" Vl ", " I'll ")
    x = x.replace("Pd ", "I'd ")
    x = x.replace("P've ", "I've ")
    x = x.replace("Im ", "I'm ")
    x = x.replace("Dve ", "I've ")
    x = x.replace(" Yon ", " You ")
    x = x.replace(" yon ", " you ")
    x = x.replace("l]", "ll")
    x = x.replace("[ll", "I'll")
    x = x.replace(" agam.", " again.")
    x = x.replace(" agam ", " again ")
    x = x.replace(" upin ", " up in ")
    x = x.replace(" tle ", " the ")
    x = x.replace("youre", "you're")
    x = x.replace("I?m", "I'm")
    x = x.replace("OQ ", "O ")
    x = x.replace("VYou ", "You ")
    x = x.replace("'Th", "Th")
    x = x.replace(" hada ", " had a ")
    x = x.replace(" wasa ", " was a ")
    x = x.replace(" himin ", " him in ")
    x = x.replace("hecried", "he cried")
    x = x.replace("facade", "façade")
    x = x.replace("Facade", "Façade")
    x = x.replace(" moire ", " moiré ")
    x = x.replace(" esthetic", " æsthetic")
    x = x.replace(" gota ", " got a ")
    x = x.replace(" isit ", " is it ")
    x = x.replace(" itis ", " it is ")
    x = x.replace(" itis ", " it is ")
    x = x.replace(" isso ", " is so ")
    x = x.replace(" isa ", " is a ")
    x = x.replace(" tocome ", " to come ")
    x = x.replace(" Icried", " I cried")
    x = x.replace(" Iused", " I used")
    x = x.replace(" Inever", " I never")
    x = x.replace(" tohim", " to him")
    x = x.replace(" tosee ", " to see ")
    x = x.replace("toa ", "to a ")
    x = x.replace("QO", "O")
    x = x.replace("wentinto", "went into")
    x = x.replace(" wehave", " we have")
    x = x.replace("youthink", "you think")
    x = x.replace(" rele ", " rôle ")
    x = x.replace(" rdle ", " rôle ")
    x = x.replace(",'?", ",\"")
    x = x.replace("!'?", "!\"")
    x = x.replace("Wehave", "We have")
    x = x.replace("Hewas", "He was")
    x = x.replace("Wesaw", "We saw")
    x = x.replace("Wasit", "Was it")
    x = x.replace("wesaw", "we saw")
    x = x.replace("Hecan", "He can")
    x = x.replace(" bea ", " be a ")
    x = x.replace("Heis ", "He is ")
    x = x.replace("\"Ts", "\"Is")
    x = x.replace(" ali ", " all ")
    x = x.replace("hisown", "his own")
    x = x.replace(" doso.", " do so.")
    x = x.replace(" doso,", " do so,")
    x = x.replace(" doso ", " do so ")
    x = x.replace("Wedo", "We do")
    x = x.replace("sshe.", "s she.")
    x = x.replace("sshe ", "s she ")
    x = x.replace("sshe,", "s she,")
    x = x.replace(" nota ", " not a ")
    x = x.replace("Nota ", "Not a ")
    x = x.replace(" avery ", " a very ")
    x = x.replace("hereye", "her eye")
    x = x.replace(" wasin ", " was in ")
    x = x.replace("Iwas", "I was")
    x = x.replace(" isone ", " is one ")
    x = x.replace("Isaid", "I said")
    x = x.replace("Ithink", "I think")
    x = x.replace("lI ", "I ")
    x = x.replace("TI ", "I ")
    x = x.replace("\"TI", "\"I")
    x = x.replace(" \"\n", "\"\n")
    x = x.replace("TI'", "I'")
    x = re.sub(r"([a-z])'s([a-z])", r"\1's \2", x)
    x = re.sub(r"([a-z])shaped", r"\1-shaped", x)
    x = re.sub(r"([a-f h-z])uess ", r"\1ness", x)
    x = re.sub(r" well([a-z])", r" well-\1", x)
    x = re.sub(r" self([a-z])", r" self-\1", x)
    x = x.replace("self ish", "selfish")
    x = x.replace("sawit", "saw it")
    x = x.replace("thistime", "this time")
    x = x.replace("uess ", "ness ")
    x = x.replace("uess ", "ness ")
    x = x.replace(" itin ", " it in ")
    x = x.replace(" init ", " in it ")
    x = x.replace(" init.", " in it.")
    x = x.replace(" atthe ", " at the ")
    x = x.replace(" tothe ", " to the ")
    x = x.replace(" atthem", " at them")
    x = x.replace(" ofall", " of all")
    x = x.replace("fthe ", "f the ")
    x = x.replace(" rdle", " rôle")
    x = x.replace("Welike", "We like")
    x = x.replace(" donot", " do not")
    x = x.replace(" doit", " do it")
    x = x.replace(" doit", " do it")

    x = x.replace("forinstance", "for instance")
    x = x.replace("allthat", "all that")
    x = x.replace("IfI", "If I")
    x = x.replace("somehody", "somebody")
    x = x.replace(" havea ", " have a ")
    x = x.replace(" putin", " put in")
    x = x.replace(" ffom", " from")
    x = x.replace(" '1l", "'ll")
    x = x.replace("Tam ", "I am ")
    x = x.replace("JT", "I")
    x = x.replace("\"\"", "\"")
    x = x.replace(".\":", ".\"")
    x = x.replace(".'?", ".\"")
    x = x.replace(".\".\n", ".\"\n")




    dialogue_words = [
        "added",
        "advised",
        "agreed",
        "answered",
        "appended",
        "approved",
        "assented",
        "asserted",
        "began",
        "begged",
        "called",
        "concluded",
        "confided",
        "continued",
        "contributed",
        "cried",
        "declared",
        "demanded",
        "denied",
        "directed",
        "drawled",
        "echoed",
        "equivocated",
        "explained",
        "inquired",
        "interjected",
        "marveled",
        "murmured",
        "mused",
        "muttered",
        "observed",
        "persisted",
        "queried",
        "remarked",
        "reminded",
        "remonstrated",
        "repeated",
        "reported",
        "responded",
        "resumed",
        "retorted",
        "said",
        "sighed",
        "shrugged",
        "stated",
        "suggested",
        "teased",
        "thought",
        "told",
        "urged",
        "ventured",
        "wailed",
        "whispered",
    ]

    x = x.replace(" hke ", " like ")
    x = x.replace("\"ust ", "\"Just ")
    x = x.replace(" ery", " cry") # cry, crystal ©
    x = x.replace(" © ", " ")
    x = x.replace(" ©", "")
    x = x.replace(" )", ")")

    # "I am very drunk, said Johnny, adding politely, "And you?"
    # "I am very drunk," said Johnny, adding politely, "And you?"
    x = re.sub(r"\n\n(\".+?), said ", r"\n\n\1,\" said ", x)

    # dotdotdots fixed
    x = x.replace(", . . .", ". . . .")
    x = x.replace("..?", " . . . ?")
    x = x.replace("..\n", ". . . .\n")
    x = re.sub(r"([a-z])\. \.\n\n", r"\1\. \. \. \.\n\n", x)
    x = re.sub(r"([a-z])\. \. \.\n\n", r"\1\. \. \. \.\n\n", x)
    x = re.sub(r"([a-z]) \. \. ([a-z])", r"\1 \. \. \. \2", x)
    x = re.sub(r"([a-z])\.\. \. ", r"\1\. \. \. \. ", x)
    x = re.sub(r"([a-z])\.\. \. ", r"\1\. \. \. \. ", x)
    x = re.sub(r"([a-z])\.\. ", r"\1 \. \. \. ", x)
    x = re.sub(r" \.\.([a-z])", r" \. \. \. \1", x)
    x = re.sub(r"([a-z]) \. \.\n", r"\1 \. \. \.\n", x)


    x = re.sub(r"([a-zA-Z])\.([a-zA-Z])", r"\1 \2", x)
    x = re.sub(r"([a-zA-Z]):([a-zA-Z])", r"\1 \2", x)

    # Correct stuff like this:
    # When I said that, he said this: 'Love is love." And that was that.
    # When I said that, he said this: 'Love is love."\n\n
    # 'Love is love," said Jack. "And that was that."

    

    x = re.sub(r"Q([a-t])", r"G\1", x)
    x = x.replace(".;\n", ".\n")
    x = x.replace("?;\n", "?\n")
    x = x.replace("?:\n", "?\n")
    x = x.replace(".:\n", ".\n")
    x = x.replace("!.\n", "!\n")
    x = x.replace("?.", "?")



    # Q followed by any word that's not u > G.



    # pattern = "\n\n\"(.+?) \""
    # x = re.sub(r"\n\n\"(.+) \"", r"\1's", x)









    # x = x.replace(" . ", " . . . ")

    if poetry == True:
        x = x.replace("\n\n", "\n")
        x = x.replace("\n\n\n", "\n")
    
    x = x.replace(",\" asked", "?\" asked")
    x = x.replace(",\" inquired", "?\" inquired")
    x = x.replace(",\" exclaimed", "!\" exclaimed")

    if ",\" asked" in x:
        print_in_red("OH MY GOD WTF HAPPENED")
        exit()
    print_in_green("OCR has been corrected!")
    return x

## Clark only!

# italicize("Clark", x)
#
# x = x.replace(" v. ", "'' v. ''")

# pagename = "User:PseudoSkull/Waylaid for now"
# site = pywikibot.Site()
#
# page = pywikibot.Page(site, pagename)
# page.text = x
# print(f"{page.text} is what this is")
# # print(page.text)
# page.save("Dumping historical content into this page...")

# January 4, 2:10 PM

# December 27
# Rock Hill
# Columbia
#

# parsed_text = x

# parsed_text = parsed_text.replace("\n\n\n\n\n", "[/s/]")
# parsed_text = parsed_text.replace("\n\n\n\n", "[/s/]")
# parsed_text = parsed_text.replace("\n\n\n", "[/s/]")
# # sum(1 for c in message if c.isupper())
# parsed_text = parsed_text.split("[/s/]")

# for i in parsed_text:
#     if len(i) <= 150:
#         parsed_text.remove(i)
#         print(i)

# chapters_taken = []

# # for i in parsed_text:
# #     capital_vs_non = len(i[0]) - 5 < sum(1 for c in i if c.isupper())
# #     i = i.split("\n\n")
# #     new = []
# #     if len(i[0]) <= 50 and capital_vs_non == True:
# #         i.pop(0)
# #     i = "\n\n".join(i)
# #     chapters_taken.append(i)

# parsed_text = chapters_taken

# # print(parsed_text[21-5])

# # count = 4
# # annotated = []
# # for i in parsed_text:
# #     count += 1
# #     annotated.append(f"Page Number {count}:\n\n" + i + "\n\n----")

# # pagename = "User:PseudoSkull/Waylaid for now"
# # site = pywikibot.Site()

# # page = pywikibot.Page(site, pagename)
# # print(len(parsed_text))
# # page.text = "\n\n\n".join(parsed_text)
# # # page.text = "\n\n\n\n\n".join(annotated)
# # # print(f"{page.text} is what this is")
# # # print(page.text)
# # page.save("Dumping historical content into this page...")

# # cont = input("Continue on with the thing?")

# # page_num = 12
# # filename = "Orange Grove.djvu"
# # work = "Orange Grove"

# # lines = [
# #     "Talkin' 'bout my girl. My girl!",
# #     "Oo-oo-oo-ooh, Jackie Blue.",
# #     "I LOVE rock 'n' roll! Put another dime in the jukebox, baby.",
# #     "I want candy! I want candy!",
# #     "They call me mellow yellow.",
# #     "That's the way, uh-huh, uh-huh, I like it, uh-huh, uh-huh.",
# #     "Na na na na, na na na na, hey hey hey, good-bye.",
# #     "Top Cat! The most effectual! Top Cat! Who's intellectual!",
# # ]

# # for p in parsed_text:
# #     pagename = f"Page:{filename}/{page_num}"
# #     print(f"Doing {pagename}...")
# #     site = pywikibot.Site()

# #     page = pywikibot.Page(site, pagename)
# #     page.text = f"<noinclude><pagequality level=\"1\" user=\"PseudoSkull\" /></noinclude>{p}<noinclude></noinclude>"
# #     # page.text = "\n\n\n\n\n".join(annotated)
# #     # print(f"{page.text} is what this is")
# #     # print(page.text)
# #     time.sleep(50)
# #     page.save(f"{lines[random.randint(0, len(lines)-1)]}")
# #     page_num += 1

def replace_bad_quote_spaces(text):
    # Example of what this fixes:
    ## Bad: "Louder, Tommie, louder. "The voice swelled brave and loud.
    ## Fix: "Louder, Tommie, louder." The voice swelled brave and loud.
    pattern = r"\n\n\"(.+?)( \")"
    potential_bad_quote_spaces = re.findall(pattern, text)
    for match in potential_bad_quote_spaces:
        text_before_space_quote = match[0]
        if "\"" not in text_before_space_quote:
            # text = re.sub(pattern)
            text = text.replace(f"\n\n\"{text_before_space_quote} \"", f"\n\n\"{text_before_space_quote}\" ")
        # text = text.replace(i[0] + i[1], i[0] + "\"")
    return text