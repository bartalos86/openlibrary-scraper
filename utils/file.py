
import datetime
import os
import re


STARTING = 1

def sanitize_value(value):
    if value is None:
        return "N/A"
    sanitized = str(value).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    sanitized = ' '.join(sanitized.split())
    return sanitized

def save_book(book_metadata):
  global STARTING
  header = ""
  if STARTING == 1:
    generated_header = generate_header(book_metadata)
    try:
        with open("books.tsv", "r") as f:
            header = f.readline()
    except FileNotFoundError:
        header = ""

    if header != generated_header:
      with open("books.tsv", "w") as f:
        f.write(generated_header)

    STARTING = 0

  append_book_to_file(book_metadata)

def save_book_page_source(source, book_title):
  os.makedirs("page_sources", exist_ok=True)
  if not book_title or book_title == "N/A":
        book_title = f"unknown_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

  safe_title = sanitize_book_link(book_title)

  filename = generate_link_path(safe_title)

  with open(filename, "w", encoding="utf-8") as f:
     f.write(source)

def read_book_from_file(page):
  safe_title = sanitize_book_link(page)

  filename = generate_link_path(safe_title)
  source = None
  try:
    with open(filename, "r", encoding="utf-8") as f:
      source = f.read()
  except:
    source = None
  return source


def sanitize_book_link(link):
  safe_title = re.sub(r'[<>:"/\\|?*]', '_', str(link))
  safe_title = safe_title[:100]
  return safe_title;

def generate_link_path(safe_link):
  return f"page_sources/{safe_link}.html"

def generate_header(book_metadata):
  keys = book_metadata.keys()
  header = "\t".join(keys) + "\n"
  return header;


def append_book_to_file(book_metadata):
  with open("books.tsv", "a") as f:
    values = [sanitize_value(book_metadata[k]) for k in book_metadata.keys()]
    f.write("\t".join(values) + "\n")
