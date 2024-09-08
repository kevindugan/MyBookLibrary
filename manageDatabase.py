#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import dotenv_values
from sqlalchemy import create_engine, URL, select
from sqlalchemy.orm import sessionmaker
from csv import DictWriter, DictReader
from base64 import b64encode, b64decode
from os.path import splitext
from models import Base, CategoriesTB, BooksTB
from uuid import uuid4
from re import compile, fullmatch
from pathlib import Path

config = dotenv_values(".env")

def init_db(host):
    """Initialize the database from defined models"""
    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=True)
    Base.metadata.create_all(engine)
    
def drop_db_tables(host):
    """Drop all tables from defined models"""
    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def ingest_db(host, filename, type):
    if type == "categories":
        ingest_db_categories(host, filename)
    elif type == "books":
        ingest_db_books(host, filename)
    else:
        raise KeyError()

def ingest_db_categories(host, filename):
    """Ingest all category data from csv file"""
    # Collect any malformed values from csv
    with open(filename, "r") as infile:
        dict_reader = DictReader(infile)
        category_pattern = compile(r"[A-Z]{3}[0-9]{6}")
        malformed = {it["cat_id"] for it in dict_reader if category_pattern.fullmatch(it["cat_id"]) is None}

    # Read all values and construct table rows
    with open(filename, "r") as infile:
        dict_reader = DictReader(infile)
        rows = [CategoriesTB(
            cat_id=it["cat_id"],
            cat_path=it["cat_path"].replace(" / ", "|")
        ) for it in dict_reader if it["cat_id"] not in malformed]
        
    if len(malformed) > 0:
        message = ["The following entries are malformed and were not added:"] + malformed
        print("\n" + "\n    ".join(message) + "\n")

    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        session.add_all(rows)
        session.commit()

def ingest_db_books(host, filename: Path):
    """Ingest all book data from csv file
    
    cover art should be file path relative to csv file
    """
    # Construct Category Map
    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        res = session.execute(select(CategoriesTB.cat_id, CategoriesTB.id)).mappings().all()
        category_mapping = {it.cat_id.strip(): it.id for it in res}

    with open(filename, "r") as infile:
        dict_reader = DictReader(infile)
        row_data = [{
            "id": it["id"].strip() if it["id"].strip() != "" else str(uuid4()),
            "title": it["title"].strip(),
            "author": it["author"].strip(),
            "isbn": it["isbn"].strip() if it["isbn"].strip() != "" else None,
            "cover_art": image_to_b64( (filename.parent / it["cover_art"].strip()).absolute() ) if it["cover_art"].strip() != "" else None,
            "category": category_mapping[it["category"].strip()] if it["category"].strip() != "" else None
        } for it in dict_reader]

    with SessionLocal() as session:
        session.add_all([
            BooksTB(**it) for it in row_data
        ])
        session.commit()

def dump_db(host, dest: Path):
    from json import dumps
    if not dest.exists():
        dest.mkdir(parents=True)
    if any(dest.iterdir()):
        raise RuntimeError("Output directory must be empty")

    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        categories = [{
            "cat_id": it.CategoriesTB.cat_id,
            "cat_path": it.CategoriesTB.cat_path.replace("|", " / ")
        } for it in session.execute(select(CategoriesTB)).mappings().all()]
        
        with open(dest/"categories.csv", "w") as ofile:
            field_names = ["cat_id", "cat_path"]
            writer = DictWriter(ofile, fieldnames=field_names)
            
            writer.writeheader()
            [writer.writerow(it) for it in categories]
            
        book_query = (
            select(
                BooksTB.id,
                BooksTB.title,
                BooksTB.author,
                CategoriesTB.cat_id,
                BooksTB.isbn,
                BooksTB.cover_art)
            .join(CategoriesTB, BooksTB.category == CategoriesTB.id)
        )
        
        books = [{
            "id": str(it.id),
            "title": it.title,
            "author": it.author,
            "isbn": it.isbn,
            "category": it.cat_id,
            "cover_art": b64_to_image(it.cover_art, dest)
        } for it in session.execute(book_query).mappings().all()]

        with open(dest/"books.csv", "w") as ofile:
            field_names = ["id", "title", "author", "isbn", "category", "cover_art"]
            writer = DictWriter(ofile, fieldnames=field_names)
            
            writer.writeheader()
            [writer.writerow(it) for it in books]

def image_to_b64(filepath):
    cover_fc = open(filepath, "rb").read()
    b64_cover = b64encode(cover_fc).decode("utf-8")
    ext = splitext(filepath)[-1].replace('.','')
    return f"data:image/{ext};base64,{b64_cover}"

def b64_to_image(url, dest_dir: Path):
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)
    if not dest_dir.is_dir:
        raise RuntimeError("Must supply output directory")

    value = fullmatch(r"data:image/(?P<ext>[a-z]+);base64,(?P<encoding>.+)", url)
    ext = value.group("ext")
    enc = value.group("encoding")
    output_file = dest_dir / f"{uuid4()}.{ext}"
    with open(output_file, "wb") as outfile:
        outfile.write(b64decode(enc))
        
    return output_file.parts[-1]

def main():
    # Call the appropriate sub command with args
    func_name, func_args = parse_cli()
    func_name(**func_args)

def parse_cli():
    parser = ArgumentParser(description="Manage Database")
    subparser = parser.add_subparsers(title="Commands", metavar="")
    parser.add_argument("--host", dest="host", help="Host location", default="localhost", type=str)
    
    # Initialize DB Parser
    init_parser = subparser.add_parser("init", help="Initialize database", formatter_class=ArgumentDefaultsHelpFormatter)
    init_parser.set_defaults(func=init_db)

    # Drop Tables
    drop_parser = subparser.add_parser("drop", help="Drop database tables and reinitialize", formatter_class=ArgumentDefaultsHelpFormatter)
    drop_parser.set_defaults(func=drop_db_tables)
    
    # Ingest Data
    ingest_parser = subparser.add_parser("ingest", help="Ingest data from csv file", formatter_class=ArgumentDefaultsHelpFormatter)
    ingest_parser.add_argument("filename", help="Input file", type=Path)
    ingest_parser.add_argument("--type", help="Type of Data", choices=["categories", "books"], required=True, type=str)
    ingest_parser.set_defaults(func=ingest_db)
    
    # Dump Data
    dump_parser = subparser.add_parser("dump", help="Dump database data to csv file", formatter_class=ArgumentDefaultsHelpFormatter)
    dump_parser.add_argument("dest", help="Output directory. Must be empty or not exist", type=Path)
    dump_parser.set_defaults(func=dump_db)

    # Parse the cli args, splitting out function from args
    args = vars(parser.parse_args())
    func_name = args["func"]
    func_args = {k:v for k,v in args.items() if k != "func"}
    
    return func_name, func_args

if __name__ == "__main__":
    main()
