'doc' is the CAB-LAB documentation folder. Documentation is build from *.rst files using Sphinx.
index.rst is the main documentation page.

To install Sphinx run:

     > pip install Sphinx

To build the CAB-LAB documentation run:

     > cd cablab-core/doc
     > make html

or to force regeneration of docs, run:

     > cd cablab-core
     > sphinx-build -E -a -b html doc doc/_build/html

Then find the html documentation in cablab-core/doc/_build/html

More info:
    * Sphinx Tutorial: http://sphinx-doc.org/tutorial.html
    * RST Primer: http://sphinx-doc.org/rest.html#rst-primer