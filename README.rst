Echidna
=======

|echidna-ci|_ |echidna-cover|_

.. |echidna-ci| image:: https://travis-ci.org/praekelt/echidna.png?branch=develop
.. _echidna-ci: https://travis-ci.org/praekelt/echidna

.. |echidna-cover| image:: https://coveralls.io/repos/praekelt/echidna/badge.png?branch=develop
.. _echidna-cover: https://coveralls.io/r/praekelt/echidna

Echidna is a horizontally scalable pubsub service that:

* allows many thousands of subscribers to connect over WebSocket_
* allows publishers to publish via a simple RESTful JSON HTTP API
* stores currently relevent notification in ZooKeeper_
* is implemented using Cyclone and Twisted_

.. _WebSocket: http://www.websocket.org/
.. _ZooKeeper: http://zookeeper.apache.org
.. _Twisted: https://twistedmatrix.com

Documentation available online at http://echidna.readthedocs.org/.


Getting started
---------------

To install in a virtualenv::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -e .

To run tests locally::

    (ve)$ trial echidna

To run a demo locally::

    (ve)$ ./demo.sh

and then open ``http://localhost:8888/`` your browser (open the URL in
multiple tabs for the full effect).

To build the docs locally::

    (ve)$ pip install Sphinx
    (ve)$ cd docs
    (ve)$ make html

You'll find the built docs in `docs/_build/index.html`


Reporting bugs
--------------

Issues can be filed in the GitHub issue tracker. Please don't use the
issue tracker for general support queries.
