from config import MODELS_DIR

MODELS = {
    "1.7b": "Qwen3-1.7B-Q4_K_M.gguf",
    "4b": "Qwen3-4B-Q4_K_M.gguf",
}
DEFAULT_MODEL = "1.7b"

def model_path(code):
    if code not in MODELS:
        raise ValueError("Unknown model. Use 1.7b or 4b.")
    return MODELS_DIR / MODELS[code]
