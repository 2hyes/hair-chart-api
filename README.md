# hair-chart-api
api service for hair chart project

## design

### dev env
This project deploys a FastAPI server and a PostgreSQL database on an AWS EC2 (Ubuntu 24.04) instance using Docker Compose.

- design

    ![Architecture Diagram](./docs/hair-chart-dev-design.png)

- Ports

    | Component       | Port   | Exposed To      |
    | --------------- | ------ | --------------- |
    | FastAPI Backend | `8000` | Public (Client) |
    | PostgreSQL DB   | `5432` | Internal Only   |

### prod env (WIP)

For production use, consider:
- Using Amazon RDS for database
- Exposing API behind Nginx or a reverse proxy
- Adding HTTPS termination via Let's Encrypt or AWS ACM

## Setup

### init setting
- .env
    ```
    # DEV env
    POSTGRES_USER={ID}
    POSTGRES_PASSWORD={PWD}
    POSTGRES_DB={DB_NAME}
    ```
    DB 정보를 입력한다.

- db 생성 (자동 생성)
    ```sql
    -- 1. create database
    CREATE DATABASE hair_chart_dev
    WITH ENCODING 'UTF8'
        LC_COLLATE='ko_KR.UTF-8'
        LC_CTYPE='ko_KR.UTF-8'
        TEMPLATE=template0;

    -- if there isn't ko_KR.UTF-8, you need to install
    -- locale -a | grep ko_KR; sudo locale-gen ko_KR.UTF-8 && sudo update-locale

    -- 2. create user 
    -- 여기에 유저와 패스워드 수정해주세요.
    CREATE USER hair_chart_user WITH PASSWORD 'your_password_here';
    GRANT ALL PRIVILEGES ON DATABASE hair_chart_dev TO hair_chart_user;
    ```
    기본적으로 환경변수 셋팅으로 자동 처리되어 컨테이너 실행시 자동 생성됩니다.
    생성이 되지않은 경우에만 수동으로 처리해주세요.


## Run api server
- local
    ```
    uvicorn main:app --reload
    ```

- with docker (on server)
    ```
    docker compose down -v 
    docker compose up --build
    ```

## Deploy
- for dev environment
    ```
    docker compose up --build -d
    ```
    git 연동했음
    git pull해서 신규 커밋에서 다시 compose하는 형태

- for prod environment
    