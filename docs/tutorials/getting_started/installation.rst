Installation
============

Vaelchi 0.1.0 requires Python 3.12 or newer. Its runtime dependencies are NumPy,
pandas, SciPy, and scikit-learn.

Clone the repository and install Vaelchi in a virtual environment:

.. code-block:: console

   git clone https://github.com/cacodcar/vaelchi.git
   cd vaelchi
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install .
   python -c "import vaelchi; print(vaelchi.__version__)"

The version printed should be ``0.1.0``. On Windows, activate the environment
with ``.venv\Scripts\activate`` instead.

For an editable development installation, use:

.. code-block:: console

   python -m pip install -e '.[test,quality,docs]'

Version 0.1.0 is available from this repository; it has not been published to PyPI.

Build distributions
-------------------

.. code-block:: console

   python -m build

This creates a source distribution and a wheel under ``dist/``. To install the
wheel into a separate environment:

.. code-block:: console

   python -m pip install dist/vaelchi-0.1.0-py3-none-any.whl

Building distributions does not publish them.
