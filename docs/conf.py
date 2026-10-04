import os
project = 'SCARAB'
author = 'SCARAB contributors'
copyright = '2026, '+author
extensions = ['myst_parser']
source_suffix = {'.md': 'markdown'}
root_doc = 'index'
# Public-page allow-list keeps local manuscript drafts and research assets out.
include_patterns = ['citations.md', 'cli-reference.md', 'development.md', 'documentation.md', 'index.md', 'inputs.md', 'installation.md', 'outputs.md', 'parameters.md', 'quickstart.md', 'resources.md', 'reviewer-test.md', 'troubleshooting.md', 'workflow.md', 'reassembly.md']
myst_heading_anchors = 4
html_theme = 'sphinx_rtd_theme'
html_theme_options = {'collapse_navigation': False, 'navigation_depth': 2}
html_title = project+' documentation'
html_baseurl = os.environ.get('READTHEDOCS_CANONICAL_URL', '')
html_static_path = ['assets']
html_css_files = ['docs.css']
