import unittest
import os
import sys
import csv
from typing import Dict, Any
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.file import sanitize_value
from utils.metadata import (
    safe_find_property,
    safe_find_multiple_properties,
    extract_book_page_metadata
)


class TestRegexPatterns(unittest.TestCase):
    """Test class for individual regex patterns"""

    @classmethod
    def setUpClass(cls):
        """Load all html test files and expected results from tsv"""
        cls.test_data = {}
        cls.expected_results = {}
        cls.maxDiff = None

        test_dir = os.path.dirname(os.path.abspath(__file__))

        # Load expected results from tsv file
        tsv_path = os.path.join(test_dir, "expected_results.tsv")
        try:
            with open(tsv_path, 'r', encoding='utf-8') as tsvfile:
                reader = csv.DictReader(tsvfile, delimiter='\t', skipinitialspace=False, dialect='excel', quoting=csv.QUOTE_NONE, quotechar='\\')
                for idx, row in enumerate(reader, start=1):
                    filename = f"book{idx}.html"
                    cls.expected_results[filename] = row
                    print(f"Loaded expected results for {filename}: {row.get('title', 'N/A')[:50]}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Expected results file not found: {tsv_path}")

        # Load HTML files
        html_dir = os.path.join(test_dir, "test_html")
        for filename in cls.expected_results.keys():
            filepath = os.path.join(html_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cls.test_data[filename] = f.read()
                    print(f"Loaded HTML file: {filepath}")
            except FileNotFoundError:
                print(f"Warning: {filepath} not found. Tests will be skipped for this file.")
                cls.test_data[filename] = None

        print(f"\nTotal files loaded: {len([v for v in cls.test_data.values() if v])}/{len(cls.expected_results)}")

    def _normalize_value(self, value: str) -> str:
        """Normalize values for comparison (handle empty strings, whitespace, \t, \n.)"""
        if value is None or value == "" or value.strip() == "":
            return "N/A"
        return sanitize_value(value)

    def _test_regex(self, filename: str, field: str, pattern: str, group: int = 1, is_multiple: bool = False):
        """Test for each individual method"""
        if self.test_data.get(filename) is None:
            self.skipTest(f"{filename} not found")

        if filename not in self.expected_results:
            self.skipTest(f"No expected results for {filename}")

        expected = self._normalize_value(self.expected_results[filename].get(field, "N/A"))

        if is_multiple:
            actual = safe_find_multiple_properties(self.test_data[filename], pattern, group)
        else:
            actual = safe_find_property(self.test_data[filename], pattern, group)

        actual = self._normalize_value(actual)

        self.assertEqual(
            actual,
            expected,
            f"\n{'='*80}\n"
            f"Regex test failed for field '{field}' in {filename}\n"
            f"Expected: '{expected}'\n"
            f"Actual:   '{actual}'\n"
            f"Pattern:  {pattern[:100]}...\n"
            f"{'='*80}"
        )

    def _test_all_files(self, field: str, pattern: str, group: int = 1, is_multiple: bool = False):
        """Test a regex pattern across all HTML files"""
        for filename in self.expected_results.keys():
            with self.subTest(file=filename, field=field):
                self._test_regex(filename, field, pattern, group, is_multiple)

    # Test regex patterns
    def test_regex_id(self):
        """Test ID extraction regex: name="edition_id" value="/books/([^"]+)" """
        pattern = r'name="edition_id"\s+value="/books/([^"]+)"'
        self._test_all_files("id", pattern)

    def test_regex_title(self):
        """Test title extraction regex: <h1[^>]*class="[^"]*work-title[^"]*"[^>]*>(.*?)</h1>"""
        pattern = r'<h1[^>]*class="[^"]*work-title[^"]*"[^>]*>(.*?)</h1>'
        self._test_all_files("title", pattern)

    def test_regex_cover_url(self):
        """Test cover URL extraction regex: <meta property="og:image" content="([^"]+)" """
        pattern = r'<meta property="og:image" content="([^"]+)"'
        self._test_all_files("cover_url", pattern)

    def test_regex_author(self):
        """Test author extraction regex (multiple): <a[^>]*itemprop=["\']author["\'][^>]*>(.*?)</a>"""
        pattern = r'<a[^>]*itemprop=["\']author["\'][^>]*>(.*?)</a>'
        self._test_all_files("author", pattern, is_multiple=True)

    def test_regex_rating(self):
        """Test rating extraction regex: <span[^>]*itemprop=["\']ratingValue["\'][^>]*>(.*?)</span>"""
        pattern = r'<span[^>]*itemprop=["\']ratingValue["\'][^>]*>(.*?)</span>'
        self._test_all_files("rating", pattern)

    def test_regex_date_published(self):
        """Test date published extraction regex: <span[^>]*itemprop=["\']datePublished["\'][^>]*>(.*?)</span>"""
        pattern = r'<span[^>]*itemprop=["\']datePublished["\'][^>]*>(.*?)</span>'
        self._test_all_files("date_published", pattern)

    def test_regex_publisher(self):
        """Test publisher extraction regex: <a[^>]*itemprop=["\']publisher["\'][^>]*>(.*?)</a>"""
        pattern = r'<a[^>]*itemprop=["\']publisher["\'][^>]*>(.*?)</a>'
        self._test_all_files("publisher", pattern)

    def test_regex_language(self):
        """Test language extraction regex: <span[^>]*itemprop=["\']inLanguage["\'][^>]*>.*?<a[^>]*>(.*?)</a>"""
        pattern = r'<span[^>]*itemprop=["\']inLanguage["\'][^>]*>.*?<a[^>]*>(.*?)</a>'
        self._test_all_files("language", pattern)

    def test_regex_pages(self):
        """Test pages extraction regex: <a[^>]*itemprop=["\']numberOfPages["\'][^>]*>(.*?)</a>"""
        pattern = r'<a[^>]*itemprop=["\']numberOfPages["\'][^>]*>(.*?)</a>'
        self._test_all_files("pages", pattern)

    def test_regex_description(self):
        """Test description extraction regex: <div[^>]*class=["\']read-more__content["\'][^>]*>(.*?)</div>"""
        pattern = r'<div[^>]*class=["\']read-more__content["\'][^>]*>(.*?)</div>'

        for filename in self.expected_results.keys():
            with self.subTest(file=filename):
                if self.test_data.get(filename) is None:
                    self.skipTest(f"{filename} not found")

                match = re.search(pattern, self.test_data[filename], re.IGNORECASE | re.DOTALL)
                if match:
                    raw_desc = match.group(1).strip()
                    clean_desc = self._normalize_value(re.sub(r'<.*?>', '', raw_desc).strip())
                    actual = clean_desc if clean_desc else "N/A"
                else:
                    actual = "N/A"

                expected = self._normalize_value(self.expected_results[filename].get("description", "N/A"))

                self.assertEqual(actual, expected,
                    f"Description mismatch in {filename}\nExpected: {expected[:100]}\nActual: {actual[:100]}")

    def test_regex_published_in(self):
        """Test published_in extraction regex: <dt[^>]*>Published in</dt>\s*<dd[^>]*>(.*?)</dd>"""
        pattern = r'<dt[^>]*>Published in<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'
        self._test_all_files("published_in", pattern)

    def test_regex_series(self):
        """Test series extraction regex: <dt[^>]*>Series</dt>\s*<dd[^>]*>(.*?)</dd>"""
        pattern = r'<dt[^>]*>Series<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'
        self._test_all_files("series", pattern)

    def test_regex_genre(self):
        """Test genre extraction regex: <dt[^>]*>Genre</dt>\s*<dd[^>]*>(.*?)</dd>"""
        pattern = r'<dt[^>]*>Genre<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'
        self._test_all_files("genre", pattern)

    def test_regex_isbn10(self):
        """Test ISBN-10 extraction regex: <dt[^>]*>ISBN 10</dt>\s*<dd[^>]*>(.*?)</dd>"""
        pattern = r'<dt[^>]*>ISBN 10<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'
        self._test_all_files("isbn10", pattern)

    def test_regex_isbn13(self):
        """Test ISBN-13 extraction regex: <dt[^>]*>ISBN 13</dt>\s*<dd[^>]*>(.*?)</dd>"""
        pattern = r'<dt[^>]*>ISBN 13<\/dt>\s*<dd[^>]*>(.*?)<\/dd>'
        self._test_all_files("isbn13", pattern)

    def test_regex_goodreads_url(self):
        """Test Goodreads URL extraction regex: <dt[^>]*>Goodreads</dt>.*?<a[^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<dt[^>]*>Goodreads<\/dt>.*?<a[^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("goodreads_url", pattern)

    def test_regex_download_pdf_url(self):
        """Test PDF download URL regex: <a[^>]*data-ol-link-track=["\']Download\|pdf_ia["\'][^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<a[^>]*data-ol-link-track=["\']Download\|pdf_ia["\'][^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("download_pdf_url", pattern)

    def test_regex_download_epub_url(self):
        """Test EPUB download URL regex: <a[^>]*data-ol-link-track=["\']Download\|epub_ia["\'][^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<a[^>]*data-ol-link-track=["\']Download\|epub_ia["\'][^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("download_epub_url", pattern)

    def test_regex_download_text_url(self):
        """Test text download URL regex: <a[^>]*data-ol-link-track=["\']Download\|text_ia["\'][^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<a[^>]*data-ol-link-track=["\']Download\|text_ia["\'][^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("download_text_url", pattern)

    def test_regex_download_mobi_url(self):
        """Test MOBI download URL regex: <a[^>]*data-ol-link-track=["\']Download\|mobi_ia["\'][^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<a[^>]*data-ol-link-track=["\']Download\|mobi_ia["\'][^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("download_mobi_url", pattern)

    def test_regex_download_daisy_url(self):
        """Test DAISY download URL regex: <a[^>]*data-ol-link-track=["\']Download\|daisy_ia["\'][^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<a[^>]*data-ol-link-track=["\']Download\|daisy_ia["\'][^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("download_daisy_url", pattern)

    def test_regex_worldcat_rent_url(self):
        """Test WorldCat URL regex: <a[^>]*class=["\']worldcat-link["\'][^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<a[^>]*class=["\']worldcat-link["\'][^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("worldcat_rent_url", pattern)

    def test_regex_betterworldbooks_url(self):
        """Test Better World Books URL regex: <li[^>]*class=["\']prices-betterworldbooks["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<li[^>]*class=["\']prices-betterworldbooks["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("betterworldbooks_url", pattern)

    def test_regex_amazon_url(self):
        """Test Amazon URL regex: <li[^>]*class=["\']prices-amazon["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<li[^>]*class=["\']prices-amazon["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("amazon_url", pattern)

    def test_regex_bookshop_url(self):
        """Test Bookshop.org URL regex: <li[^>]*class=["\']prices-bookshop-org["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']"""
        pattern = r'<li[^>]*class=["\']prices-bookshop-org["\'][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\']'
        self._test_all_files("bookshop_url", pattern)

    def test_regex_download_mp3_url(self):
        """Test MP3 download URL regex: href=["\'](https?://[^"\']*?mp3\.zip)["\']"""
        pattern = r'href=["\'](https?://[^"\']*?mp3\.zip)["\']'
        self._test_all_files("download_mp3_url", pattern)

    def test_regex_subjects_people(self):
        """Test subjects people extraction regex (multiple): <a href="/subjects/person:[^"]+"[^>]*>([^<]+)</a>"""
        pattern = r'<a href="/subjects/person:[^"]+"[^>]*>([^<]+)</a>'
        self._test_all_files("subjects_people", pattern, is_multiple=True)

    def test_regex_subjects_places(self):
        """Test subjects places extraction regex (multiple): <a href="/subjects/place:[^"]+"[^>]*>([^<]+)</a>"""
        pattern = r'<a href="/subjects/place:[^"]+"[^>]*>([^<]+)</a>'
        self._test_all_files("subjects_places", pattern, is_multiple=True)


    def test_complete_metadata_extraction(self):
        """Test that extract_book_page_metadata() function"""
        for filename in self.expected_results.keys():
            with self.subTest(file=filename):
                if self.test_data.get(filename) is None:
                    self.skipTest(f"{filename} not found")

                result = extract_book_page_metadata(self.test_data[filename])
                expected = self.expected_results[filename]

                mismatches = []
                for field in expected.keys():
                    expected_val = self._normalize_value(expected[field])
                    actual_val = self._normalize_value(result.get(field, "N/A"))
                    if expected_val != actual_val:
                        mismatches.append(
                            f"  {field}:\n    Expected: '{expected_val}'\n    Actual:   '{actual_val}'"
                        )

                if mismatches:
                    self.fail(
                        f"\n{'='*80}\n"
                        f"Mismatches in {filename}:\n" +
                        "\n".join(mismatches) +
                        f"\n{'='*80}"
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)