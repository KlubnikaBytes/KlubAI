# Backup and recovery

Use one running KlubAI process. Backups are stored in `storage/backups/` and contain indexed text, metadata and vectors, not original documents or conversation memory. They are unencrypted; protect access and retain a separate secure copy of original sources.

- `/knowledge-backup`: create a verified SQLite backup.
- `/knowledge-backups`: list available backup filenames.
- `/knowledge-export`: export document metadata JSON (not a restorable database).
- `/knowledge-restore filename confirm`: restore a listed matching-schema backup, with an automatic backup of the previous index.
- `/knowledge-clear confirm`: clear indexed documents after an automatic backup; source files remain.

Before restoration, exit other processes and back up the current index and source files. Use only trusted backups. After restoration, run `/knowledge-verify`, `/knowledge-status` and `/knowledge-sync`. Reconcile changed sources manually. Test recovery on isolated data first. Full live restoration, large databases and concurrent access are not validated. Restoration stages a copy in RAM. The current implementation does not automatically back up before bulk reindexing.

Isolated test: `python -m pytest tests/test_knowledge_administration.py -v`.
