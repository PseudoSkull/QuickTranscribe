# WS_collection

import os
import requests
from handle_web_downloads import download_file
from bs4 import BeautifulSoup

def download_gutenberg_directory(directory_url, base_folder, new_folder=None):
    response = requests.get(directory_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Create a local directory to save the files
    # directory_name = os.path.basename(os.path.normpath(directory_url))
    if new_folder:
        new_folder_path = os.path.join(base_folder, new_folder)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        base_folder += f"/{new_folder}"

    # Download each file in the directory
    for row in soup.find_all("tr")[2:]:  # Skip the first row containing table headers
        columns = row.find_all("td")
        if not columns:
            break
        file_type = columns[0].img["alt"]
        file_name = columns[1].a["href"]

        if "/files/" in file_name:
            continue

        file_url = f"{directory_url}/{file_name}"

        # If the file is a directory, recursively download files from that directory
        if file_type == "[DIR]":
            folder_name = file_name
            download_gutenberg_directory(file_url, base_folder, new_folder=folder_name)
        # Generate the file URL and download it
        else:
            download_file(file_url, base_folder, file_name)

"""<tbody><tr>
<th></th>
<th>Format <span>
<a href="/help/bibliographic_record.html#Format" title="Explain Format."><span class="icon icon_help noprint"></span></a>
</span></th>
<th class="noscreen">Url</th>
<th class="right">Size</th>
<th class="noprint"><span>
<a href="/help/bibliographic_record.html#Dropbox" title="Explain Dropbox."><span class="icon icon_help noprint"></span></a>
</span></th>
<th class="noprint"><span>
<a href="/help/bibliographic_record.html#Google_Drive" title="Explain Google Drive."><span class="icon icon_help noprint"></span></a>
</span></th>
<th class="noprint"><span>
<a href="/help/bibliographic_record.html#OneDrive" title="Explain OneDrive."><span class="icon icon_help noprint"></span></a>
</span></th>
</tr>
<tr class="even" about="https://www.gutenberg.org/ebooks/5172.html.images" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="text/html" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/ebooks/5172.html.images" type="text/html" class="link" title="Download">Read this book online: HTML5</a></td>
<td class="noscreen">https://www.gutenberg.org/ebooks/5172.html.images</td>
<td class="right" property="dcterms:extent" content="336034">328&nbsp;kB</td>
<td class="noprint">
</td>
<td class="noprint">
</td>
<td class="noprint">
</td>
</tr><tr class="odd" about="https://www.gutenberg.org/files/5172/5172-h/5172-h.htm" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="text/html; charset=utf-8" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/files/5172/5172-h/5172-h.htm" type="text/html; charset=utf-8" class="link" title="Download">Read this book online: HTML (as submitted)</a></td>
<td class="noscreen">https://www.gutenberg.org/files/5172/5172-h/5172-h.htm</td>
<td class="right" property="dcterms:extent" content="352935">345&nbsp;kB</td>
<td class="noprint">
</td>
<td class="noprint">
</td>
<td class="noprint">
</td>
</tr><tr class="odd" about="https://www.gutenberg.org/ebooks/5172.epub3.images" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="application/epub+zip" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/ebooks/5172.epub3.images" type="application/epub+zip" class="link" title="Download">EPUB3 (E-readers incl. Send-to-Kindle)</a></td>
<td class="noscreen">https://www.gutenberg.org/ebooks/5172.epub3.images</td>
<td class="right" property="dcterms:extent" content="164806">161&nbsp;kB</td>
<td class="noprint">
<a href="/ebooks/send/dropbox/5172.epub3.images" title="Send to Dropbox." rel="nofollow"><span class="icon icon_dropbox"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/gdrive/5172.epub3.images" title="Send to Google Drive." rel="nofollow"><span class="icon icon_gdrive"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/msdrive/5172.epub3.images" title="Send to OneDrive." rel="nofollow"><span class="icon icon_msdrive"></span></a>
</td>
</tr><tr class="even" about="https://www.gutenberg.org/ebooks/5172.epub.noimages" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="application/epub+zip" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/ebooks/5172.epub.noimages" type="application/epub+zip" class="link" title="Download">EPUB (no images)</a></td>
<td class="noscreen">https://www.gutenberg.org/ebooks/5172.epub.noimages</td>
<td class="right" property="dcterms:extent" content="170392">166&nbsp;kB</td>
<td class="noprint">
<a href="/ebooks/send/dropbox/5172.epub.noimages" title="Send to Dropbox." rel="nofollow"><span class="icon icon_dropbox"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/gdrive/5172.epub.noimages" title="Send to Google Drive." rel="nofollow"><span class="icon icon_gdrive"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/msdrive/5172.epub.noimages" title="Send to OneDrive." rel="nofollow"><span class="icon icon_msdrive"></span></a>
</td>
</tr><tr class="odd" about="https://www.gutenberg.org/ebooks/5172.kf8.images" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="application/x-mobipocket-ebook" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/ebooks/5172.kf8.images" type="application/x-mobipocket-ebook" class="link" title="Download">Kindle</a></td>
<td class="noscreen">https://www.gutenberg.org/ebooks/5172.kf8.images</td>
<td class="right" property="dcterms:extent" content="347254">339&nbsp;kB</td>
<td class="noprint">
<a href="/ebooks/send/dropbox/5172.kf8.images" title="Send to Dropbox." rel="nofollow"><span class="icon icon_dropbox"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/gdrive/5172.kf8.images" title="Send to Google Drive." rel="nofollow"><span class="icon icon_gdrive"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/msdrive/5172.kf8.images" title="Send to OneDrive." rel="nofollow"><span class="icon icon_msdrive"></span></a>
</td>
</tr><tr class="even" about="https://www.gutenberg.org/ebooks/5172.kindle.images" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="application/x-mobipocket-ebook" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/ebooks/5172.kindle.images" type="application/x-mobipocket-ebook" class="link" title="Download">older Kindles</a></td>
<td class="noscreen">https://www.gutenberg.org/ebooks/5172.kindle.images</td>
<td class="right" property="dcterms:extent" content="319629">312&nbsp;kB</td>
<td class="noprint">
<a href="/ebooks/send/dropbox/5172.kindle.images" title="Send to Dropbox." rel="nofollow"><span class="icon icon_dropbox"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/gdrive/5172.kindle.images" title="Send to Google Drive." rel="nofollow"><span class="icon icon_gdrive"></span></a>
</td>
<td class="noprint">
<a href="/ebooks/send/msdrive/5172.kindle.images" title="Send to OneDrive." rel="nofollow"><span class="icon icon_msdrive"></span></a>
</td>
</tr><tr class="even" about="https://www.gutenberg.org/files/5172/5172-0.txt" typeof="pgterms:file">
<td><span class="icon icon_book"></span></td>
<td property="dcterms:format" content="text/plain; charset=utf-8" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/files/5172/5172-0.txt" type="text/plain; charset=utf-8" class="link" title="Download">Plain Text UTF-8</a></td>
<td class="noscreen">https://www.gutenberg.org/files/5172/5172-0.txt</td>
<td class="right" property="dcterms:extent" content="281259">275&nbsp;kB</td>
<td class="noprint">
</td>
<td class="noprint">
</td>
<td class="noprint">
</td>
</tr>
<tr class="even">
<td><span class="icon icon_folder"></span></td>
<td class="unpadded icon_file"><a href="/files/5172/" class="link">More Files…</a></td>
<td class="noscreen">https://www.gutenberg.org/files/5172/</td>
<td></td>
<td class="noprint"></td>
<td class="noprint"></td>
<td class="noprint"></td>
</tr>
</tbody>"""

def download_gutenberg_ebooks(gutenberg_id, base_folder):
    ebooks_url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}"
    response = requests.get(ebooks_url)
    ebooks_html_data = BeautifulSoup(response.content, "html.parser")

    for row in ebooks_html_data.find_all("tr"):
        file_url = row.get("about")
        if file_url:
            if "/ebooks/" in file_url:
                if file_url.endswith(".html.images"):
                    download_file(file_url, base_folder, "file_to_parse.html")
                else:
                    filename = file_url.split("/")[-1]
                    filename = filename.replace(".noimages", "")
                    filename = filename.replace(".images", "")
                    download_file(file_url, base_folder, filename)



def download_gutenberg_files(gutenberg_id, base_folder):
    other_files_url = f"https://www.gutenberg.org/files/{gutenberg_id}"
    download_gutenberg_ebooks(gutenberg_id, base_folder)
    download_gutenberg_directory(other_files_url, base_folder)

def find_gutenberg_html_file(base_folder):
    html_file_name = "file_to_parse.html"
    html_file_path = os.path.join(base_folder, html_file_name)
    with open(html_file_path, "r") as html_file:
        html_data = html_file.read()
    html_data = BeautifulSoup(html_data, "html.parser")
    return html_data

def parse_gutenberg_text(gutenberg_id, base_folder):
    html_data = find_gutenberg_html_file(base_folder)
    print(html_data)
    
base_folder = "projectfiles/gutenberg"

gutenberg_id = "5172"

download_gutenberg_files(gutenberg_id, base_folder)
# download_gutenberg_ebooks(gutenberg_id, base_folder)
parse_gutenberg_text(gutenberg_id, base_folder)