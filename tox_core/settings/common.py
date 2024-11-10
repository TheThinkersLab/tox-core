"""
Settings for eox-core
"""
from __future__ import absolute_import, unicode_literals

from importlib.util import find_spec

SECRET_KEY = 'a-not-to-be-trusted-secret-key'


def plugin_settings(settings):
    """
    Defines eox-core settings when app is used as a plugin to edx-platform.
    See: https://github.com/openedx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    pass
