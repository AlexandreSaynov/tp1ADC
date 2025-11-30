# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Macrohard Teams'
copyright = '2025, Alexandre Saynov, Sergiy Iurchenko'
author = 'Alexandre Saynov, Sergiy Iurchenko'
release = '1.0'

import sys
sys.path.insert(0, '../')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'  # se quiser suportar docstrings Google/NumPy style
]

templates_path = ['_templates']
exclude_patterns = []

autodoc_mock_imports = ["sqlalchemy"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#3a7bd5",
        "color-brand-content": "#3a7bd5",
    },
    "dark_css_variables": {
        "color-brand-primary": "#6ca0ff",
        "color-brand-content": "#6ca0ff",
    }
}

html_static_path = ['_static']