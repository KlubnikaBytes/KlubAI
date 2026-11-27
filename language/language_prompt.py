INSTRUCTIONS = {
    'en': 'Respond in English.',
    'hi': 'Respond in Hindi using Devanagari script. केवल सरल और स्वाभाविक हिंदी में उत्तर दें।',
    'bn': 'Respond in Bengali using Bengali script. সহজ ও স্বাভাবিক বাংলায় উত্তর দিন।',
    'hinglish': 'Respond in Hinglish using Latin script. Roman Hindi mein jawab do, English technical terms use karo. Example style: Yeh ek useful tool hai. Iska istemal kaam ke liye hota hai. Do not copy the example content.',
}


def apply_language(messages, code):
    result = [dict(message) for message in messages]
    if not result or result[0]['role'] != 'system':
        raise ValueError('Expected a system message.')
    result[0]['content'] += '\n\n' + INSTRUCTIONS[code] + ' Preserve code, identifiers and proper names. Be concise and factual.'
    return result


def reinforce_language(messages, code, retry=False):
    result = [dict(message) for message in messages]
    if result[-1]['role'] != 'user':
        raise ValueError('Expected a user message.')
    if retry:
        result = [result[0], result[-1]]
    result[-1]['content'] += '\n\nResponse requirement: ' + INSTRUCTIONS[code]
    return result
