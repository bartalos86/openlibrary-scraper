import csv
import textwrap
import colored
from indexer import BookSearchEngine

DATA_FILE = "books_arch.tsv"  # Path to your CSV file
engine = BookSearchEngine(idf_mode="probabilistic")

def safe_get(book, field):
    return book.get(field, "").strip() or "N/A"

def load_books():
    books = []
    with open(DATA_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            normalized = {k: (v.strip() if v and v.strip() else "N/A") for k, v in row.items()}
            books.append(normalized)
            engine.add_book(row)
    return books


def find_books_by_field(field, value):
    search_results = engine.boolean_search(value, 10, field)
    results = []
    for _, book, score in search_results:
        print(f" - {score:.4f} {book.get(field) or book["title"]}")
        results.append(book)
    return results

def print_book_details(book):
    title_highlight = colored.fg("yellow")
    author_highlight = colored.fg('light_blue')
    goodreads_highlight = colored.fg('light_green_3')
    description_highlight = colored.fg("grey_37")
    rating_highlight = colored.fg("light_yellow")

    title_text = colored.stylize(f"{safe_get(book,'title')}", title_highlight)
    author_text = colored.stylize(f"{safe_get(book,'author')}", author_highlight)
    rating_text = colored.stylize(f"{safe_get(book,'rating')}", rating_highlight)
    goodreads_text = colored.stylize(f"{safe_get(book,'goodreads_url')}", goodreads_highlight)
    description_text = colored.stylize(f"{safe_get(book,'description')}", description_highlight)

    print(f"\n📖 [{i}] {title_text} by {author_text}")
    print(f"Publisher: {safe_get(book,'publisher')} | Year: {safe_get(book,'date_published')} | Language: {safe_get(book,'language')}")
    print(f"Genre: {safe_get(book,'genre')} | Pages: {safe_get(book,'pages')} | Rating: {rating_text}")
    print("Description:")
    wrapped = textwrap.fill(description_text, width=80)
    print(wrapped if wrapped != "N/A" else "N/A")
    print(f"Goodreads: {goodreads_text}\n")

def print_book_summary(book, index=None):
    """Print one-line summary for a book."""
    prefix = f"[{index}] " if index is not None else ""
    title = safe_get(book, "title")

    author_highlight = colored.fg("yellow")
    author_text = colored.stylize(f"{safe_get(book,'author')}", author_highlight)

    year = safe_get(book, "date_published")
    genre = safe_get(book, "genre")
    print(f"{prefix}{title} — {author_text} ({year}) [{genre}]")


# ---------- Commands ----------
def show_book_info(title):
    matches = find_books_by_field("title", title)
    if not matches:
        print("❌ No books found with that title.")
        return

    title_highlight = colored.fg("yellow")
    author_highlight = colored.fg('light_blue')
    goodreads_highlight = colored.fg('light_green_3')
    description_highlight = colored.fg("grey_37")
    rating_highlight = colored.fg("light_yellow")

    for i, book in enumerate(matches, 1):
        title_text = colored.stylize(f"{safe_get(book,'title')}", title_highlight)
        author_text = colored.stylize(f"{safe_get(book,'author')}", author_highlight)
        rating_text = colored.stylize(f"{safe_get(book,'rating')}", rating_highlight)
        goodreads_text = colored.stylize(f"{safe_get(book,'goodreads_url')}", goodreads_highlight)
        description_text = colored.stylize(f"{safe_get(book,'description')}", description_highlight)
        print(f"\n📖 [{i}] {title_text} by {author_text}")
        print(f"Publisher: {safe_get(book,'publisher')} | Year: {safe_get(book,'date_published')} | Language: {safe_get(book,'language')}")
        print(f"Genre: {safe_get(book,'genre')} | Pages: {safe_get(book,'pages')} | Rating: {rating_text}")
        print("Description:")
        wrapped = textwrap.fill(description_text, width=80)
        print(wrapped if wrapped != "N/A" else "N/A")
        print(f"Goodreads: {goodreads_text}\n")


def show_download_links(title):
    matches = find_books_by_field("title", title)
    if not matches:
        print("❌ No books found with that title.")
        return

    title_highlight = colored.fg("yellow")
    author_highlight = colored.fg('light_blue')


    for i, book in enumerate(matches, 1):
        title_text = colored.stylize(f"{safe_get(book,'title')}", title_highlight)
        author_text = colored.stylize(f"{safe_get(book,'author')}", author_highlight)
        print(f"\n📥 [{i}] Download links for {title_text} by {author_text}:")
        links = {
            "PDF": safe_get(book, "download_pdf_url"),
            "EPUB": safe_get(book, "download_epub_url"),
            "TEXT": safe_get(book, "download_text_url"),
            "MOBI": safe_get(book, "download_mobi_url"),
            "DAISY": safe_get(book, "download_daisy_url"),
            "MP3": safe_get(book, "download_mp3_url"),
            "RENT": safe_get(book, "worldcat_rent_url"),
            "BETTERWORLD": safe_get(book, "betterworldbooks_url"),
            "AMAZON": safe_get(book, "amazon_url"),
            "BOOKSHOP": safe_get(book, "bookshop_url"),
        }
        found_any = False
        link_highlight = colored.fg("green")

        for fmt, url in links.items():
            if url != "N/A":
              link_text = colored.stylize(f"{url}", link_highlight)
              print(f"  - {fmt}: {link_text}")
              found_any = True
        if not found_any:
            print("  No download links available.")


def show_author_info(author):
    author_books = find_books_by_field("author", author)
    if not author_books:
        print("❌ No books found by this author.")
        return

    print(f"\n👤 Books by {author}:")
    for i, b in enumerate(author_books, 1):
        print_book_summary(b, i)


def show_language_books(language):
    lang_books = find_books_by_field("language", language)
    if not lang_books:
        print("❌ No books found in this language.")
        return

    author_highlight = colored.fg("light_blue")
    lang_highlight = colored.fg("green")

    print(f"\n📚 Books in language: '{language}':")
    for i, book in enumerate(lang_books, 1):
      prefix = f"[{i}] " if i is not None else ""
      title = safe_get(book, "title")

      author_text = colored.stylize(f"{safe_get(book,'author')}", author_highlight)
      language_text = colored.stylize(f"{safe_get(book,'language')}", lang_highlight)

      year = safe_get(book, "date_published")
      genre = safe_get(book, "genre")
      print(f"{prefix}{title} — {author_text} ({year}) [{genre}] - {language_text}")


def show_publisher_books(publisher):
    publisher_books = find_books_by_field("publisher", publisher)
    if not publisher_books:
        print("❌ No books found from this publisher.")
        return

    print(f"\n🏢 Books published by '{publisher}':")
    for i, b in enumerate(publisher_books, 1):
        print_book_summary(b, i)

def show_subjects_books(subject):
    subject_books = find_books_by_field("subjects", subject)
    if not subject_books:
        print("❌ No books found with this subject.")
        return

    title_highlight = colored.fg("yellow")
    author_highlight = colored.fg('light_blue')
    subjects_highlight = colored.fg("green")


    print(f"\n🏢 Books with '{subject}':")
    for i, book in enumerate(subject_books, 1):
      title_text = colored.stylize(f"{safe_get(book,'title')}", title_highlight)
      author_text = colored.stylize(f"{safe_get(book,'author')}", author_highlight)
      people_subject_text = colored.stylize(f"{safe_get(book,'subjects_people')}", subjects_highlight)
      place_subject_text = colored.stylize(f"{safe_get(book,'subjects_places')}", subjects_highlight)

      print(f"\n📖 [{i}] {title_text} by {author_text}")
      print(f"Publisher: {safe_get(book,'publisher')} | Year: {safe_get(book,'date_published')} | Language: {safe_get(book,'language')}")
      print("People subjects:")
      wrapped = textwrap.fill(people_subject_text, width=80)
      print(wrapped if wrapped != "N/A" else "N/A")
      print("Place subjects:")
      wrapped = textwrap.fill(place_subject_text, width=80)
      print(wrapped if wrapped != "N/A" else "N/A")


def show_similar_books(books, isbn):
    target = None
    for b in books:
        if safe_get(b, "isbn10") == isbn or safe_get(b, "isbn13") == isbn:
            target = b
            break

    if not target:
        print("❌ ISBN not found.")
        return

    genre = safe_get(target, "genre")
    author = safe_get(target, "author")
    publisher = safe_get(target, "publisher")
    rating = safe_get(target, "rating")
    print(f"\n🔍 Similar books to '{safe_get(target,'title')}' (Genre: {genre})")

    similar = find_books_by_field("all", f"{genre} OR {author} OR {publisher} OR {rating}")
    # similar = [b for b in books if safe_get(b, "genre") == genre and safe_get(b, "title") != safe_get(target, "title")]
    if not similar:
        print("No similar books found.")
    else:
        for i, b in enumerate(similar[:10], 1):
            print_book_summary(b, i)


# ---------- Main CLI ----------
def main():
    books = load_books()
    engine.build_tfidf()
    engine.summary()

    print("=== 📚 Book Search Interface ===")
    print("Commands:")
    print(" book <name, desc>         → info about a book")
    print(" downloads <name, desc>    → download links")
    print(" author <name>             → books by author")
    print(" language <language>       → books in genre")
    print(" publisher <name>          → books by publisher")
    print(" subjects <name>           → books with subject")
    print(" similar <isbn>            → similar books")
    print(" exit                      → quit\n")

    while True:
        try:
            cmd = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting.")
            break

        if not cmd:
            continue
        if cmd.lower() == "exit":
            print("👋 Exiting.")
            break

        parts = cmd.split(" ", 1)
        if len(parts) != 2:
            print("⚠️  Invalid command. Example: 'book Dune'")
            continue

        action, arg = parts[0].lower(), parts[1].strip()

        if action == "book":
            show_book_info(arg)
        elif action == "downloads":
            show_download_links(arg)
        elif action == "author":
            show_author_info(arg)
        elif action == "language":
            show_language_books(arg)
        elif action == "publisher":
            show_publisher_books(arg)
        elif action == "subjects":
            show_subjects_books(arg)
        elif action == "similar":
            show_similar_books(arg)
        else:
            print("⚠️  Unknown command.")


if __name__ == "__main__":
    main()
