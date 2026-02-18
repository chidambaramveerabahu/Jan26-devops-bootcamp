
```bash
docker run --name postgres-db \
    -e POSTGRES_USER=myuser \
    -e POSTGRES_PASSWORD=mypassword \
    -e POSTGRES_DB=mydatabase \
    -p 5432:5432 \
    -d postgres:15
```


<!-- postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'testdb')} -->


<!-- postgresql://{username:password}@{host}:5432/{db_name} -->
postgresql://myuser:mypassword}@{localhost:5432/mydatabase