# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')
import setup as appsetup

extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']
source_suffix = '.rst'
master_doc = 'index'
project = u'nomad'
copyright = u'2011, Alexander Solovyov'
version = release = appsetup.config['version']
exclude_patterns = ['_build']
html_title = "%s v%s" % (project, version)
