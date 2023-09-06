# WS_collection

{
    "title": "In the Tall Grass",
    "work_item": "Qxxxxxxxxxx",
    "version_item": "Qxxxxxxxxxx",
    "image": None, # If the story has a main image in it that is NOT a vignette or drop initial image or back cover, then add its filename here
    "wikisource_link": "The Grey Story Book/In the Tall Grass",
    "work_link": "In the Tall Grass",
    "status": "proofread", # If full work is proofread/validated, then just copy its status
}

"""
Proposed workflow:
* Create subwork_data.json, based on the above template
* Create work item and version item for each subwork, and as each is created, add the QIDs to subwork_data.json
** Create a new subwork_data.json for each new work THE INSTANT IT'S CREATED, and save file, just to ensure that the file exists
** If QID already exists for item, check that item accordingly

* (For now) Check all variants to see if their pages exist on Wikisource as disambiguation pages
** handle_disambig: If so, add to disambiguation page [["Tramp, Tramp, Tramp" (Yates)|"Tramp, Tramp, Tramp"]], a short story by [[Author:Katherine Merritte Yates|]]
** If not, create simple redirect
** Whichever is chosen for the redirect, add to subwork_data.json as "work_link"

* Create section "Individual short stories" on author page (handle_author.py)
** Rely on work_link for each entry
"""

"""
WORK ITEM SHOULD LOOK LIKE THIS

In the Tall Grass (Q122228186)
short story by Katherine Merritte Yates

instance of
literary work

title
In the Tall Grass (English)

form of creative work
short story

genre
children's fiction
Christian literature

has edition or translation
In the Tall Grass

author
Katherine Merritte Yates

country of origin
United States of America

language of work or name
English

publication date
1904
"""

"""
VERSION ITEM SHOULD LOOK LIKE THIS
In the Tall Grass (Q122228206)
1905 edition of work by Katherine Merritte Yates

instance of
version, edition, or translation

title
In the Tall Grass (English)

edition or translation of
In the Tall Grass

author
Katherine Merritte Yates

language of work or name
English

publication date
1905

published in (P1433)
The Grey Story Book (version of collection)

Wikisource (1 entry)
en	The Grey Story Book/In the Tall Grass (proofread badge)
"""