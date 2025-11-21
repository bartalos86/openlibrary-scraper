from pyspark.sql import SparkSession
from pyspark.sql import Row
import os
from utils.file import sanitize_value
from utils.metadata import extract_book_page_metadata

def extract_from_file(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                page_source = f.read()
            book_data = extract_book_page_metadata(page_source, log=False)

            sanitized_data = {k: sanitize_value(v) for k, v in book_data.items()}

            return Row(**sanitized_data)
        except Exception as e:
            return Row(error=str(e), file_path=file_path)

def extract_spark_tsv(html_folder: str, output_path: str):
    spark = SparkSession.builder \
        .appName("SparkMetadataProcessor") \
        .config("spark.driver.memory", "8g") \
        .getOrCreate()

    html_files = [
        os.path.join(html_folder, f)
        for f in os.listdir(html_folder)
        if (f.endswith(".html") or f.endswith(".htm")) and "_books_" in f
    ]

    rdd = spark.sparkContext.parallelize(html_files)

    metadata_rdd = rdd.map(extract_from_file)
    df = spark.createDataFrame(metadata_rdd)

    df = df.filter(df.title.isNotNull())
    df = df.dropDuplicates(["id"])

    df.coalesce(1).write \
        .option("header", True) \
        .option("delimiter", "\t") \
        .mode("overwrite") \
        .csv(output_path)

    print(f"✅ Extracted {df.count()} books from source files.")
    print(f"TSV output saved to: {output_path}")

    spark.stop()


extract_spark_tsv("page_sources", "spark_extracted")