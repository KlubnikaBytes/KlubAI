"""Run local inference without touching conversation or memory databases."""
import json
import time
from config import DATASETS_DIR
from core.model_engine import ModelEngine
from language.language_prompt import apply_language, reinforce_language
from language.response_validator import matches_language


def main():
    cases = json.loads((DATASETS_DIR / 'multilingual_benchmark.json').read_text(encoding='utf8'))
    engine = ModelEngine()
    passed = 0
    try:
        engine.load_model()
        for case in cases:
            code = case['language']
            messages = apply_language([{'role':'system','content':'Answer accurately and briefly.'},{'role':'user','content':case['question']}],code)
            start = time.perf_counter()
            for retry in (False, True):
                stream = engine.stream_response(reinforce_language(messages,code,retry),temperature=.2)
                try:
                    answer = ''.join(stream).strip()
                finally:
                    stream.close()
                if matches_language(answer,code):
                    break
            ok = matches_language(answer,code)
            passed += int(ok)
            print(f"\n{code} | {case['question']} | language={ok} | {time.perf_counter()-start:.2f}s")
            print(answer if ok else '[Rejected language output]')
            print('Reference for manual factual review:',case['reference'])
        print(f'\nLanguage compliance: {passed}/{len(cases)}. Factual quality requires manual review.')
    finally:
        engine.close()

if __name__ == '__main__':
    main()
