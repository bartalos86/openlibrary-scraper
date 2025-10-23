from os import listdir
import os
from os.path import isfile, join

from utils.file import sanitize_book_link
from utils.url import create_link, read_link_queue, read_visited_links, save_link_queue, save_visited_links



def get_downloaded_page_files():
  return [f for f in listdir("page_sources") if isfile(join("page_sources", f))]

def clean_forbidden_files():
  visited_links = read_visited_links()
  link_queue = read_link_queue();

  all_files = get_downloaded_page_files()
  last_file = ""
  files_to_remove = []
  new_visited_links = []

  for file in all_files:
    file_name = f"page_sources/{file}"
    with open(file_name, "r") as f:
      content = f.read()
      if "<html><head><title>403 Forbidden</title></head>" in content:
        files_to_remove.append(file_name)
        last_file = content

  print(last_file)
  print(f"File to remove: {len(files_to_remove)}")
  input()

  for file in files_to_remove:
    os.remove(file)

clean_forbidden_files()