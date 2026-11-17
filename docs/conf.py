"""Build Vael documentation with Sphinx Book Theme."""

import tomllib
from pathlib import Path

# Read the release without importing scientific dependencies during setup.
ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "pyproject.toml").open("rb") as stream:
    release = tomllib.load(stream)["project"]["version"]
version = release
project = "Vael"
author = "Rahul Kakodkar"
copyright = "2023-2026, Rahul Kakodkar"

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_togglebutton",
    "sphinx_tabs.tabs",
]
master_doc = "index"
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**/.ipynb_checkpoints",
]
myst_enable_extensions = [
    "amsmath",
    "deflist",
    "dollarmath",
    "colon_fence",
    "substitution",
]
nb_execution_mode = "off"
autosummary_generate = True
add_module_names = False
autodoc_member_order = "bysource"

html_theme = "sphinx_book_theme"
html_title = "Vael"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_context = {"default_mode": "light"}
html_theme_options = {
    "repository_url": "https://github.com/cacodcar/vael",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_edit_page_button": True,
    "use_source_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    "use_sidenotes": True,
}
