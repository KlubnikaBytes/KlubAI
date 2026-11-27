# KlubAI v0.6.0

Independent local terminal AI assistant application developed by Klubnika Bytes. Uses pretrained Qwen3 weights, not a foundation model trained by Klubnika Bytes. No external AI inference API is required.

## Capabilities

Local conversation, streaming, SQLite memory, arithmetic and GST, date/time, unit conversion, six-format file generation (PDF, DOCX, XLSX, CSV, TXT, PPTX), eight-format document reading, spreadsheet analysis, document summarization and local knowledge retrieval with source excerpts.

## Setup

Windows x64, Python 3.11, CPU with AVX2 recommended. The development machine has 16 GB RAM; this is not a measured minimum. See [offline setup](docs/OFFLINE_SETUP.md) for dependencies and model acquisition.

```powershell
cd D:\KlubAI
.\venv\Scripts\Activate.ps1
python main.py
```

Use `/help` to list commands and `/exit` to quit. Put files for reading in `inputs/` and knowledge sources in `knowledge/documents/`. Generated files are in `outputs/`.

## Architecture

Terminal → assistant routers → deterministic tools or local Qwen3 inference. Knowledge sources → extraction → overlapping chunks → SQLite FTS5 and local embeddings → hybrid retrieval → validated excerpts. Memory and knowledge use separate SQLite databases.

## Documentation

- [Knowledge engine](docs/KNOWLEDGE_ENGINE.md)
- [Command reference](docs/COMMAND_REFERENCE.md)
- [Backup and recovery](docs/BACKUP_AND_RECOVERY.md)
- [Offline setup](docs/OFFLINE_SETUP.md)
- [Changelog](CHANGELOG.md)

## Testing

`python -m pytest tests -q` and `python -m pip check`. Development baseline: 218 passing tests. Review generated content before professional use. No OCR, comprehensive security audit or custom model training yet. Model and dependency licenses remain applicable; repository licensing must be established by the owner. Do not commit private inputs, databases, backups or model weights.
