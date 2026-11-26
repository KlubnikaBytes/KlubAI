
from llama_cpp import Llama

from config import (
    MODEL_PATH,
    CONTEXT_SIZE,
    BATCH_SIZE,
    CPU_THREADS,
    GPU_LAYERS,
    MAX_TOKENS,
    TEMPERATURE,
    TOP_P,
    TOP_K,
    REPEAT_PENALTY,
)


class ModelEngine:

    def __init__(self):

        self.model = None

    def load_model(self):

        if not MODEL_PATH.is_file():

            raise FileNotFoundError(
                f"AI model not found: {MODEL_PATH}"
            )

        self.model = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=CONTEXT_SIZE,
            n_threads=CPU_THREADS,
            n_threads_batch=CPU_THREADS,
            n_batch=BATCH_SIZE,
            n_gpu_layers=GPU_LAYERS,
            use_mmap=True,
            use_mlock=False,
            verbose=False,
        )

    def is_loaded(self):

        return self.model is not None

    @staticmethod
    def sanitize_content(content):

        special_tokens = [
            "<|im_start|>",
            "<|im_end|>",
            "<|endoftext|>",
            "<think>",
            "</think>",
        ]

        for token in special_tokens:
            content = content.replace(token, "")

        return content

    def build_prompt(self, messages):

        parts = []

        for message in messages:

            role = message["role"]

            if role not in (
                "system",
                "user",
                "assistant",
            ):
                continue

            content = self.sanitize_content(
                message["content"]
            )

            parts.append(
                f"<|im_start|>{role}\n"
                f"{content}<|im_end|>\n"
            )

        # Qwen3 non-thinking mode
        parts.append(
            "<|im_start|>assistant\n"
            "<think>\n\n</think>\n\n"
        )

        return "".join(parts)

    def prepare_prompt(self, messages):

        if not self.is_loaded():

            raise RuntimeError(
                "KlubAI model is not loaded."
            )

        messages = [
            dict(message)
            for message in messages
        ]

        while True:

            prompt = self.build_prompt(messages)

            tokens = self.model.tokenize(
                prompt.encode("utf-8"),
                special=True,
            )

            required_tokens = (
                len(tokens)
                + MAX_TOKENS
                + 16
            )

            if required_tokens <= CONTEXT_SIZE:

                return prompt

            # Remove oldest completed conversation turn.
            # Preserve the system prompt and latest question.
            if (
                len(messages) >= 4
                and messages[1]["role"] == "user"
                and messages[2]["role"] == "assistant"
            ):

                del messages[1:3]

            else:

                raise ValueError(
                    "The question or saved context is too "
                    "long. Please shorten it."
                )

    def stream_response(self, messages):

        prompt = self.prepare_prompt(messages)

        stream = self.model(
            prompt,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            repeat_penalty=REPEAT_PENALTY,
            stop=[
                "<|im_end|>",
                "<|im_start|>",
                "<|endoftext|>",
            ],
            echo=False,
            stream=True,
        )

        try:

            for chunk in stream:

                choices = chunk.get(
                    "choices", []
                )

                if not choices:
                    continue

                text = choices[0].get(
                    "text", ""
                )

                if text:
                    yield text

        finally:

            close = getattr(
                stream, "close", None
            )

            if callable(close):
                close()

    def generate_response(self, messages):

        response_parts = []

        for text in self.stream_response(messages):

            response_parts.append(text)

        return "".join(
            response_parts
        ).strip()

    def close(self):

        if self.model is not None:

            self.model.close()

            self.model = None
