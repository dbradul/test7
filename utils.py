import functools

import time


def format_records(records):
    return '<br>'.join(str(rec) for rec in records)

def profile(msg='Elapsed time'):
    def internal(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            print(msg, f'({f.__name__}): {time.time() - start}s')
            return result
        return deco
    return internal