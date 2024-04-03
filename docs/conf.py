# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("."))
import sphinx_rtd_theme

import arkfunds

# -- Project information -----------------------------------------------------

project = "arkfunds-python"
copyright = "2024, Fredrik Haarstad"
author = "Fredrik Haarstad"
release = arkfunds.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]
autoclass_content = "class"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
}
html_static_path = ["_static"]
