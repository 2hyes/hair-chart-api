# hair-chart-api
api service for hair chart project

## setting
### postgreSQL 

[Download PostgreSQL](https://www.postgresql.org/download/) and start it as a background service.

- for mac
```
# install
brew install postgresql

# start 
brew services start postgresql
```

### DB setting 
refer to [hair-chart-db](https://github.com/2hyes/hair-chart-db)

### .env
- for dev environment
    ```
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_DB=
    ```
- for prod environment
    
    wip


## run api server
```
uvicorn main:app --reload
```

with docker
```
docker compose down -v 
docker compose up --build
```
