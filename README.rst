Indexator
=========

Indexator is a powerful index for quick search. Data is stored in a simple DB, like gdbm, berkelyDB or Tokyo cabinet, with a specific index format.
Indexator doesn't handle well delete, but it's very efficient for selecting and counting. Its primary target is log analysis.

http://www.facebook.com/note.php?note_id=89508453919

Install
=======

::

  easy_install -U pyparsing
  easy_install -U pytc

Usage
=====

You need a library::

  library = Library('/tmp/index.test')

and some documents::

  document = Document()
  document['name'] = 'Robert'
  document['score'] = 42
  document['tags'] = ('machin', 'truc', 'simple')
  document.set('data', inverse=False)

Document can act as a dictionnary (with string keys), or with a set when you need to specify informations. Field value can be unique or a collection.

You can now add it to the library::

  library.append(document)

And querying it::

  for document in library.documents(library.query("score:42 and tags:simple")):
    print document

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
