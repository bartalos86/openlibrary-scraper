import re
from selenium.webdriver.common.by import By
from file import save_book_page_source


def extract_metadata(page, page_driver):
  if "/books/" in page:
    return extract_book_page_metadata(page_driver)
  else:
    return None

# def safe_get_property(driver, by, selector, attr="text"):
#   try:
#       element = driver.find_element(by, selector)
#       return element.text.strip() if attr == "text" else element.get_attribute(attr)
#   except Exception:
#       return "N/A"

# def safe_get_multiple_properties(driver, by, selector, attr="text"):
#   try:
#       elements = driver.find_elements(by, selector)
#       if not elements:
#         return "N/A"
#       values = [
#             element.text.strip() if attr == "text" else (element.get_attribute(attr) or "").strip()
#             for element in elements
#       ]
#       return ",".join(filter(None, values))
#   except Exception:
#       return "N/A"


def safe_find_property(source: str, pattern: str, group: int = 1):
    match = re.search(pattern, source, re.IGNORECASE | re.DOTALL)
    return match.group(group).strip() if match else "N/A"

def safe_find_multiple_properties(source: str, pattern: str, group: int = 1):
    matches = re.findall(pattern, source, re.IGNORECASE | re.DOTALL)
    if not matches:
        return "N/A"
    cleaned = [m.strip() for m in matches if m.strip()]
    return ",".join(cleaned)


def extract_book_page_metadata(page_source: str):
    book_data = {
        "id": safe_find_property(page_source, r'name="edition_id"\s+value="/books/([^"]+)"'),
        "title": safe_find_property(page_source, r'<h1[^>]*class="[^"]*work-title[^"]*"[^>]*>(.*?)</h1>'),
        "cover_url": safe_find_property(page_source, r'<meta property="og:image" content="([^"]+)"'),
        "author": safe_find_multiple_properties(page_source, r'<a[^>]*itemprop=["\']author["\'][^>]*>(.*?)</a>'),
        "rating": safe_find_property(page_source, r'<span[^>]*itemprop=["\']ratingValue["\'][^>]*>(.*?)</span>'),
        "date_published": safe_find_property(page_source, r'<span[^>]*itemprop=["\']datePublished["\'][^>]*>(.*?)</span>'),
        "publisher": safe_find_property(page_source, r'<a[^>]*itemprop=["\']publisher["\'][^>]*>(.*?)</a>'),
        "language": safe_find_property(page_source, r'<span[^>]*itemprop=["\']inLanguage["\'][^>]*>.*?<a[^>]*>(.*?)</a>'),
        "pages": safe_find_property(page_source, r'<a[^>]*itemprop=["\']numberOfPages["\'][^>]*>(.*?)</a>'),
        "description": safe_find_property(page_source, r'<div[^>]*class=["\']read-more__content["\'][^>]*>(.*?)</div>'),

        "published_in": safe_find_property(page_source, r'<dt[^>]*>Published in<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'),
        "series": safe_find_property(page_source, r'<dt[^>]*>Series<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'),
        "genre": safe_find_property(page_source, r'<dt[^>]*>Genre<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'),
        "isbn10": safe_find_property(page_source, r'<dt[^>]*>ISBN 10<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'),
        "isbn13": safe_find_property(page_source, r'<dt[^>]*>ISBN 13<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'),

        "goodreads_url": safe_find_property(page_source, r'<dt[^>]*>Goodreads<\/dt>.*?<a[^>]*href=["\']([^"\']+)["\']'),
        "download_pdf_url": safe_find_property(page_source, r'<a[^>]*data-ol-link-track=["\']Download\|pdf_ia["\'][^>]*href=["\']([^"\']+)["\']'),
        "download_epub_url": safe_find_property(page_source, r'<a[^>]*data-ol-link-track=["\']Download\|epub_ia["\'][^>]*href=["\']([^"\']+)["\']'),
        "download_text_url": safe_find_property(page_source, r'<a[^>]*data-ol-link-track=["\']Download\|text_ia["\'][^>]*href=["\']([^"\']+)["\']'),
        "download_mobi_url": safe_find_property(page_source, r'<a[^>]*data-ol-link-track=["\']Download\|mobi_ia["\'][^>]*href=["\']([^"\']+)["\']'),
        "download_daisy_url": safe_find_property(page_source, r'<a[^>]*data-ol-link-track=["\']Download\|daisy_ia["\'][^>]*href=["\']([^"\']+)["\']'),
        "worldcat_rent_url": safe_find_property(page_source, r'<a[^>]*class=["\']worldcat-link["\'][^>]*href=["\']([^"\']+)["\']'),
        "betterworldbooks_url": safe_find_property(page_source, r'<li[^>]*class=["\']prices-betterworldbooks["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']'),
        "amazon_url": safe_find_property(page_source, r'<li[^>]*class=["\']prices-amazon["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']'),
        "bookshop_url": safe_find_property(page_source, r'<li[^>]*class=["\']prices-bookshop-org["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']'),

                # Additional regex-based extractions you requested:
        "download_mp3_url": safe_find_property(page_source, r'href=["\'](https?://[^"\']*?mp3\.zip)["\']'),
        "subjects_people": safe_find_multiple_properties(page_source, r'<a href="/subjects/person:[^"]+"[^>]*>([^<]+)</a>'),
        "subjects_places": safe_find_multiple_properties(page_source, r'<a href="/subjects/place:[^"]+"[^>]*>([^<]+)</a>'),
    }

    if book_data["description"] != "N/A":
        book_data["description"] = re.sub(r'<.*?>', '', book_data["description"]).strip()

    print(f"\nViewing book with title: {book_data['title']}")
    print(f"Cover: {book_data['cover_url']}")
    print(f"Author: {book_data['author']}")
    print(f"Rating: {book_data['rating']}")
    print(f"Date published: {book_data['date_published']}")
    print(f"Publisher: {book_data['publisher']}")
    print(f"Language: {book_data['language']}")
    print("------------------------------------\n")

    return book_data
# def extract_book_page_metadata(page_driver):
#   book_data = {
#       "title": safe_get_property(page_driver, By.CSS_SELECTOR, "h1.work-title"),
#       "cover_url": safe_get_property(page_driver, By.CSS_SELECTOR, "img.cover", attr="src"),
#       "author": safe_get_multiple_properties(page_driver, By.CSS_SELECTOR, "a[itemprop='author']"),
#       "rating": safe_get_property(page_driver, By.CSS_SELECTOR, "span[itemprop='ratingValue']"),
#       "date_published": safe_get_property(page_driver, By.CSS_SELECTOR, "span[itemprop='datePublished']"),
#       "publisher": safe_get_property(page_driver, By.CSS_SELECTOR, "a[itemprop='publisher']"),
#       "language": safe_get_property(page_driver, By.CSS_SELECTOR, "span[itemprop='inLanguage'] a"),
#       "pages": safe_get_property(page_driver, By.CSS_SELECTOR, "a[itemprop='numberOfPages']"),
#       "description": safe_get_property(page_driver, By.CSS_SELECTOR, "div.read-more__content.markdown-content"),
#       "published_in": safe_get_property(page_driver, By.XPATH, "//dt[normalize-space()='Published in']/following-sibling::dd[1]"),
#       "series": safe_get_property(page_driver, By.XPATH, "//dt[normalize-space()='Series']/following-sibling::dd[1]"),
#       "genre": safe_get_property(page_driver, By.XPATH, "//dt[normalize-space()='Genre']/following-sibling::dd[1]"),
#       "isbn10": safe_get_property(page_driver, By.XPATH, "//dt[normalize-space()='ISBN 10']/following-sibling::dd[1]"),
#       "isbn13": safe_get_property(page_driver, By.XPATH, "//dt[normalize-space()='ISBN 13']/following-sibling::dd[1]"),
#       "goodreads_url": safe_get_property(page_driver, By.XPATH, "//dt[normalize-space()='Goodreads']/following-sibling::dd[1]/a", attr="href"),
#       "download_pdf_url": safe_get_property(page_driver, By.CSS_SELECTOR, "a[data-ol-link-track='Download|pdf_ia']", attr="href"),
#       "download_text_url": safe_get_property(page_driver, By.CSS_SELECTOR, "a[data-ol-link-track='Download|text_ia']", attr="href"),
#       "download_epub_url": safe_get_property(page_driver, By.CSS_SELECTOR, "a[data-ol-link-track='Download|epub_ia']", attr="href"),
#       "download_mobi_url": safe_get_property(page_driver, By.CSS_SELECTOR, "a[data-ol-link-track='Download|mobi_ia']", attr="href"),
#       "download_daisy_url": safe_get_property(page_driver, By.CSS_SELECTOR, "a[data-ol-link-track='Download|daisy_ia']", attr="href"),
#       "worldcat_rent_url": safe_get_property(page_driver, By.CSS_SELECTOR, "a.worldcat-link", "href"),
#       "betterworldbooks_url": safe_get_property(page_driver, By.CSS_SELECTOR, "li.prices-betterworldbooks a", "href"),
#       "amazon_url": safe_get_property(page_driver, By.CSS_SELECTOR, "li.prices-amazon a", "href"),
#       "bookshop_url": safe_get_property(page_driver, By.CSS_SELECTOR, "li.prices-bookshop-org a", "href"),
#   }
#   try:
#     page_driver.execute_script("window.scrollTo(0, 3500)")
#   except:
#     print("Cannot scroll")
#   print(f"\nViewing book with title: {book_data['title']}")
#   print(f"Cover: {book_data['cover_url']}")
#   print(f"Author: {book_data['author']}")
#   print(f"Rating: {book_data['rating']}")
#   print(f"Date published: {book_data['date_published']}")
#   print(f"Publisher: {book_data['publisher']}")
#   print(f"Language: {book_data['language']}")
#   print("------------------------------------\n")

#   return book_data
