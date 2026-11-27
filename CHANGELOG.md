# KlubAI – Changelog

## Version 0.6.0 – 27 November 2026 (planned release)

### Independent Knowledge Engine

- SQLite FTS5/BM25 indexing, document ingestion and overlapping chunks.
- Local 384-dimensional embeddings, cosine search and reciprocal rank fusion.
- Retrieval-augmented answers with exact excerpt validation and source references.
- Rule-based section selection and whitespace-tolerant answer recovery.
- Document updates, synchronization preview, duplicate detection and reindexing.
- Integrity checks, SQLite backups, restoration, metadata export and confirmed clearing.

### Verification

- 218 automated tests passed on Windows; dependency check passed.
- Individual reindexing and multi-product retrieval verified.
- Isolated backup restoration tested; full live restoration and bulk reindexing not verified.
- Network disconnection was not independently recorded.

### Limitations

- Pretrained Qwen3 weights; no custom training yet. English-oriented retrieval; answers may be incomplete or inaccurate.
- Backups are unencrypted and exclude original documents. Single-process administration only.

## Version 0.5.0 – 26 November 2026

### Intelligent Task Execution Release

Developed by Klubnika Bytes.

### New Features

- Independent mathematical calculation engine.
- Decimal-based arithmetic calculations.
- GST, discount and percentage calculations.
- Local date and time retrieval.
- Date difference and date adjustment calculations.
- Leap year identification.
- Length, mass, temperature, time, volume, area and digital storage conversions.
- Local PDF, Word, Excel, CSV, TXT, Markdown, JSON and PowerPoint reading.
- Spreadsheet statistical analysis.
- Sum, average, minimum and maximum calculations.
- Group-wise data aggregation.
- AI-powered document summarization.
- Document-based question answering.

### Improvements

- Improved Excel content formatting.
- Removed unnecessary trailing empty columns.
- Improved numerical output formatting.
- Added Unicode unit symbol handling.
- Improved document intelligence instructions.
- Improved document text availability checks.

### Security

- Restricted file access to authorized input directories.
- Path traversal rejection.
- File size and document processing limits.
- Restricted mathematical expression evaluation.
- Local document processing without external AI APIs.

### Testing

- 132 automated regression tests passed.
- 9 additional unit conversion checks passed.
- Manual task integration testing completed.
- Python dependency validation passed.

### Existing Features

- Local AI conversation using Qwen3.
- Persistent SQLite memory.
- Conversation history.
- Response streaming.
- PDF, DOCX, XLSX, CSV, TXT and PPTX generation.

### Known Limitations

- AI-generated answers may contain factual errors.
- Large-document processing is limited by the current context window.
- OCR for scanned documents is not available.
- Custom model training and knowledge retrieval remain under development.
- Comprehensive production security auditing remains pending.

## Version 0.4.0 – 26 November 2026

### Initial Local AI Assistant Release

- Local CPU-based AI inference.
- Interactive terminal assistant.
- Persistent memory and conversation management.
- Response streaming.
- Six-format document generation.
- GitHub source code integration.
