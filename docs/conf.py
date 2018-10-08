# -*- coding: utf-8 -*-

import setup as appsetup
import sys
sys.path.insert(0, '..')

extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']
source_suffix = '.rst'
master_doc = 'index'
project = u'nomad'
copyright = u'2011, Alexander Solovyov'
version = release = appsetup.config['version']
exclude_patterns = ['_build']
html_title = "%s v%s" % (project, version)
