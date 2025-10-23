
# Openlib Scraper Project

As my project I will be scraping books from the openlibrary.org page. My target information for scraping will be only the books themselves. Later addtitional details about the author and publisher will be joined in from wikipedia.

**The targer page for scraping**: https://openlibrary.org/

**Fields which are scraped**: id, title, cover_url, author, rating, date_published, publisher, language, pages, description, published_in, series, genre, isbn10, isbn13, goodreads_url, download_pdf_url, download_epub_url, download_text_url, download_mobi_url, download_daisy_url, worldcat_rent_url, betterworldbooks_url, amazon_url, bookshop_url, download_mp3_url, subjects_people, subjects_places

Data samples:
``` tsv
id	title	cover_url	author	rating	date_published	publisher	language	pages	description	published_in	series	genre	isbn10	isbn13	goodreads_url	download_pdf_url	download_epub_url	download_text_url	download_mobi_url	download_daisy_url	worldcat_rent_url	betterworldbooks_url	amazon_url	bookshop_url	download_mp3_url	subjects_people	subjects_places
OL10174042M	Algebra and Trigonometry Structure and Method Book 2 (Teacher's Edition) (The Classic)	https://covers.openlibrary.org/b/id/8519822-L.jpg	Richard G. Brown,Richard G. Brown	4.0 (1 rating)	2000	McDougal Littell	English	N/A	N/A	N/A	N/A	N/A	0395977266	9780395977262	N/A	N/A	N/A	N/A	N/A	N/A	https://worldcat.org/isbn/9780395977262	https://www.betterworldbooks.com/product/detail/-9780395977262	https://www.amazon.com/dp/B00IN8US6M/?tag=internetarchi-20	https://bookshop.org/a/3112/9780395977262	N/A	N/A	N/A
OL10290330M	"Reader's Digest" DIY Manual	https://covers.openlibrary.org/b/id/2350235-L.jpg	Reader's Digest Association,Reader's Digest Association	N/A	September 24, 2004	Reader's Digest	N/A	N/A	N/A	N/A	N/A	N/A	0276429338	9780276429330	https://www.goodreads.com/book/show/974810	N/A	N/A	N/A	N/A	N/A	https://worldcat.org/isbn/9780276429330	https://www.betterworldbooks.com/product/detail/-9780276429330	https://www.amazon.com/dp/0276429338/?tag=internetarchi-20	https://bookshop.org/a/3112/9780276429330	N/A	N/A	N/A
OL10423933M	Criminal Procedure: Criminal Practice Series	https://openlibrary.org/images/icons/avatar_book-sm.png	Wayne R. LaFave,Wayne R. LaFave	N/A	1999	West Publishing	English	N/A	N/A	N/A	N/A	N/A	0314243410	9780314243416	N/A	N/A	N/A	N/A	N/A	N/A	https://worldcat.org/oclc/42880035	https://www.betterworldbooks.com/product/detail/-9780314243416	https://www.amazon.com/dp/0314243410/?tag=internetarchi-20	https://bookshop.org/a/3112/9780314243416	N/A	N/A	United States
OL14975868M	The girl in the green valley	https://covers.openlibrary.org/b/id/10758687-L.jpg	Elizabeth Hoy,Elizabeth Hoy	3.6 (7 ratings)	1973	Mills and Boon	English	N/A	N/A	London	N/A	N/A	0263055256	N/A	https://www.goodreads.com/book/show/4915497	N/A	N/A	N/A	N/A	N/A	https://worldcat.org/oclc/1615211	https://www.betterworldbooks.com/product/detail/-9780263055252	https://www.amazon.com/dp/0263055256/?tag=internetarchi-20	https://bookshop.org/a/3112/9780263055252	N/A	N/A	N/A
OL14981439M	Fight for Love	https://covers.openlibrary.org/b/id/13049586-L.jpg	Penny Jordan,Penny Jordan	3.9 (11 ratings)	1988	Mills &amp; Boon	English	N/A	N/A	Richmond	N/A	N/A	0263758699	N/A	N/A	N/A	N/A	N/A	N/A	N/A	https://worldcat.org/oclc/655874970	https://www.betterworldbooks.com/product/detail/-9780263758696	https://www.amazon.com/dp/0263758699/?tag=internetarchi-20	https://bookshop.org/a/3112/9780263758696	N/A	Natasha Ames,Jay Travers	Texas,England
```

## Questions and answers:

- book search (title, description, genre, language, publisher): this will display all important information about a book
- download/buy links for book (title, description, genre, language, publisher):  displays all the available formats to download the book or buy/rent urls
- author (name): search for book by author name, later this will also display additional information about the found authors
- language (language): find book in the given languages
- publisher (publisher name): find books from given publisher
- subjects (people or place): find books with the given subjects
- similar (isbn): find similar books


## Frameworks

**Framework for scraping**: Selenium
Reasons:
 - Big parts of the pages are rendered dynamically using Javascript. For example carousel of books. Selenium has the best support forrendering pages with Javascript
 - Selenium offered all the necessary functionalities for: sleep and (through workaround) modifying the user-agent and headers.
 - Selenium also has the option to simulate other browsers, in case the pages do not render correctly in one.
 - For our use case Selenium is fast enough
Disadvantages:
- Selenium may use more resources (it is not a problem in our case)

**Frameowork for regex**: re
- default python regex library, I used this one due to the fact that I did not need anything more complex for this use case

**Additional libraries**: colored, textwrap
- these libraries were used to format for the console output

## Metadata during crawling:
For the initial implementation of the crawler I created two .tsv files. One for visited links and the second for saving the queue on the disk. These had the following format, these functionality is still in the code but not used anymore:
```tsv
url	parent	date_accessed
```
Later I have come to the conclusion that I do not need to save these links to the disk, I can just keep them in memory and save my SSD from constant overwrites. Due to saving all source pages I can deterministically reconstruct the whole link tree from the source files themselves.

## Headers and other configuration:

**Wait time**: dynamically 5-10 sec

During testing I have found that: wait time less that 5 seconds caused crashes and timeouts and wait time above 10 was unnecessary. So 5-10 seconds was an ideal range where the crawler didnt crash, did not get blocked and was not waiting unreasonably long time.

### Headers
- Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
- User-Agent: dynamically
  - Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Contact: xbartalos@stuba.sk
  - Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36, Contact: xbartalos@stuba.sk
  - Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36, Contact: xbartalos@stuba.sk
  - Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1, Contact: xbartalos@stuba.sk
- Referer: dynamically
  - https://www.google.com/
  - https://www.bing.com/
  - https://duckduckgo.com/
  - https://openlibrary.org/
- Accept-Language: dynamically
  - en-US,en;q=0.9
  - en-GB,en;q=0.9
  - en-US;q=0.8,en;q=0.7

On header where the `dynamic` option was specified these were selected randomly for each request from the given options. Dynamic headers were needed due to the fact that our crawler kep getting blocked, for this reasing we keep chaning randomly the User-Agent with each request (this is the most important) and also the Referrer and Accept languages. Fot he user agent the choice of headers was based on the most popular user agents (which I modified to include my contact details) so that our crawler is not suspicious.
For the Referrer the values are the most popular seach engines and the page itself.
For the Accept-Language the values are english languages with some parameter differences to be less suspicious.


## Code

### URL Extraction

All the url extraction from the pages was done using this function:

``` python
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

def is_file_url(url):
    return re.search(r'\.[a-zA-Z0-9]{1,5}($|\?|#)', url) is not None
```

### Book extraction

All the book data extraction happened using extract_book_page_metadata() function which gets the page source as input and where for each property there is a defined regex using which the value for the given property is extracted in safe_find_property() or for multiple values safe_find_multiple_properties().

```python

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

        "download_mp3_url": safe_find_property(page_source, r'href=["\'](https?://[^"\']*?mp3\.zip)["\']'),
        "subjects_people": safe_find_multiple_properties(page_source, r'<a href="/subjects/person:[^"]+"[^>]*>([^<]+)</a>'),
        "subjects_places": safe_find_multiple_properties(page_source, r'<a href="/subjects/place:[^"]+"[^>]*>([^<]+)</a>'),
    }

    if book_data["description"] != "N/A":
      book_data["description"] = re.sub(r'<.*?>', '', book_data["description"]).strip()

```

### Indexing
 I have a total of 6 indexes, where each category indexes the documents based on the combination of different fields:
 - title: title, description, genre, language, publisher
 - author: author
 - language: language
 - publisher: publisher
 - subjects: subjects_people, subjects_places
 - all: title, author, genre, publisher, language, description, series, subjects_people, subjects_places

The document text for indexes where multiple fields are included is the concatenated string value of all the fields.
For each of the indexes there are different document frequency values.

To index a field (or combination of multiple):
- first we tokenize the text and get the unique tokens
- for each unique term we save the document it is contained in
- we count that in how many documents the term is included in total
- also for searching purposes we calculate for each word the positional index / document (this is for exact phrase search, not realted to indexing)

For each index we then build the tfid vectors, this is done when all the documents are added:
- for each document we count each word (the text retrieved is according to the index)
- then for each term we calculate the idf then which we normalize using logarithmic normalization `(1 + math.log10(tf)) * idf`
- we append the calculated idf wector to the results for the given index

#### Calulating idf
I have chosen 2 methods to calculate the idf according to the lectures:
- Log-Inverse Document Frequency (standard): log(N/df) - this ranks only based on how many docuemnts contain the term out of all the documents
- Probabilistic IDF: log((N - df + 0.5) / (df + 0.5)) - this compares the number of documents which contain the term with the documents that do not
For each term the idf is calculated according to the configured mode of the indexer. This mode is set on the initialization of the indexer.

#### Search
The implemntation supports complete boolean search for filtering the results. Supported operators are: `AND`, `OR`, `NOT`, `"concerete phrase"` and `(grouping)`.

We first parse the boolean expression when there are groups than reqursively for each group. The results are then ranked using cosine similarity.
The algorithm:
- we count each term in the query
- we calculate the idf and create the tfid vector
- we rank each result of the boolean search using cosine similarity.

``` python

scores = []
query_terms = self._tokenize(query)
q_counts = Counter(query_terms)
q_vec = {}
for term, tf in q_counts.items():
    idf = self._idf(term, index_name)
    q_vec[term] = (1 + math.log10(tf)) *
for doc_id, (book_id, book) in enumerate(self.documents):
    if book_id in result_set:
        score = self._cosine_similarity(q_vec, self.tfidf_vectors[index_name][doc_id])
        scores.append((book_id, book, score if score > 0 else 0.1))
scores.sort(key=lambda x: x[-1], reverse=True)
return scores[:top_n]

```


### Search examples



## Statistics

| Metric                          | Value        |
|----------------------------------|--------------|
| **Total number of crawled documents** | 22,459       |
| **Size on disk**                 | 3.44 GB      |
| **Approximate time to index**    | ~3 minutes   |
| **Total number of useful books** | 2,114        |


## How to run

The scarper part of the application can be run using `python3 scraper.py`. This will start the crawling from the root page, if a page is already downloaded crawl the links from the file if not then starts downloading and saving the page sources to disk.

The indexer part of the application can be started using `python3 menu.py <idf_method>`. This will first index all the available files starting from the root. The indexer supports two type of modes (probabilistic | standard) which can be set by passing the desired method as argument.

### Packages

`pip install selenium`
`pip install colored`

## Unit tests

Unit tests for testing the regex snippets on sample books are in the `test` folder. The correct results are in the `expencted_results.tsv` and the html files are in the `test/test_html` folder.
The tests can be run using `python3 regex_test.py`