"""
CacheTools Utilities

This code is public domain.
"""

from typing import Optional, Callable, Dict, List, Set, Any, Union, MutableMapping

import cachetools
import json


#
# UTILS
#


class MutMapMix:
    """Convenient MutableMapping Mixin, forward to _cache."""

    def __getitem__(self, key):
        return self._cache.__getitem__(key)

    def __setitem__(self, key, val):
        return self._cache.__setitem__(key, val)

    def __delitem__(self, key):
        return self._cache.__delitem__(key)

    def __len__(self):
        return self._cache.__len__()

    def __iter__(self):
        return self._cache.__iter__()


class KeyMutMapMix(MutMapMix):
    """Convenient MutableMapping Mixin with a key filter, forward to _cache."""

    def _key(self, key):
        return key

    def __getitem__(self, key):
        return self._cache.__getitem__(self._key(key))

    def __setitem__(self, key, val):
        return self._cache.__setitem__(self._key(key), val)

    def __delitem__(self, key):
        return self._cache.__delitem__(self._key(key))


#
# CACHETOOLS EXTENSIONS
#


class PrefixedCache(KeyMutMapMix, MutableMapping):
    """Cache class to add a key prefix."""

    def __init__(self, cache: MutableMapping, prefix: Union[str, bytes] = ""):
        self._prefix = prefix
        self._cache = cache

    def _key(self, key):
        return self._prefix + str(key)


class StatsCache(MutMapMix, MutableMapping):
    """Cache class to keep stats."""

    def __init__(self, cache: MutableMapping):
        self._reads, self._writes, self._dels, self._hits = 0, 0, 0, 0
        self._cache = cache

    def hits(self):
        return float(self._hits) / float(max(self._reads, 1))

    def __getitem__(self, key):
        # log.debug(f"get: {key} {key in self._cache}")
        self._reads += 1
        res = self._cache.__getitem__(key)
        self._hits += 1
        return res

    def __setitem__(self, key, val):
        self._writes += 1
        return self._cache.__setitem__(key, val)

    def __delitem__(self, key):
        self._dels += 1
        return self._cache.__delitem__(key)

    def clear(self):
        return self._cache.clear()


#
# MEMCACHED
#


class JsonSerde:
    """JSON serialize/deserialize for MemCached."""

    # keep strings, else json
    def serialize(self, key, value):
        if isinstance(value, str):
            return value.encode("utf-8"), 1
        else:
            return json.dumps(value).encode("utf-8"), 2

    # reverse previous serialization
    def deserialize(self, key, value, flags):
        if flags == 1:
            return value.decode("utf-8")
        elif flags == 2:
            return json.loads(value.decode("utf-8"))
        else:
            raise Exception("Unknown serialization format")


class MemCached(KeyMutMapMix, MutableMapping):
    """MemCached-compatible wrapper class for cachetools with key encoding."""

    def __init__(self, cache):
        self._cache = cache

    # memcached keys are constrained bytes, we need some encoding…
    # short (250 bytes) ASCII without control chars nor spaces
    # we do not use hashing which might be costly and induce collisions
    def _key(self, key):
        import base64
        return base64.b64encode(str(key).encode("utf-8"))

    def __len__(self):
        return self._cache.stats()[b"curr_items"]

    def stats(self):
        return self._cache.stats()

    def clear(self):
        return self._cache.flush_all()


class PrefixedMemCached(MemCached):
    """MemCached-compatible wrapper class for cachetools with a key prefix."""

    def __init__(self, cache, prefix: str = ""):
        super().__init__(cache=cache)
        self._prefix = bytes(prefix, "utf-8")

    def _key(self, key):
        import base64
        return self._prefix + base64.b64encode(str(key).encode("utf-8"))


class StatsMemCached(MemCached):
    """Cache MemCached-compatible class with stats."""

    def __init__(self, cache):
        self._cache = cache

    def hits(self):
        """Return overall cache hit rate."""
        stats = self._cache.stats()
        return float(stats[b"get_hits"]) / max(stats[b"cmd_get"], 1)


#
# REDIS
#


class RedisCache(MutableMapping):
    """Redis wrapper for cachetools."""

    def __init__(self, cache, ttl=600):
        self._cache = cache
        self._ttl = ttl

    def info(self, *args, **kwargs):
        return self._cache.info(*args, **kwargs)

    def clear(self):
        return self._cache.flushdb()

    def _serialize(self, s):
        return json.dumps(s)

    def _deserialize(self, s):
        return json.loads(s)

    def _key(self, key):
        return json.dumps(key)

    def __getitem__(self, index):
        val = self._cache.get(self._key(index))
        if val:
            return self._deserialize(val)
        else:
            raise KeyError()

    def __setitem__(self, index, value):
        return self._cache.set(self._key(index), self._serialize(value), ex=self._ttl)

    def __delitem__(self, index):
        return self._cache.delete(self._key(index))

    def __len__(self):
        return self._cache.dbsize()

    def __iter__(self):
        raise Exception("not implemented yet")


class PrefixedRedisCache(RedisCache):
    """Prefixed Redis wrapper class for cachetools."""

    def __init__(self, cache, prefix: str = "", ttl=600):
        super().__init__(cache, ttl)
        self._prefix = prefix

    def _key(self, key):
        return self._prefix + json.dumps(key)


class StatsRedisCache(RedisCache):
    """TTL-ed Redis wrapper class for cachetools."""

    def __init__(self, cache, ttl=600):
        super().__init__(cache, ttl)

    def hits(self):
        stats = self.info(section="stats")
        return float(stats["keyspace_hits"]) / (stats["keyspace_hits"] + stats["keyspace_misses"])
