######################################
TMC Leaf Nodes code quality guidelines
######################################

***********************
Code formatting / style
***********************

Black
^^^^^
TMC Leaf Nodes uses the ``black`` code formatter to format its code. Formatting can 
be checked using the command ``make python-format``.

The CI pipeline does check that if code has been formatted using black or not.

Linting
^^^^^^^
TMC Leaf Nodes uses below libraries/utilities for linting. Linting can be checked 
using command ``make python-lint``.

* ``isort`` - It provides a command line utility, Python library and 
    plugins for various editors to quickly sort all your imports.

* ``black`` - It is used to check if the code has been blacked.

* ``flake8`` - It is used to check code base against coding style (PEP8), 
    programming errors (like “library imported but unused” and “Undefined name”),etc.

* ``pylint`` - It is looks for programming errors, helps enforcing a coding standard, 
    sniffs for code smells and offers simple refactoring suggestions.

*************
Test coverage
*************

TMC Leaf Nodes uses pytest to test its code, with the pytest-cov plugin for
measuring coverage.





