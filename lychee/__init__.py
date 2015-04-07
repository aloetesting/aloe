def step(sentence_or_func):
    # TODO: write this

    if isinstance(sentence_or_func, str):
        return lambda func: func
    else:
        return func
