
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from file import read_book_from_file, save_book, save_book_page_source
from header import pick_random_headers
from metadata import extract_metadata
from url import create_link, create_link_with_accessed, get_book_id_from_link, get_links_from_page, get_not_visited_from_new_links, read_link_queue, read_visited_links, save_link_queue, save_visited_links

headers = {
    "Referer": "https://google.com",
}

chrome_options = Options()
chrome_options.add_argument("--headless=new")

# Start the driver
driver = webdriver.Chrome(options=chrome_options)

driver.execute_cdp_cmd("Network.enable", {})


# driver.get("https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending/")  # Test endpoint
# print(driver.page_source)

starting_page = "https://openlibrary.org";
maximum_depth = 5
maximum_books = 3

book_index = 0
visited_links = read_visited_links();
link_queue = []

previous_link = ""


def try_get_page(page):
  source = read_book_from_file(page)
  if source == None:
    print("Accessing from web")
    random_headers = pick_random_headers()
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": random_headers})
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random_headers["User-Agent"], "acceptLanguage": random_headers["Accept-Language"]})

    driver.get(page)
    wait_delay = random.randrange(5, 15, 1)
    driver.implicitly_wait(wait_delay)
    time.sleep(wait_delay)
    source = driver.page_source
  else:
    print("Accessing from file")
  return source



def load_starting_page():
  global link_queue
  global visited_links
  global book_index
  global previous_link

  visited_links = read_visited_links();
  book_index = len(visited_links)

  page_source = try_get_page(starting_page)

  links = get_links_from_page(page_source, starting_page);
  # print(links)
  #We read linq queue from file is available to continue session
  link_queue = read_link_queue();
  if not link_queue:
    link_queue = get_not_visited_from_new_links(visited_links, link_queue, links)


  while link_queue:
    crawl_pages(link_queue.pop(0))


def crawl_pages(link):
  global book_index
  global visited_links
  global link_queue

  page = link.url

  book_index = book_index +1;
  print(f"URLs in Queue: {book_index}/{len(link_queue)}\n")
  print(f"Total books extracted: {len(visited_links)}")



  ## Load source
  page_source = try_get_page(link.url)

  if "<html><head><title>403 Forbidden</title></head>" in page_source:
    print(page_source)
    print("We have been blocked")
    quit()
  # print(page_source)
  book_id = link.book_id
  visited_books = {link.book_id for link in visited_links}

  print(f"Page: {page}\nBook id: {book_id}")
  # We do not want one book multiple times
  if book_id != None and book_id not in visited_books:
    book_metadata = extract_metadata(page, page_source)

    if book_metadata != None and book_metadata["title"] != "N/A":
      save_book(book_metadata)


  save_book_page_source(page_source, page)
  visited_link = create_link_with_accessed(url=page,parent=link.parent)
  visited_links.append(visited_link)
  save_visited_links(visited_links)
  save_link_queue(link_queue)

  links = get_links_from_page(page_source, page);
  new_links = get_not_visited_from_new_links(visited_links, link_queue, links)

  if len(link_queue) < 25000:
    link_queue.extend(new_links)


load_starting_page()
driver.quit()
