.. _style:

Coding Style
############

.. contents::


Introduction
============

This document describes the coding conventions used to write :mod:`itools`. If
you ever contribute a patch to :mod:`itools`, be sure your code adheres to
these rules.  When something is not specified here, follow the general
recommendations from *PEP 8*:

    http://www.python.org/peps/pep-0008.html


Language, Encoding and Filenames
================================

Here some general rules that *must* be respected, always:

* Code must be written in English.
* The source files must be encoded in UTF-8.
* The names of the modules and packages must be in lowercase.


Module structure
================

Each module is split in six sections:

* The Encoding
* The Copyright
* The License
* The Documentation String
* The Imports
* The Code

Now we are going to describe the module's heading, made up of the first five
sections.  The following code shows, as an example, the beginning of the
:file:`itools/odf/oo.py` file::

    # -*- coding: UTF-8 -*-
    # Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
    # Copyright (C) 2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
    # Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
    #
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.

    """This module provides file handlers for Open Office 1.0 documents
    (Writer, Calc and Impress).
    """

    # Import from the Standard Library
    from mimetypes import add_type

    # Import from itools
    from itools.handlers import register_handler_class
    from odf import OOFile


The Encoding
------------

Since we only use UTF-8, the first line of the module will always be::

    # -*- coding: UTF-8 -*-


The Copyright
-------------

After the encoding comes the copyright, which is made up of one or more lines
with the following structure::

    # Copyright (C) YEARS AUTHOR-NAME <AUTHOR-EMAIL>


The License
-----------

Right after the copyright statement comes a reference to the license. For
:mod:`itools` it is the *GPL* version 3, or later.


The Documentation String
------------------------

There must be a documentation string explaining what the module does. See
section :ref:`style-doc-strings` for details on how to write the documentation
strings.


The Imports
-----------

The import statements follow the module's documentation string and close the
heading. There may be import statements within the code too, but only in
exceptional cases, for example to avoid circular references.

Imports must be classified: first those from the *Standard Library*, then
those from :mod:`itools`, and finally those from other third-party packages.
Within each group the order must be alphabetical.

The example that follows comes from the :file:`itools/xml/office.py` file::

    # Import from the Standard Library
    from os.path import join as join_path
    from subprocess import call
    from tempfile import mkdtemp

    # Import from itools
    from itools import vfs
    from itools.handlers import File, register_handler_class
    from indexer import xml_to_text

Note that every section starts with the comment ``Import from ...``.  Also,
generally we import the functions, classes and constants we are going to use,
and not the whole package:

    ================================ ========================
    Good                             Bad
    ================================ ========================
    ``from tempfile import mkdtemp`` ``import tempfile``
    -------------------------------- ------------------------
    ``mkdtemp(..)``                  ``tempfile.mkdtemp(..)``
    ================================ ========================

Note that the ``import vfs`` line above shows an exception to the rule.
Another rule is not to import everything within a package:

    ================================ ==========================
    Good                             Bad
    ================================ ==========================
    ``from tempfile import mkdtemp`` ``from tempfile import *``
    ================================ ==========================


Formatting
==========


Indentation, Spaces and Line Length
-----------------------------------

Here the general rules to format the code that must always be respected:

* There must be no tabs, nowhere, never.
* Each indentation level must have four (4) spaces.
* There must be no trailing spaces in a line.
* Lines should be 79 characters wide at most.


Line Wrap
---------

The preferred way of wrapping long lines is by using Python's implied line
continuation inside parentheses, brackets and braces. If necessary, you can
add an extra pair of parentheses around an expression, but sometimes using a
backslash looks better. Make sure to indent the continued line appropriately.


One line, one statement
-----------------------

Don't put more than one statement on the same line:


**Bad**
::

    if x is True: do_something()

**Good**
::

    if x is True:
        do_something()

**Bad**
::

    do_one(); do_two()

**Good**
::

    do_one()
    do_two()


**Bad**
::

    def f(x, y): return x * y`

**Good**
::

    def f(x, y):
        return x * y


Blank lines
-----------

Separate classes with three blank lines. Separate methods and functions with
two blank lines. There is also a blank line between the class definition and
the first method definition.

Use blank lines in functions, sparingly, to indicate logical sections.



Whitespace in expressions and statements
----------------------------------------

Surround operators with one white space. There are a couple of exceptions to
this rule: first, arithmetic operators in complex mathematical expressions may
not be surrounded by a white space to make them more compact.

And the the sign ``=`` used in keyword arguments should not be surrounded by
spaces, never:

    =========================== =============================
    Good                        Bad
    =========================== =============================
    ``Document(title="hello")`` ``Document(title = "hello")``
    =========================== =============================

Never add spaces neither before nor after parentheses, brackets or braces.
The only exception is for list comprehensions, where it is allowed to add a
space after the opening bracket, and another space before the closing bracket.

The comma and colon must be followed by a space (or a new line), but never put
a space before. The only exception is for one element tuples, where the comma
must be immediately followed by the closing parentheses.  The semicolon should
never be used.


Comments
========

Comments must describe the code that follows them, and must be indented to the
same level of that code. Inline comments are not allowed; this is to say, a
comment always starts a new line.

A comment starts by a single ``#`` character followed by a space.

Comments must be written in good English (as good as the developer can write
it). This means, for example, that the first letter must be capitalized.


Naming conventions
==================

The names of *variables*, *classes*, *functions*, *methods* and *constants*
are written with one or more English words. Most of the words used are
*nouns*, *verbs*, and *adjectives*.

Abbreviations may be used, but in general it is preferred the complete word,
for example, ``language`` instead of ``lang``. When an abbreviation is not
obvious, its meaning should be explained with a comment.

The allowed naming conventions are three:

* **lower_case_with_underscores** All words are in lowercase and separated by
  an underscore. This convention is used for *variables*, *functions* and
  *methods*.
* **UPPER_CASE_WITH_UNDERSCORES** All words are in uppercase and separated by
  an underscore. Used only for *constants*.
* **CapitalizedWords** All words start by an uppercase, with the rest of the
  word in lowercase. Words are not separated by any character, the uppercase
  letters serve to visually distinguish when a new word starts. Used only for
  *classes*.


Class names
-----------

Class names are written in capitalized words. Typically they are made of nouns
and/or adjectives.


Functions and methods
---------------------

Functions and methods are written in lowercase with underscores.

They must start by a verb, and they should be followed by a complement that
clarifies what the function does. For example, it is better to spell
``set_object`` than just ``set``.


Variables
---------

Variables are written in lowercase with underscores. Most of the time they are
nouns with or without adjectives.

One letter variables may be used in mathematical expressions, for sequence
indexes, or in comprehensive lists::

    public = [ x for x in handlers if x.state == 'public' ]


Constants
---------

Constants are written in uppercase with underscores.


.. _style-doc-strings:

Documentation Strings
=====================

Follow the general recommendations from PEP 257:

    http://www.python.org/peps/pep-0257.html


Forbidden Python
================

There are several Python constructs that must be avoided... {\bf TODO}


Mesure the quality of your code with :file:`isetup-quality.py`
==============================================================

We develop a script that mesure Python source code quality.  This script help
you to identify and fix some coding style mistakes as:

* Lines with tabulators
* Lines longer than 79 characters
* Lines with trailing whitespaces
* Lines bad indented
* Bad used of exceptions
* ...

Here, you can find the list of options available:

.. code-block:: sh

    $ isetup-quality.py --help

    Usage: isetup-quality.py [OPTIONS] [FILES]

    Shows some statistics about the quality of the Python code

    Options:
      --version            show program's version number and exit
      -h, --help           show this help message and exit
      -f, --fix            makes some small improvements to  the source code (MAKE
                           A BACKUP FIRST)
      -w INT, --worse=INT  number of worse files showed, 0 for all
      -s, --show-lines     give the line of each problem found
      -g, --graph          create graphs of code quality evolution.

Here some examples of script Usage:

    +-------------------------------------------------+--------------------------------------------------+
    | Command                                         | Description                                      |
    +=================================================+==================================================+
    | ``isetup-quality.py`` ``*.py``                  | Analyse all Python files in your directory.      |
    | ``isetup-quality.py`` ``file1.py`` ``file2.py`` | Analyse the two files ``file1.py`` and           |
    |                                                 | ``file2.py``.                                    |
    +-------------------------------------------------+--------------------------------------------------+
    | ``isetup-quality.py``                           | If your project is versioned with GIT, the       |
    |                                                 | script will analyse all files versionned in your |
    |                                                 | repository.                                      |
    +-------------------------------------------------+--------------------------------------------------+
    | ``isetup-quality.py -f``                        | The script will fix automaticaly somes mistakes  |
    |                                                 | (as remove trailing whitespaces) of your         |
    |                                                 | versionned files.                                |
    +-------------------------------------------------+--------------------------------------------------+
    | ``isetup-quality.py -w 3``                      | List the 3 worses files for each category of     |
    |                                                 | problem.                                         |
    +-------------------------------------------------+--------------------------------------------------+
    | ``isetup-quality.py -s example.py``             | Will list all errors found in the file           |
    |                                                 | ``example.py``, and will give the exact line     |
    |                                                 | number at which the error is detected.           |
    +-------------------------------------------------+--------------------------------------------------+
    | ``isetup-quality.py --graph``                   | You also can generate graphics (if your project  |
    |                                                 | is versionned with GIT) representing the         |
    |                                                 | evolution of the quality of your Python code     |
    |                                                 | within the time.                                 |
    +-------------------------------------------------+--------------------------------------------------+



