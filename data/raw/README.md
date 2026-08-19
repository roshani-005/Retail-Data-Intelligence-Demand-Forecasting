# Raw Data

Place the supplied Kaggle/Superstore CSV here as:

```text
superstore.csv
```

The repository does not fabricate or alter the source dataset. Once the CSV is present, run:

```bash
python src/etl.py
```

The ETL pipeline will create curated files under `data/processed/`.

Expected fields are documented in the root README. The pipeline validates the schema before transforming the data.
