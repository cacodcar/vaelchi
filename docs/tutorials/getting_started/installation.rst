Installation
============

Vaelchi requires Python 3.12 or newer. Its runtime dependencies are NumPy,
pandas, SciPy, and scikit-learn.

Install Vaelchi from PyPI in a virtual environment:

.. code-block:: console

   python -m venv .venv
   source .venv/bin/activate
   python -m pip install vaelchi
   python -c "import vaelchi; print(vaelchi.__version__)"

The version check prints the installed version. On Windows, activate the
environment with ``.venv\Scripts\activate`` instead.

For an editable development installation, clone the repository and install the
optional tools:

.. code-block:: console

   git clone https://github.com/cacodcar/vaelchi.git
   cd vaelchi
   python -m pip install -e '.[test,quality,docs]'

Build distributions
-------------------

.. code-block:: console

   python -m build

This creates a source distribution and a wheel under ``dist/``. To install the
wheel into a separate environment:

.. code-block:: console

   python -m pip install dist/vaelchi-0.2.0-py3-none-any.whl

Building distributions does not publish them.
