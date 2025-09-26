# Database Intake (Postgres/Mongo/Chroma/SQLAlchemy)

Goal: catalog schemas/tables/collections to feed the blueprint and tasks pipeline.

Recommended (no new deps needed): export lightweight manifests and feed as CSVs.

- Postgres (psql):
  - `psql "$DSN" -c "\\dt" > repos/pg_tables.txt`
  - `psql "$DSN" -c "\\d+ schema.table" > repos/pg_schema_table.txt`
  - Convert to CSV listing tables with columns: `name,desc,tags,score`
- Mongo (mongosh):
  - `mongosh "$URI" --eval "db.getCollectionNames().join('\\n')" > repos/mongo_collections.txt`
  - Add CSV entries for key collections.
- Chroma/Vector DB:
  - List collections and counts; add CSV entries for target collections.

Feed the CSVs into blueprint/intake:
- `./ops/generate_blueprint.sh repos repos 20`
- `./ops/intake_inventory.sh --filelist repos/db_collections.csv --label db`

Later (optional): tools/db_intake.py can be added to connect and auto-export schema; for now we keep the process manual for speed and zero new dependencies.

