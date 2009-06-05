Indexator
=========

Indexator is a powerful index for quick search. Data is stored in a simple DB, like gdbm, berkelyDB or Tokyo cabinet, with a specific index format.
Indexator doesn't handle well delete, but it's very efficient for selecting and counting. Its primary target is log analysis.

Install
=======
easy_install -U pyparsing
easy_install -U pytc

Modules
=======

Bitset
------

A bitset is a large ordered collection of boolean. It handles booleans operations, and, or, xor, not and cardinality.
Bitset can be stored and load. Compression is handled.

http://en.wikipedia.org/wiki/Bitmap_index

Library
-------

A library handles collection of documents. A document is a collection of fields. The library stores documents and manage an inversed index.
`Tokyo Cabinet`_ handles the storage.

Log
---

A simple parser for apache formated data. **Common** and **combined** format can be used.

User-agent
----------

A fast parser to handle user-agent. Datas comes from http://browsers.garykeith.com/ .

Graph
-----

A simple wrapper to make full HTML graph with javascript and canvas only : flot_.

.. _`Tokyo Cabinet`: http://tokyocabinet.sourceforge.net/
.. _flot: http://code.google.com/p/flot/
