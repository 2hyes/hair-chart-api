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
    DATABASE_URL=postgresql://{USER}:{PASSWORD}@{localhost}/hair_chart_dev
    ```
- for prod environment
    
    wip