# Automatic Database Persistence

The extraction server now automatically persists extracted questions to the SQLite database while maintaining filesystem backups.

## How It Works

When the Tampermonkey script extracts a question and sends it to the server:

1. **Filesystem Backup** (as before):
   - HTML saved to `extractions/{timestamp}_{source}_{index}.html`
   - JSON metadata saved to `extractions/{timestamp}_{source}_{index}.json`
   - Images downloaded to `extractions/{timestamp}_{source}_{index}_img{N}.{ext}`

2. **Database Persistence** (NEW):
   - Question extracted and parsed to determine source and question key
   - Source created or retrieved from database
   - Question record created with unique constraint on (source_id, source_question_key)
   - Images copied to `media_root/{source}/{question_key}_img{N}.{ext}`
   - Media records created linking images to questions

## Running the Server

Start the extraction server:

```bash
python scripts/extraction_server.py
```

Or use the PowerShell script:

```bash
.\scripts\start_extraction_server.ps1
```

The server will:
- Listen on http://localhost:5000
- Accept extraction POSTs from Tampermonkey
- Save to filesystem (extractions/)
- Persist to database (doughub.db)
- Copy media to media_root/

## Server Output

When an extraction is received:

```
================================================================================
[NEW] EXTRACTION RECEIVED at 2025-11-16T20:00:00.000Z
================================================================================
[URL] https://mksap19.acponline.org/app/question-bank/...
[SITE] MKSAP 19
[ELEMENTS] 892
[IMAGES] 2
[SIZE] 156.3 KB
================================================================================

[SAVED] Files saved:
   HTML: extractions\20251116_200000_MKSAP_19_0.html
   JSON: extractions\20251116_200000_MKSAP_19_0.json

[DB] Persisting: MKSAP_19/mk19x_3_id_q008
[DB] Added question to database (ID: 5)
[DB]   Copied to media_root: MKSAP_19/mk19x_3_id_q008_img0.jpg
[DB]   Added media (ID: 6): MKSAP_19/mk19x_3_id_q008_img0.jpg
[DB]   Copied to media_root: MKSAP_19/mk19x_3_id_q008_img1.png
[DB]   Added media (ID: 7): MKSAP_19/mk19x_3_id_q008_img1.png
[DB] ✓ Successfully persisted to database

[PREVIEW] Body Text Preview:
Skip to content Home Text Question Bank...

================================================================================
[OK] Total extractions received: 1
[FILE] View HTML: P:\Python Projects\DougHub\extractions\20251116_200000_MKSAP_19_0.html
[DB] ✓ Persisted to database
================================================================================
```

## Error Handling

If database persistence fails:
- The filesystem backup is **still saved** (data is not lost)
- An error message is logged to the terminal
- The API response includes the error details

Example error output:
```
[DB] ✗ Database persistence failed: Database connection error
```

## API Response

The `/extract` endpoint now returns:

```json
{
  "status": "success",
  "message": "Data received successfully",
  "extraction_count": 1,
  "files": {
    "html": "extractions/20251116_200000_MKSAP_19_0.html",
    "json": "extractions/20251116_200000_MKSAP_19_0.json",
    "images": ["extractions/20251116_200000_MKSAP_19_0_img0.jpg"]
  },
  "database": {
    "persisted": true,
    "error": null
  }
}
```

## Querying the Database

After extraction, query the database using the ingestion module or directly:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from doughub.config import DATABASE_URL
from doughub.persistence import QuestionRepository

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
repo = QuestionRepository(session)

# Get all questions from a source
questions = repo.get_all_questions(source_id=1)

# Get a specific question
question = repo.get_question_by_source_key(source_id=1, source_question_key="mk19x_3_id_q008")

session.close()
```

## Idempotency

The system is idempotent - extracting the same question multiple times will:
- Create a new filesystem backup each time (with different timestamp)
- **NOT** create duplicate database entries
- Log that the question already exists in the database

## Manual Bulk Import

To import existing extractions from the `extractions/` directory:

```bash
python -m doughub.ingestion
```

This is useful for:
- Importing extractions created before database integration
- Re-importing after database reset
- Bulk processing of archived extractions

## Directory Structure

```
DougHub/
├── doughub.db                    # SQLite database
├── extractions/                  # Filesystem backups (timestamped)
│   ├── 20251116_200000_MKSAP_19_0.html
│   ├── 20251116_200000_MKSAP_19_0.json
│   └── 20251116_200000_MKSAP_19_0_img0.jpg
└── media_root/                   # Organized media storage
    ├── MKSAP_19/
    │   ├── mk19x_3_id_q008_img0.jpg
    │   └── mk19x_3_id_q008_img1.png
    └── ACEP_PeerPrep/
        └── question_123_img0.jpg
```

## Benefits

1. **Dual Storage**: Filesystem backups for inspection + database for querying
2. **Automatic**: No manual ingestion needed for new extractions
3. **Safe**: Filesystem backup always saved, even if DB fails
4. **Organized**: Media files stored in structured directories
5. **Idempotent**: Safe to extract same question multiple times
6. **Queryable**: Efficient database queries vs filesystem scanning

## Migration Path

Eventually, once confident in the database system:
1. The filesystem backups in `extractions/` can be archived or deleted
2. All workflows will use the database via `QuestionRepository`
3. Media files will remain in `media_root/` as the canonical storage
