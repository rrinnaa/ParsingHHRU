FROM alpine:latest

RUN apk add --no-cache sqlite

COPY init_db.sql /init_db.sql

VOLUME /db

WORKDIR /db

CMD ["sqlite3", "/db/vacancies.db", ".read /init_db.sql"]
