set PGUSER=xkocal00
set PGPASSWORD=admin4isa

dropdb isa-local
call heroku pg:pull DATABASE_URL isa-local