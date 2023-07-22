# WS_collection

from debug import print_in_green, print_in_red, print_in_yellow, print_in_blue, process_break
from hathi import get_hathitrust_images
from handle_projectfiles import assemble_pdf

folder = "hathi_images"
hathitrust_full_text_id = "hvd.32044080048069"

print(f"Attempting to download {hathitrust_full_text_id}...")

folder_path = get_hathitrust_images(hathitrust_full_text_id, folder)

assemble_pdf(folder_path)

print_in_green("Done!")