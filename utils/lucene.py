import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, Term
from org.apache.lucene.search import (
    IndexSearcher, BooleanQuery, BooleanClause, TermQuery, PhraseQuery, TermRangeQuery
)
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser

from datetime import datetime

class LuceneIndexer:
    FIELD_GROUPS = {
        "all": [
            "title", "author", "description", "genre", "language",
            "publisher", "series", "subjects_people", "subjects_places", "authors"
        ],
        "title": ["title", "description", "genre", "language", "publisher"],
        "author": ["author", "authors_processed"],
        "language": ["language"],
        "date_published": ["date_published"],
        "publisher": ["publisher"],
        "subjects": ["subjects_people", "subjects_places"],
    }

    def __init__(self, index_dir="books_index", similarity="bm25"):
        lucene.initVM()

        self.directory = FSDirectory.open(Paths.get(index_dir))
        self.analyzer = StandardAnalyzer()
        cfg = IndexWriterConfig(self.analyzer)

        cfg.setSimilarity(BM25Similarity())

        self.writer = IndexWriter(self.directory, cfg)

    @staticmethod
    def parse_date(date_str):
        if not date_str or date_str.upper() in ["N/A", "NA"]:
            return None
        for fmt in ("%B %d, %Y", "%B %Y", "%Y"):
            try:
                dt = datetime.strptime(date_str, fmt)
                # default to January 1 if something is missing
                return dt.strftime("%Y%m%d")
            except ValueError:
                continue
        return None

    # For handling complex author dictionary field
    def _extract_field_value(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            extracted = []
            for item in value:
                if isinstance(item, dict):
                    extracted.extend(str(v) for v in item.values() if v is not None)
                else:
                    extracted.append(str(item))
            return " ".join(extracted)
        elif isinstance(value, dict):
            return " ".join(str(v) for v in value.values() if v is not None)
        else:
            return str(value) if value is not None else ""


    def add_book(self, book):
        doc = Document()

        doc.add(StringField("id", str(book["id"]), Field.Store.YES))

        for key, value in book.items():
            # Handling json
            if key == "authors":
                doc.add(TextField("authors_processed", str(self._extract_field_value(book.get("authors", ""))), Field.Store.YES))
                # Store for retrieval
                doc.add(TextField("authors", str(book.get("authors", "")), Field.Store.YES))
                continue;

            if key != "id":
                doc.add(TextField(key, str(value), Field.Store.YES))


        self.writer.updateDocument(Term("id", str(book["id"])), doc)

    def commit(self):
        self.writer.commit()

    # def _parse_query(self, query, fields):
    #     if isinstance(fields, str):
    #         fields = [fields]

    #     tokens = []
    #     i = 0
    #     while i < len(query):
    #         if i < len(query) and query[i] == '"':
    #             j = query.find('"', i + 1)
    #             if j == -1:
    #                 j = len(query)
    #             phrase = query[i + 1:j]
    #             if phrase:
    #                 tokens.append(("PHRASE", phrase))
    #             i = j + 1
    #         elif not query[i].isspace():
    #             j = i
    #             while j < len(query) and not query[j].isspace() and query[j] != '"':
    #                 j += 1
    #             word = query[i:j]
    #             if word:
    #                 tokens.append(("WORD", word))
    #             i = j
    #         else:
    #             i += 1
    #     # If single field, just return that query
    #     if len(fields) == 1:
    #         return self.build_single_field_query(fields[0], tokens)

    #     # For multiple fields: (field1_query) OR (field2_query) OR ...
    #     multi_field_builder = BooleanQuery.Builder()
    #     multi_field_builder.setMinimumNumberShouldMatch(1)
    #     for field in fields:
    #         field_query = self.build_single_field_query(field, tokens)
    #         multi_field_builder.add(field_query, BooleanClause.Occur.SHOULD)

    #     return multi_field_builder.build()


    def _parse_query(self, query_text, fields):
        if isinstance(fields, str):
            fields = [fields]

        try:
            flags = [BooleanClause.Occur.SHOULD] * len(fields)
            return MultiFieldQueryParser.parse(query_text, fields, flags, self.analyzer)
        except Exception as e:
            print(f"Query parsing error: {e}")
            return None

    # def build_single_field_query(self, field, tokens):
    #     b = BooleanQuery.Builder()
    #     current_op = "OR"

    #     for ttype, val in tokens:
    #         if val.upper() in ["AND", "OR", "NOT"]:
    #             current_op = val.upper()
    #             continue

    #         if ttype == "PHRASE":
    #             phrase_builder = PhraseQuery.Builder()
    #             for word in val.lower().split():
    #                 phrase_builder.add(Term(field, word))
    #             q = phrase_builder.build()
    #         else:
    #             q = TermQuery(Term(field, val.lower()))

    #         if current_op == "AND":
    #             b.add(q, BooleanClause.Occur.MUST)
    #         elif current_op == "NOT":
    #             b.add(q, BooleanClause.Occur.MUST_NOT)
    #         else:
    #             b.add(q, BooleanClause.Occur.SHOULD)

    #     return b.build()

    def search_by_date_range(self, start_date=None, end_date=None, query_text=None, index_name="all", top_n=5):
        reader = DirectoryReader.open(self.directory)
        searcher = IndexSearcher(reader)
        start = start_date if start_date else "00000101"
        end = end_date if end_date else "99991231"

        date_query = TermRangeQuery.newStringRange("date_published", start, end, True, True)

        search_field = self.FIELD_GROUPS[index_name]
        if query_text:
            text_query = self._parse_query(query_text, search_field)
            b = BooleanQuery.Builder()
            b.add(date_query, BooleanClause.Occur.MUST)
            b.add(text_query, BooleanClause.Occur.MUST)
            final_query = b.build()
        else:
            final_query = date_query

        results = searcher.search(final_query, top_n)
        out = []
        for sd in results.scoreDocs:
            doc = searcher.storedFields().document(sd.doc)
            book_data = {"score": sd.score, "book": {}}
            for field in doc.getFields():
                field_name = field.name()
                field_value = doc.get(field_name)
                clean_name = field_name.replace("raw_", "") if field_name.startswith("raw_") else field_name

                if clean_name == "authors":
                    book_data["book"][clean_name] = eval(field_value)
                else:
                    book_data["book"][clean_name] = field_value

            out.append(book_data)

        return out


    def search(self, query, index_name="all", top_n=5):
        search_field = self.FIELD_GROUPS[index_name]

        reader = DirectoryReader.open(self.directory)
        searcher = IndexSearcher(reader)

        lucene_query = self._parse_query(query, search_field)
        print(lucene_query);
        results = searcher.search(lucene_query, top_n)

        out = []
        for sd in results.scoreDocs:
            doc = searcher.storedFields().document(sd.doc)
            book_data = {"score": sd.score, "book": {}}
            for field in doc.getFields():
                field_name = field.name()
                field_value = doc.get(field_name)
                clean_name = field_name.replace("raw_", "") if field_name.startswith("raw_") else field_name


                if clean_name == "authors":
                     book_data["book"][clean_name] = eval(field_value) # this is a JSON Object
                else:
                    book_data["book"][clean_name] = field_value

            out.append(book_data)

        return out
