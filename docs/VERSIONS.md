# Versions

[Sources](https://github.com/zx80/cachetools-utils),
[documentation](https://zx80.github.io/cachetools-utils/) and
[issues](https://github.com/zx80/cachetools-utils/issues)
are hosted on [GitHub](https://github.com).
Install [package](https://pypi.org/project/CacheToolsUtils/) from
[PyPI](https://pypi.org/).

## TODO or NOT TODO…

- write a tutorial!
- write recipes!
- add a `close`?
- rename `hits`  `hit_rate`?
- add other efficiency statistics?
- add ability to reconnect if an external cache fails?
  this could be for redis or memcache.
  Maybe the existing client can do that with appropriate options?

## 8.0 on ?

Add `LockedCache` class for shared cache and threading.
Add resiliency option to `TwoLevelCache`.
Add extended `cached` decorator with `in` and `del` support.
Use base85 instead of base64 for MemCached keys.
Improved documentation.
Hide some private internals.

## 7.0 on 2023-06-17

Switch to `pyproject.toml`.
Require Python *3.10+* for easier typing.

## 6.0 on 2023-03-19

Improved documentation for `github.io`.
Add a `pyproject.toml` (stupid) file.

## 5.1 on 2022-11-12

Test with Python *3.12*.

## 5.0 on 2022-09-11

Add `pymarkdown` check.
Add GitHub CI configuration.
Add a badge.

## 4.3 on 2022-09-07

Fix missing key filtering for `Redis`'s `get`, `set` and `delete`.
Also forward `in` in Mixin.

## 4.2 on 2022-08-05

Fix minor typo in a badge.

## 4.1 on 2022-08-05

Code reformating.
Improved documentation.
Improved checks.
Improved Makefile.

## 4.0 on 2022-03-13

Remove `StatsRedisCache` and `StatsMemCached` by moving the `hits()` method
to `RedisCache` and `MemCached`, respectively.
The two classes still exist for upward compatibility, but are deprecated.
Improve test coverage, now only 4 not-covered lines.
Improve documentation.

## 3.0 on 2022-03-06

Use simpler `kwargs` approach for caching methods and functions.
Add a `gen` parameter for caching methods and functions.
Improve documentation.

## 2.0 on 2022-02-24

Add `cacheMethods` and `cacheFunctions`.
Improve documentation.
100% coverage test.

## 1.1.0 on 2022-01-30

Improve documentation.
Add `TwoLevelCache`.
Add 100% coverage test.

## 1.0.0 on 2022-01-29

Add `set`, `get` and `delete` forwarding to `RedisCache`, so that redis
classes can be stacked.

## 0.9.0 on 2022-01-29

Initial version extracted from another project.