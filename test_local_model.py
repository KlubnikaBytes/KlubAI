
from pathlib import Path
import time
import traceback

import llama_cpp
from llama_cpp import Llama


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "Qwen3-1.7B-Q4_K_M.gguf"
)


def main():

    print("=" * 60)
    print("KlubAI - Local AI Model Test")
    print("Developed by Klubnika Bytes")
    print("=" * 60)

    print(f"Library version: {llama_cpp.__version__}")

    if not MODEL_PATH.is_file():
        print("ERROR: Model file not found.")
        return

    print(f"Model path: {MODEL_PATH}")

    print(
        f"Model size: "
        f"{MODEL_PATH.stat().st_size / (1024 ** 3):.2f} GiB"
    )

    model = None

    try:

        print("\nLoading local AI model...", flush=True)

        load_start = time.perf_counter()

        model = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=1024,
            n_threads=4,
            n_threads_batch=4,
            n_batch=64,
            n_gpu_layers=0,
            use_mmap=True,
            use_mlock=False,
            verbose=True,
        )

        load_time = time.perf_counter() - load_start

        print("\nMODEL LOADED SUCCESSFULLY")

        print(f"Model loading time: {load_time:.2f}s")

        prompt = (
            "<|im_start|>system\n"
            "You are KlubAI, an AI assistant application "
            "developed by Klubnika Bytes using Qwen3."
            "<|im_end|>\n"
            "<|im_start|>user\n"
            "What is Python? Answer in one sentence."
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
            "<think>\n\n</think>\n\n"
        )

        print("\nGenerating AI response...", flush=True)

        response_start = time.perf_counter()

        result = model(
            prompt,
            max_tokens=128,
            temperature=0.3,
            top_p=0.8,
            top_k=20,
            stop=[
                "<|im_end|>",
                "<|im_start|>",
                "<|endoftext|>",
            ],
            echo=False,
        )

        response_time = (
            time.perf_counter() - response_start
        )

        response = result["choices"][0]["text"].strip()

        if not response:
            raise RuntimeError("Model returned an empty response.")

        print("\n" + "=" * 60)
        print("KlubAI Response:")
        print("=" * 60)

        print(response)

        print("\n" + "=" * 60)
        print("Performance Information")
        print("=" * 60)

        print(f"Model loading time: {load_time:.2f}s")
        print(f"Response time: {response_time:.2f}s")

        usage = result.get("usage", {})

        completion_tokens = usage.get(
            "completion_tokens", 0
        )

        print(
            f"Prompt tokens: "
            f"{usage.get('prompt_tokens', 0)}"
        )

        print(f"Generated tokens: {completion_tokens}")

        if response_time > 0:
            print(
                f"Generation speed: "
                f"{completion_tokens / response_time:.2f} tokens/sec"
            )

        print("\nLOCAL AI TEST COMPLETED SUCCESSFULLY")

    except Exception as error:

        print("\nLOCAL AI TEST FAILED")
        print(f"Error: {error}")

        traceback.print_exc()

    finally:

        if model is not None:
            model.close()

            print("\nModel resources released.")


if __name__ == "__main__":
    main()
