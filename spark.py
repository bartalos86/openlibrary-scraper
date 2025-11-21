import os
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, explode, split, to_json, trim, collect_list, struct, broadcast, when
)
from pyspark.sql.types import StructType, StructField, StringType
from datetime import datetime
from utils.file import sanitize_value

AUTHOR_REGEX = {
    "born": r"\|\s*(?:birth_date|born)\s*=\s*(.+)",
    "died": r"\|\s*(?:death_date|died)\s*=\s*(.+)",
    "occupation": r"\|\s*occupation\s*=\s*(.+)",
    "nationality": r"\|\s*nationality\s*=\s*(.+)",
    "alma_mater": r"\|\s*alma_mater\s*=\s*(.+)",
    "notable_works": r"\|\s*(?:notableworks|notable_works)\s*=\s*(.+)",
    "awards": r"\|\s*(?:awards|notable_awards)\s*=\s*(.+)",
    "spouse": r"\|\s*spouse\s*=\s*(.+)",
    "pseudonym": r"\|\s*pseudonym\s*=\s*(.+)",
    "birth_place": r"\|\s*birth_place\s*=\s*(.+)",
    "death_place": r"\|\s*death_place\s*=\s*(.+)",
}

PUBLISHER_REGEX = {
    "name": r"\|\s*(?:name|publisher)\s*=\s*(.+)",
    "parent": r"\|\s*parent\s*=\s*(.+)",
    "status": r"\|\s*status\s*=\s*(.+)",
    "founded": r"\|\s*founded\s*=\s*(.+)",
    "founders": r"\|\s*founders\s*=\s*(.+)",
    "successor": r"\|\s*successor\s*=\s*(.+)",
    "country": r"\|\s*country\s*=\s*(.+)",
    "headquarters": r"\|\s*headquarters\s*=\s*(.+)",
    "distribution": r"\|\s*distribution\s*=\s*(.+)",
    "keypeople": r"\|\s*keypeople\s*=\s*(.+)",
    "publications": r"\|\s*publications\s*=\s*(.+)",
    "topics": r"\|\s*topics\s*=\s*(.+)",
    "genre": r"\|\s*genre\s*=\s*(.+)",
    "imprints": r"\|\s*imprints\s*=\s*(.+)",
    "url": r"\|\s*url\s*=\s*(.+)",
}

def sanitize_wiki_value(value: str) -> str:
    if not value or not isinstance(value, str):
        return "N/A"

    v = value

    # Remove references and templates
    v = re.sub(r"<ref[^>]*>.*?</ref>", "", v)
    v = re.sub(r"\{\{.*?\}\}", "", v)
    v = re.sub(r"\[\[|\]\]", "", v)

    # Handle LaTeX and wiki formatting
    v = re.sub(r"\\textbf\{([^}]*)\}", r"\1", v)
    v = re.sub(r"'''([^']*)'''", r"\1", v)
    v = re.sub(r"''([^']*)''", r"\1", v)

    # Replace wiki-style lists
    v = re.sub(r"(?m)^\*+\s*", "- ", v)
    v = re.sub(r"{{plainlist\|", "", v)
    v = re.sub(r"{{flatlist\|", "", v)
    v = re.sub(r"}}", "", v)

    v = re.sub(r"&[a-z]+;", " ", v)
    v = re.sub(r"<.*?>", "", v)
    v = re.sub(r"\s+", " ", v).strip()

    v = re.sub(r"\\br|<br\s*/?>", ", ", v)
    v = re.sub(r"(?m)^\*+\s*", "- ", v)
    v = re.sub(r"\s*,\s*,+", ", ", v)
    v = re.sub(r"\s+", " ", v).strip()


    v = v.strip("|[]{} ")

    return v if v else "N/A"


page_regex = re.compile(r"<page>(.*?)</page>", re.S)
title_regex = re.compile(r"<title>(.*?)</title>", re.S)



def extract_fields(text: str, regex_list):
    """Extract infobox fields for a single Wikipedia author page."""
    info = {}

    for key, pattern in regex_list.items():
        match = re.search(pattern, text)
        if not match:
            info[key] = None
            continue

        raw_value = match.group(1)
        clean_val = sanitize_wiki_value(raw_value)

        # Date template normalization
        date_match = re.search(r"(\d{3,4})\|(\d{1,2})\|(\d{1,2})", raw_value)
        if date_match:
            try:
                clean_val = datetime.strptime(
                    f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}",
                    "%Y-%m-%d"
                ).strftime("%Y-%m-%d")
            except ValueError:
                clean_val = raw_value.replace("|", "-")

        info[key] = clean_val

    return info

def extract_author_info(xml_chunk, authors):
    results = []
    for page in page_regex.findall(xml_chunk):
        title_match = title_regex.search(page)
        if not title_match:
            continue

        title = title_match.group(1).strip()
        if title not in authors:
            continue

        infobox_match = re.search(r"\{\{Infobox[^\n]*?[^\n]*?([\s\S]*?)\}\}\s*\n", page, re.S | re.I)
        infobox_text = infobox_match.group(1) if infobox_match else page

        fields = extract_fields(infobox_text, AUTHOR_REGEX)

        extracted = {"title": title}
        extracted.update(fields)

        results.append(tuple(extracted[k] for k in ["title"] + list(AUTHOR_REGEX.keys())))

    return results

def extract_publisher_info(xml_chunk, publishers):
    results = []
    for page in page_regex.findall(xml_chunk):
        title_match = title_regex.search(page)
        if not title_match:
            continue

        title = title_match.group(1).strip()
        if title not in publishers:
            continue

        infobox_match = re.search(r"\{\{Infobox[^\n]*?(publisher)[^\n]*?([\s\S]*?)\}\}\s*\n", page, re.S | re.I)
        infobox_text = infobox_match.group(1) if infobox_match else page

        fields = extract_fields(infobox_text, PUBLISHER_REGEX)

        extracted = {"title": title}
        extracted.update(fields)

        results.append(tuple(extracted[k] for k in ["title"] + list(PUBLISHER_REGEX.keys())))

    return results


def chunk_stream(iterator, max_pages=500):
    buffer, count = [], 0
    for line in iterator:
        buffer.append(line)
        if "</page>" in line:
            count += 1
        if count >= max_pages:
            yield "\n".join(buffer)
            buffer, count = [], 0
    if buffer:
        yield "\n".join(buffer)


def load_if_exists(spark: SparkSession, path: str):
    if os.path.exists(path):
        print(f"✅ Found existing parquet at {path}, loading...")
        return spark.read.parquet(path)
    else:
        print(f"⚠️ No parquet found at {path}.")
        return None



def process_books(books_df, spark):
    sc = spark.sparkContext

    joined_df = load_if_exists(spark, "data/processed_books/")
    if joined_df is not None:
        print("✅ Loaded existing processed dataset.")
        return joined_df

    print("ℹ️ No saved dataset found. Starting fresh processing...")

    # unique author names
    authors = (
        books_df.select("author")
        .rdd.flatMap(lambda r: [a.strip() for a in r.author.split(",") if a.strip()])
        .distinct()
        .collect()
    )
    authors_bc = sc.broadcast(set(authors))
    print(f"✅ Loaded {len(authors)} unique authors")

    wiki_rdd = (
        sc.textFile("data/enwiki-20251001-pages-articles-multistream.xml.bz2", minPartitions=50)
        .mapPartitions(lambda it: chunk_stream(it, max_pages=300))
    )

    # Extract author info
    author_info_rdd = wiki_rdd.flatMap(lambda chunk: extract_author_info(chunk, authors_bc.value))

    columns = ["title"] + list(AUTHOR_REGEX.keys())
    schema = StructType([StructField(c, StringType(), True) for c in columns])
    authors_df = spark.createDataFrame(author_info_rdd, schema).cache()

    print(f"✅ Extracted {authors_df.count()} author entries from Wikipedia dump")

    authors_df = authors_df.withColumnRenamed("title", "author_title")

    # Explode multiple authors
    books_exploded = (
        books_df
        .withColumn("author_name", explode(split(col("author"), ",")))
        .withColumn("author_name", trim(col("author_name")))
    )

    joined = (
        books_exploded
        .join(broadcast(authors_df),
              books_exploded.author_name == authors_df.author_title,
              "left")
        .withColumn(
            "has_info",
            when(
                col("born").isNotNull() | col("birth_place").isNotNull()  | col("birth_place").isNotNull() | col("died").isNotNull() | col("occupation").isNotNull() | col("nationality").isNotNull(),
                True
            ).otherwise(False)
        )
        # .filter(col("has_info"))
        .groupBy(*books_df.columns)
        .agg(
            collect_list(
                struct(
                    col("author_name"),
                    col("born"),
                    col("birth_place"),
                    col("died"),
                    col("occupation"),
                    col("nationality"),
                    col("notable_works"),
                    col("awards"),
                    col("spouse")
                )
            ).alias("authors")
        )
    )

    # Cache saving
    output_path = "data/processed_books/"
    joined.write.mode("overwrite").parquet(output_path)

    print(f"joined: {joined.count()}")
    joined_flat = joined.withColumn("authors", to_json(col("authors")))

    joined_flat \
        .write \
        .option("header", True) \
        .option("sep", "\t") \
        .mode("overwrite") \
        .csv("data/processed_books/csv")
    print(f"✅ Saved processed dataset to {output_path}")

    return joined
