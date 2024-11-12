"""
Settings for eox-core
"""
from __future__ import absolute_import, unicode_literals

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
)

SECRET_KEY = 'a-not-to-be-trusted-secret-key'


def plugin_settings(settings):
    """
    Defines eox-core settings when app is used as a plugin to edx-platform.
    See: https://github.com/openedx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    pass
