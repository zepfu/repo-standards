# Sphinx configuration for repo-standards

from datetime import datetime

# Project information
project = "repo-standards"
copyright = f"{datetime.now().year}, Zepfu"
author = "Zepfu"
release = "1.0.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",  # For markdown support
    "sphinx_rtd_theme",
    "sphinxcontrib.mermaid",  # For Mermaid diagrams
]

# Markdown support
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Templates
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "auto/*.md"]

# HTML output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "repo-standards Documentation"
html_short_title = "repo-standards"

# Theme options
html_theme_options = {
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
}

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# MyST Parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "tasklist",
]

# Mermaid configuration
mermaid_version = "latest"  # Use latest Mermaid.js
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: { useMaxWidth: true }
});
"""
