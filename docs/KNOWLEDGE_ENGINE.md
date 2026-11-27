# Independent knowledge engine

## Workflow

1. Copy supported PDF, DOCX, XLSX, CSV, TXT, MD, JSON or PPTX sources into `knowledge/documents/`.
2. Run `/knowledge-files`, then `/knowledge-add filename` or `/knowledge-add-all`.
3. Run `/knowledge-embed`, then `/knowledge-status`.
4. Search with `/knowledge-search words`, `/knowledge-semantic query` or `/knowledge-hybrid query`.
5. Ask `/ask-knowledge What is Billnika?`.

## Design

SHA-256 duplicate checks; 1000-character chunks with 150-character overlap; SQLite FTS5/BM25; all-MiniLM-L6-v2 local normalized 384-dimensional vectors; cosine threshold 0.20; reciprocal rank fusion K=60. RAG uses up to five chunks and a 2000-token evidence budget. Exact excerpt validation checks source IDs and copied text, not factual truth or relevance. Section selection is rule-based. Automatic RAG mode is session-only and currently recognizes `about billnika ` and `about klubai ` prefixes.

## Maintenance

`/knowledge-sync` previews changes; `/knowledge-detail ID` shows metadata; `/knowledge-update ID` replaces chunks and invalidates vectors; run `/knowledge-embed` afterwards. `/knowledge-reindex ID` rebuilds chunks and vectors together. `/knowledge-reindex-all confirm` rebuilds all indexed sources; make a backup first. `/knowledge-remove ID confirm` removes the index entry, not the source. `/knowledge-duplicates` detects identical source bytes. `/knowledge-verify` checks database, FTS and vectors; use status to check missing vectors.

## Limits

English-oriented embeddings, fixed character chunking, no OCR, extraction limits, possible irrelevant retrieval or abstention despite available evidence. Source locations refer to extracted text offsets, not necessarily original page numbers. Updating the index does not train model weights. Large-scale retrieval and concurrent administration are not validated.
