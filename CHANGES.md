Changes
=======

1.0 (2015-09-22)
----------------

- Split I/O classes into a reader and writer to eliminate some overhead
- Removed deprecated features - #31
- Allow `NLJStream(json_lib)` to be a string or module - #30
- Implement `NLJStream.name` - #29
- Test against and support Python 2.6 (This may not last long) - #44


0.3.2 (2015-05-21)
------------------

- Added `Stream.num_failures` - #24


0.3.1 (2015-05-20)
------------------

- Fixed broken write mode - #16


0.3 (2015-05-18)
----------------

- New `open()` function that acts as the primary frontend to the entire API.
- New `Stream()` class to handle the behind the scenes work.
- Re-worked `load/s()` and `dump/s()` to be more canonical.
