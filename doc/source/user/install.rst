.. _install:

Installation of Motra
=====================

This part of the documentation covers the installation of Motra.

Using pip
---------

To install Motra, simply run this simple command in your terminal of choice::

    $ pip install motra


From the Source Code
--------------------

Motra is actively developed on `Github <https://github.com/pyecore/motra>`_.

You can either clone the public repository::

    $ git clone git://github.com/pyecore/motra.git

Or, download the `tarball <https://github.com/pyecore/motra/tarball/master>`_::

    $ curl -OL https://github.com/pyecore/motra/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your own Python
package, or install it into your site-packages easily::

    $ cd motra
    $ pip install .


Dependencies
------------

The dependencies required by pyecore are:

* pyecore which is used for the metamodeling support (modeling/metamodeling...),
* Mako which is used as basis for the model to text transformations.

These dependencies are directly installed if you choose to use ``pip``.
