"""
A Simple cache decorator with TTL.

Adapted from https://stackoverflow.com/questions/815110/is-there-a-decorator-to-simply-cache-function-return-values

A more complete code could be https://github.com/scidam/cachepy , but as it's not installable via pip, I stick with this simple code atm.
https://github.com/argaen/aiocache/tree/master/aiocache is also a ful lfeature cache, but too complex for our use.
"""

from datetime import datetime, timedelta

__version__ = "0.0.1"


# TODO: SOME REWORK TODO HERE, caches func call, but not the params!


class Asyncttlcache(object):
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.ttl = kwargs.get("ttl", 10)

    def __call__(self, func):
        async def inner(*args, **kwargs):
            # Is some lock needed here to be thread safe?
            ttl = timedelta(seconds=kwargs.get("ttl", self.ttl))
            if (
                not ttl
                or func not in self.cached_function_responses
                or (
                    datetime.now() - self.cached_function_responses[func]["fetch_time"]
                    > ttl
                )
            ):
                if "ttl" in kwargs:
                    del kwargs["ttl"]
                res = await func(*args, **kwargs)
                self.cached_function_responses[func] = {
                    "data": res,
                    "fetch_time": datetime.now(),
                }
            return self.cached_function_responses[func]["data"]

        return inner
