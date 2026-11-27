from language.response_validator import matches_language


def isolate_context(messages, code):
    """Keep complete compatible turns; never mutate persisted history."""
    if len(messages) < 2 or messages[0]['role'] != 'system' or messages[-1]['role'] != 'user':
        raise ValueError('Expected system and latest user messages.')
    result = [dict(messages[0])]
    history = messages[1:-1]
    # A bounded history can begin with an orphan assistant message.
    if history and history[0]['role'] == 'assistant':
        history = history[1:]
    for i in range(0, len(history)-1, 2):
        user, assistant = history[i:i+2]
        if user['role'] == 'user' and assistant['role'] == 'assistant' and matches_language(assistant['content'], code):
            result.extend((dict(user), dict(assistant)))
    result.append(dict(messages[-1]))
    return result
