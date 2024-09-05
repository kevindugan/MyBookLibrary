from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import dotenv_values
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from csv import reader
from base64 import b64encode
from models import Base, CategoriesTB
from re import compile

config = dotenv_values(".env")

def init_db(host, port):
    """Initialize the database from defined models"""
    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=port, database=config["DB_NAME"])
    engine = create_engine(url, echo=True)
    Base.metadata.create_all(engine)
    
def drop_db_tables(host, port):
    """Drop all tables from defined models"""
    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=port, database=config["DB_NAME"])
    engine = create_engine(url, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def ingest_db(host, filename, type):
    if type == "categrories":
        ingest_db_categories(host, filename)
    elif type == "books":
        ingest_db_books(host, filename)

def ingest_db_categories(host, filename):
    """Ingest all category data from csv file"""
    # Collect any malformed values from csv
    with open(filename, "r") as infile:
        category_pattern = compile(r"[A-Z]{3}[0-9]{6}")
        csvfile = reader(infile)
        next(csvfile) # Skip the header line
        malformed = [it for it,_ in csvfile if category_pattern.fullmatch(it) is None]

    # Read all values and construct table rows
    with open(filename, "r") as infile:
        csvfile = reader(infile)
        next(csvfile) # Skip the header line
        rows = [CategoriesTB(cat_id=it, cat_path=jt.replace(" / ", "|")) for it,jt in csvfile if it not in malformed]
        
    if len(malformed) > 0:
        message = ["The following entries are malformed and were not added:"] + malformed
        print("\n" + "\n    ".join(message) + "\n")

    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        session.add_all(rows)
        session.commit()

def ingest_db_books(host, filename):
    """Ingest all book data from csv file
    
    cover art should be file path relative to csv file
    """
    # from base64 import b64encode
    # cover_fc = open("data/stewart_calculus.jpg", "rb").read()
    # b64_cover = base64.b64encode(cover_fc).decode('utf-8')
    # ext = "data/stewart_calculus.jpg".split('.')[-1]
    # url = f"data:image/{ext};base64,{b64_cover}"
    with open(filename, "r") as infile:
        csvfile = reader(infile)

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
    ingest_parser.add_argument("filename", help="Input file")
    ingest_parser.add_argument("--type", help="Type of Data", choices=["categories", "books"], required=True, type=str)
    ingest_parser.set_defaults(func=ingest_db)

    # Parse the cli args, splitting out function from args
    args = vars(parser.parse_args())
    func_name = args["func"]
    func_args = {k:v for k,v in args.items() if k != "func"}
    
    return func_name, func_args

if __name__ == "__main__":
    main()
