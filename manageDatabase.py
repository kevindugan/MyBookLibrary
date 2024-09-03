from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import dotenv_values
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from csv import reader
from models import Base, CategoriesTB

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
    
def ingest_db_data(host, filename):
    """Ingest all data from csv file"""
    with open(filename, "r") as infile:
        csvfile = reader(infile)
        rows = [CategoriesTB(cat_id=it[0], cat_path=it[1].replace(" / ", "|")) for it in csvfile]

    url = URL.create("postgresql", username=config["DB_USER"], password=config["DB_PASS"], host=host, port=config["DB_PORT"], database=config["DB_NAME"])
    engine = create_engine(url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        session.add_all(rows)
        session.commit()
    

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
    ingest_parser.set_defaults(func=ingest_db_data)

    # Parse the cli args, splitting out function from args
    args = vars(parser.parse_args())
    func_name = args["func"]
    func_args = {k:v for k,v in args.items() if k != "func"}
    
    return func_name, func_args

if __name__ == "__main__":
    main()
