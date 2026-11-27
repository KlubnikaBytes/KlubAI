# Command reference

Commands are entered inside KlubAI, not PowerShell. Replace placeholders with actual values.

| Command | Description |
|---|---|
| `/ask-knowledge question` | Answer from local knowledge |
| `/rag-info` | Show RAG configuration |
| `/rag-help` | Show RAG commands |
| `/rag-on` | Enable automatic knowledge questions |
| `/rag-off` | Disable automatic knowledge questions |
| `/knowledge-semantic query` | Semantic knowledge search |
| `/knowledge-hybrid query` | Hybrid knowledge search |
| `/knowledge-retrieval-info` | Show retrieval statistics |
| `/knowledge-embed` | Generate missing local embeddings |
| `/knowledge-embedding-info` | Show embedding statistics |
| `/knowledge-help` | Show knowledge commands |
| `/knowledge-files` | List source documents |
| `/knowledge-add filename` | Import document |
| `/knowledge-add-all` | Import all supported documents |
| `/knowledge-info` | Show knowledge statistics |
| `/knowledge-list` | List indexed documents |
| `/knowledge-search words` | Search local knowledge |
| `/knowledge-remove ID confirm` | Remove indexed document |
| `/analysis-help` | Show data analysis commands |
| `/sum filename column` | Calculate column total |
| `/average filename column` | Calculate average |
| `/max filename column` | Find maximum value |
| `/min filename column` | Find minimum value |
| `/count filename` | Count records |
| `/columns filename` | Show column names |
| `/analyze filename` | Analyze dataset |
| `/group filename group value` | Grouped totals |
| `/summarize filename` | Summarize document |
| `/ask-file filename &#124; question` | Ask about document |
| `/read-help` | Show file reading commands |
| `/read filename` | Read local document |
| `/file-info filename` | Show file information |
| `/input-files` | List available input files |
| `/date` | Show current date |
| `/time` | Show current time |
| `/datetime` | Show current date and time |
| `/day` | Show current day |
| `/days-between date date` | Calculate date difference |
| `/add-days date number` | Calculate future date |
| `/subtract-days date number` | Calculate previous date |
| `/leap-year year` | Check leap year |
| `/convert value unit to unit` | Convert units |
| `/units` | Show supported units |
| `/task-help` | Show task commands |
| `/calculate expression` | Calculate mathematics |
| `/gst amount rate` | Calculate GST |
| `/discount amount rate` | Calculate discount |
| `/percentage rate amount` | Calculate percentage |
| `/file-help` | Show file generation commands |
| `/create format topic` | Generate a file |
| `/files` | Show generated files |
| `/help` | Show available commands |
| `/clear` | Clear terminal screen |
| `/new` | Start a new conversation |
| `/history` | Show conversation history |
| `/model` | Show AI model information |
| `/memory-help` | Show memory commands |
| `/memory` | Display saved facts |
| `/remember key=value` | Save information |
| `/recall key` | Retrieve information |
| `/forget key` | Remove saved information |
| `/forget-all confirm` | Remove all saved facts |
| `/delete-data confirm` | Clear all saved data |
| `/exit` | Exit KlubAI |
| `/knowledge-status` | Show database and embedding status |
| `/knowledge-detail ID` | Show document metadata |
| `/knowledge-update ID` | Replace indexed content from source |
| `/knowledge-sync` | Preview source changes without modifying index |
| `/knowledge-reindex ID` | Rebuild document chunks and embeddings |
| `/knowledge-reindex-all confirm` | Rebuild all indexes |
| `/knowledge-duplicates` | Find identical source files |
| `/knowledge-verify` | Check database, FTS and vectors |
| `/knowledge-backup` | Create local database backup |
| `/knowledge-backups` | List local backups |
| `/knowledge-restore filename confirm` | Restore backup (automatic safety backup) |
| `/knowledge-export` | Export metadata as JSON |
| `/knowledge-clear confirm` | Clear index (automatic safety backup) |

Example: `/ask-file sample.txt | What is KlubAI?`

Commands ending in `confirm` require that literal word. `/clear` clears the screen; `/knowledge-clear confirm` clears indexed knowledge. `/delete-data confirm` clears conversation and memory data, not the knowledge index.
