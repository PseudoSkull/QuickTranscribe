#WS_collection

def print_in_color(color_code, text):
    print("\033[{}m{}\033[00m" .format(color_code, text))

def print_in_green(text):
    print_in_color("92", text)

def print_in_red(text):
    print_in_color("91", text)

def print_in_yellow(text):
    print_in_color("93", text)

def print_in_blue(text):
    print_in_color("96", text)

def process_break():
    print("\n\n")
    return input(">")

def save_html_to_file(soup):
    print("\nSaving page HTML to file...")
    html_content = soup.prettify()
    output_file = 'page.html'
    with open(output_file, 'w+', encoding='utf-8') as file:
        file.write(html_content)
    print_in_green(f"Page HTML saved to {output_file}!")