# Local and offline setup

Initial installation and model acquisition require internet or pre-staged files. On Windows x64 use Python 3.11 and a compatible CPU wheel. From the repository root:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install llama-cpp-python==0.3.18 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --only-binary=:all:
python -m pip install -r requirements.txt
python -m pip check
hf download ggml-org/Qwen3-1.7B-GGUF Qwen3-1.7B-Q4_K_M.gguf --local-dir models
Get-FileHash models\Qwen3-1.7B-Q4_K_M.gguf -Algorithm SHA256
```

Previously verified GGUF SHA-256: `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`. Review upstream model licenses. The dependency snapshot was validated on the existing machine, not a fresh installation; wheel availability may vary.

Populate embedding cache once while online:

```powershell
python -c "from fastembed import TextEmbedding; from pathlib import Path; m=TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2',cache_dir=str(Path('knowledge/embeddings').resolve()),threads=4); print(len(list(m.embed(['test']))[0]))"
```

Expected dimension: 384. Runtime embedding engine uses local files only. Keep model and cache files when offline. Disconnect Wi-Fi and Ethernet, then run `python main.py`, test a general AI question, `/knowledge-semantic Billnika invoice management` (requires indexed sample knowledge), file generation and `/knowledge-verify`. Run tests and dependency check. Reconnect only when finished.

Troubleshooting: illegal instruction 0xc000001d may indicate an incompatible native wheel; the 0.3.18 CPU wheel worked on the development Ryzen 5 7530U. The 4096 vs 40960 context warning is expected. Missing embeddings require the local cache and `/knowledge-embed`. Do not regenerate the dependency snapshot unnecessarily.
