Indexator
=========

Indexator is a powerful index for quick search. Data is stored in a simple DB, like gdbm, berkelyDB or Tokyo cabinet, with a specific index format.
Indexator doesn't handle well delete, but it's very efficient for selecting and counting. Its primary target is log analysis.

BitSet
------

A bitset is a large ordered collection of boolean. It handles booleans operations, and, or, xor, not and cardinality.
Bitset can be stored and load. Compression is handled.

http://en.wikipedia.org/wiki/Bitmap_index