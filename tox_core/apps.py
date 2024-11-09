# -*- coding: utf-8 -*-
""" Configuration as explained on tutorial
github.com/openedx/edx-platform/tree/master/openedx/core/djangoapps/plugins"""
from __future__ import unicode_literals

from django.apps import AppConfig


class ToxCoreConfig(AppConfig):
    """App configuration"""
    name = 'tox_core'
    verbose_name = "ThinkersLab Openedx Extensions"

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'tox-core',
                'regex': r'^tox-core/',
                'relative_path': 'urls',
            }
        },
        'settings_config': {
            'lms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
                'devstack': {'relative_path': 'settings.devstack'},
            },
        },
    }


class ToxCoreCMSConfig(ToxCoreConfig):
    """App configuration"""
    name = 'tox_core'
    verbose_name = "ThinkersLab Openedx Extensions"

    plugin_app = {
        'url_config': {
            'cms.djangoapp': {
                'namespace': 'tox-core',
                'regex': r'^tox-core/',
                'relative_path': 'urls',
            }
        },
        'settings_config': {
            'cms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }
