import datetime
from functools import wraps
import json
import os


def file_cache(cache_file, timeout=300):
    def decorator(func):
        ''' http://stackoverflow.com/a/1594484/68035 '''
        @wraps(func)
        def wrapped(self=None):
            now = int(datetime.datetime.now().strftime('%s'))
            stat = None
            if not hasattr(func, 'cache'):
                func.cache = None
            if os.path.exists(cache_file):
                stat = os.stat(cache_file)

            if(stat is None
               or (stat.st_size == 0) or ((now - stat.st_mtime) > timeout)):
                if self:
                    data = func(self)
                else:
                    data = func()

                with open(cache_file, 'w+') as f:
                    json.dump(data, f)

                func.cache = data
                return data
            elif func.cache:
                return func.cache
            else:
                with open(cache_file, 'r') as f:
                    func.cache = json.load(f)
                    return func.cache

        return wrapped
    return decorator
