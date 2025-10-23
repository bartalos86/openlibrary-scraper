
import csv
from dataclasses import dataclass, field
from datetime import datetime
import os
import re
from selenium.webdriver.common.by import By

from models.models import Link


def read_visited_links():
  links = []
  try:
    with open("storage/visited_links.tsv", "r", newline="", encoding="utf-8") as f:
      reader = csv.DictReader(f, delimiter="\t")
      for row in reader:
          links.append(Link(
              book_id=get_book_id_from_link(row["url"]),
              url=row["url"],
              parent=row["parent"],
              date_accessed=datetime.fromisoformat(row["date_accessed"]) if row["date_accessed"] else None
          ))
    return links
  except Exception as e:
    return []

def save_visited_links(visited_links):
  os.makedirs("storage", exist_ok=True)
  with open("storage/visited_links.tsv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["url", "parent", "date_accessed"])
    for link in visited_links:
      writer.writerow([link.url, link.parent, link.date_accessed.isoformat() if link.date_accessed else None])

def read_link_queue():
  links = []
  try:
    with open("storage/link_queue.tsv", "r", newline="", encoding="utf-8") as f:
      reader = csv.DictReader(f, delimiter="\t")
      for row in reader:
          links.append(Link(
              book_id=get_book_id_from_link(row["url"]),
              url=row["url"],
              parent=row["parent"],
              date_accessed=datetime.fromisoformat(row["date_accessed"]) if row["date_accessed"] else None
          ))
    return links
  except:
    return []

def save_link_queue(link_queue):
  os.makedirs("storage", exist_ok=True)
  with open("storage/link_queue.tsv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["url", "parent", "date_accessed"])
    for link in link_queue:
      writer.writerow([link.url, link.parent, link.date_accessed.isoformat() if link.date_accessed else None])



def get_links_from_page(page_source, page_url):
    base_url = "https://openlibrary.org"
    unique_links = set()

    hrefs = re.findall(r'href=["\']([^"\']+)["\']', page_source)

    for href in hrefs:

      if "?" in href or is_file_url(href):
        continue;

      if href.startswith("/"):
          absolute_url = base_url + href
          unique_links.add(absolute_url)
      elif href.startswith(base_url):
          unique_links.add(href)

    links = [create_link(url, page_url) for url in sorted(unique_links)]

    return links

def create_link(url, parent):
  return Link(book_id=get_book_id_from_link(url),url=url,date_accessed=None,parent=parent)

def create_link_with_accessed(url, parent):
  return Link(book_id=get_book_id_from_link(url),url=url,parent=parent)


def get_not_visited_from_new_links(visited_links, link_queue, new_links):
  not_visited = []
  visited_urls = {link.url for link in visited_links}
  queued_urls = {link.url for link in link_queue}
  for new_link in new_links:
      if (new_link.url not in visited_urls and new_link.url not in queued_urls):
          not_visited.append(new_link)

  return not_visited

def get_not_visited_from_new_links_optimized(visited_urls, queued_urls, new_links):
  not_visited = []
  for new_link in new_links:
      if (new_link.url not in visited_urls and new_link.url not in queued_urls):
          not_visited.append(new_link)
  return not_visited

def get_book_id_from_link(href):
  match = re.search(r'/books/([^/]+)', href)
  return match.group(1) if match else None

def is_file_url(url):
    return re.search(r'\.[a-zA-Z0-9]{1,5}($|\?|#)', url) is not None