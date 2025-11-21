import math
import re
from collections import defaultdict, Counter


class BookSearchEngine:
    def __init__(self, idf_mode = "standard"):
        """
        idf_mode: 'standard' (log(N/df)) or 'probabilistic' (BM25-style)
        """
        self.idf_mode = idf_mode
        self.documents = []
        self.indexes = {
             "all": defaultdict(set),
             "title": defaultdict(set),
             "author": defaultdict(set),
             "language": defaultdict(set),
             "publisher": defaultdict(set),
             "subjects": defaultdict(set),
         }

        # Document frequency per index
        self.doc_freqs = {
            "all": defaultdict(int),
            "title": defaultdict(int),
            "author": defaultdict(int),
            "language": defaultdict(int),
            "publisher": defaultdict(int),
            "subjects": defaultdict(int)
        }

        # TF-IDF vectors per index
        self.tfidf_vectors = {
            "all": [],
            "title": [],
            "author": [],
            "language": [],
            "publisher": [],
            "subjects": [],
        }

        self.position_indexes = {
            "all": defaultdict(lambda: defaultdict(list)),
            "title": defaultdict(lambda: defaultdict(list)),
            "author": defaultdict(lambda: defaultdict(list)),
            "language": defaultdict(lambda: defaultdict(list)),
            "publisher": defaultdict(lambda: defaultdict(list)),
            "subjects": defaultdict(lambda: defaultdict(list)),
        }
        self.field_groups = {
            "title": ["title", "description", "genre", "language", "publisher"],
            "author": ["author", "authors"],
            "language": ["language"],
            "publisher": ["publisher"],
            "subjects": ["subjects_people", "subjects_places"],
            "all": ["title", "author", "genre", "publisher", "language",
                   "description", "series", "subjects_people", "subjects_places"]
        }
        self.N = 0

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
        """
        Adds a book and indexes it in all specialized indexes.
        """
        book_id = book.get("id") or self.N

        self.documents.append((book_id, book))

        # Index in each specialized index
        for index_name, fields in self.field_groups.items():
            combined_text = " ".join(self._extract_field_value(book.get(f, "")) for f in fields)
            self._index_text(book_id, combined_text, index_name)

        self.N += 1

    def _index_text(self, doc_id, text, index_name):
      """Index text in a specific index."""
      terms = self._tokenize(text)
      unique_terms = set(terms)
      for term in unique_terms:
          self.indexes[index_name][term].add(doc_id)
          self.doc_freqs[index_name][term] += 1
      #Positional index for phrase searching
      for pos, term in enumerate(terms):
          self.position_indexes[index_name][term][doc_id].append(pos)

    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def build_tfidf(self):
      """Build TF–IDF vectors for all documents in all indexes."""
      for index_name in self.indexes.keys():
          self.tfidf_vectors[index_name] = []
          for doc_id, (_, book) in enumerate(self.documents):
              if index_name == "all":
                  combined_text = " ".join([
                      str(v) for v in book.values() if isinstance(v, str)
                  ])
              elif index_name == "subjects":
                  combined_text = " ".join([
                      str(book.get(k, "")) for k in self.field_groups["subjects"]
                  ])
              elif index_name == "title":
                  combined_text = " ".join([
                      str(book.get(k, "")) for k in self.field_groups["title"]
                  ])
              elif index_name == "author":
                  combined_text = str(book.get("author", ""))
              elif index_name == "language":
                  combined_text = str(book.get("language", ""))
              elif index_name == "description":
                  combined_text = str(book.get("description", ""))
              elif index_name == "publisher":
                  combined_text = str(book.get("publisher", ""))
              counts = Counter(self._tokenize(combined_text))
              vec = {}
              for term, tf in counts.items():
                  idf = self._idf(term, index_name)
                  vec[term] = (1 + math.log10(tf)) * idf
              self.tfidf_vectors[index_name].append(vec)

    def _idf(self, term, index_name = "all"):
        """Calculate IDF for a term in a specific index."""
        df = self.doc_freqs[index_name].get(term, 0)
        if df == 0:
            return 0.0
        if self.idf_mode == "probabilistic":
            return math.log10((self.N - df + 0.5) / (df + 0.5))
        else:
            return math.log10(self.N / df)

    def _cosine_similarity(self, v1, v2):
        common = set(v1.keys()) & set(v2.keys())
        num = sum(v1[t] * v2[t] for t in common)
        den1 = math.sqrt(sum(v**2 for v in v1.values()))
        den2 = math.sqrt(sum(v**2 for v in v2.values()))
        return num / (den1 * den2) if den1 and den2 else 0.0

    def _parse_boolean_query(self, query):
        """
        Parse boolean query into tokens
        """
        # Extract quoted phrases first
        phrases = re.findall(r'"([^"]+)"', query)
        phrase_placeholders = {}

        for i, phrase in enumerate(phrases):
            placeholder = f"__PHRASE_{i}__"
            phrase_placeholders[placeholder] = phrase
            query = query.replace(f'"{phrase}"', placeholder)

        # Tokenize, preserving parentheses as separate tokens
        tokens = []
        current_token = ""
        for char in query:
            if char in "()":
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
                tokens.append(char)
            elif char.isspace():
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
            else:
                current_token += char
        if current_token.strip():
            tokens.append(current_token.strip())

        # Replace placeholders back and categorize tokens
        result = []
        for token in tokens:
            if token in phrase_placeholders:
                result.append(("PHRASE", phrase_placeholders[token]))
            elif token.upper() in ["AND", "OR", "NOT"]:
                result.append(("OP", token.upper()))
            elif token in ["(", ")"]:
                result.append(("PAREN", token))
            else:
                result.append(("TERM", token))

        return result

    def _phrase_search(self, phrase: str, index_name: str = "all"):
        """Find documents containing exact phrase in a specific index."""
        terms = self._tokenize(phrase)
        if not terms:
            return set()

        position_index = self.position_indexes[index_name]

        # Start with docs containing first term
        result_docs = set(position_index[terms[0]].keys())

        # Check each document for consecutive terms
        valid_docs = set()
        for doc_id in result_docs:
            positions_first = position_index[terms[0]][doc_id]

            for start_pos in positions_first:
                # Check if all subsequent terms appear at consecutive positions
                found = True
                for i, term in enumerate(terms[1:], 1):
                    expected_pos = start_pos + i
                    if expected_pos not in position_index[term].get(doc_id, []):
                        found = False
                        break

                if found:
                    valid_docs.add(doc_id)
                    break

        return valid_docs

    def _evaluate_boolean_expression(self, tokens, index, index_name):
        """
        Recursively evaluate boolean expression.
        Returns (result_set, next_position)
        """
        result_set = None
        current_op = "OR"
        i = 0

        while i < len(tokens):
            token_type, token_value = tokens[i]

            if token_type == "OP":
                current_op = token_value
                i += 1
                continue

            # Handle opening parenthesis, recursively evaluate subexpression
            if token_type == "PAREN" and token_value == "(":
                # Find matching closing parenthesis
                paren_count = 1
                j = i + 1
                while j < len(tokens) and paren_count > 0:
                    if tokens[j][0] == "PAREN":
                        if tokens[j][1] == "(":
                            paren_count += 1
                        elif tokens[j][1] == ")":
                            paren_count -= 1
                    j += 1

                sub_tokens = tokens[i+1:j-1]
                current_set, _ = self._evaluate_boolean_expression(sub_tokens, index, index_name)
                i = j

                if result_set is None:
                    result_set = current_set
                elif current_op == "AND":
                    result_set = result_set & current_set
                elif current_op == "OR":
                    result_set = result_set | current_set
                elif current_op == "NOT":
                    result_set = result_set - current_set
                continue

            # Handle closing parenthesis
            elif token_type == "PAREN" and token_value == ")":
                break

            elif token_type == "PHRASE":
                current_set = self._phrase_search(token_value, index_name)
                i += 1
            elif token_type == "TERM":
                term = token_value.lower()
                current_set = index.get(term, set())
                i += 1
            else:
                i += 1
                continue

            if result_set is None:
                result_set = current_set
            elif current_op == "AND":
                result_set = result_set & current_set
            elif current_op == "OR":
                result_set = result_set | current_set
            elif current_op == "NOT":
                result_set = result_set - current_set

        return result_set, i

    def boolean_search(self, query: str, top_n=5, index_name: str = "all"):
        """
        Boolean search. Supported operators:  AND, OR, NOT, phrases, and grouping.
        """
        tokens = self._parse_boolean_query(query)

        if not tokens:
            return []

        index = self.indexes[index_name]

        result_set, _ = self._evaluate_boolean_expression(tokens, index, index_name)

        # NOT as first expression
        if tokens and tokens[0][0] == "OP" and tokens[0][1] == "NOT":
            all_docs = set(bid for bid, _ in self.documents)
            result_set = all_docs - (result_set or set())

        if not result_set:
            return []

        scores = []
        query_terms = self._tokenize(query)
        q_counts = Counter(query_terms)
        q_vec = {}
        for term, tf in q_counts.items():
            idf = self._idf(term, index_name)
            q_vec[term] = (1 + math.log10(tf)) * idf

        for doc_id, (book_id, book) in enumerate(self.documents):
            if book_id in result_set:
                score = self._cosine_similarity(q_vec, self.tfidf_vectors[index_name][doc_id])
                scores.append({"book": book, "score": score if score > 0 else 0.1})

        scores.sort(key=lambda x: x[-1], reverse=True)
        return scores[:top_n]

    def search(self, query: str, top_n=5, use_boolean=False, index_name: str = "all"):
        """
        Search for a query.
        """
        if use_boolean or any(op in query.upper() for op in [" AND ", " OR ", " NOT "]):
            return self.boolean_search(query, top_n, index_name)

        query_terms = self._tokenize(query)
        q_counts = Counter(query_terms)
        q_vec = {}
        for term, tf in q_counts.items():
            idf = self._idf(term, index_name)
            q_vec[term] = (1 + math.log10(tf)) * idf

        scores = []
        for doc_id, (book_id, book) in enumerate(self.documents):
            score = self._cosine_similarity(q_vec, self.tfidf_vectors[index_name][doc_id])
            if score > 0:
                scores.append({"book": book, "score": score})

        scores.sort(key=lambda x: x[-1], reverse=True)
        return scores[:top_n]
