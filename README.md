# Books Catalog

Get book categories from [BookShop.org](http://bookshop.org)

```bash
docker container run --rm -v ${PWD}:/books_app \
                     --network mybooklibrary_default \
                     -it python:3.12-bookworm bash -c \
                        "apt update && \
                         apt install -y postgresql && \
                         cd /books_app && \
                         pip install -qU pip fastapi uvicorn[standard] sqlalchemy psycopg2 && \
                         bash"
```

```sql
SELECT id,title,author,category,substring(cover_art,1,40)||'...' FROM books;
```
