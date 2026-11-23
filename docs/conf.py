"""Build Vaelchi documentation with Sphinx Book Theme."""

import sys
import tomllib
from pathlib import Path

# Read the release without importing scientific dependencies during setup.
ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "pyproject.toml").open("rb") as stream:
    release = tomllib.load(stream)["project"]["version"]
version = release
project = "Vaelchi"
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
autosummary_generate = True
add_module_names = False
autodoc_member_order = "bysource"

html_title = "Vaelchi"
html_logo = "_static/vaelchi-logo-light.png"
# OpenAI Codex: follow the system theme until the visitor chooses Light or Dark.
html_theme_options = {
    # OpenAI Codex: match the project logo to the selected documentation theme.
    "logo": {
        "image_light": "_static/vaelchi-logo-light.png",
        "image_dark": "_static/vaelchi-logo-dark.png",
    },
    "repository_url": "https://github.com/cacodcar/vaelchi",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_edit_page_button": True,
    "use_source_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    "use_sidenotes": True,
}


# Import only local build configuration; package APIs come from the installation.
sys.path.insert(0, str(Path(__file__).resolve().parent / "_shared"))
from family_docs import configure

configure(globals(), Path(__file__).resolve().parent)
