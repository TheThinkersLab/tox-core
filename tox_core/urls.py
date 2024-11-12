""" urls.py """

from django.urls import re_path

from tox_core import views

app_name = 'tox_core'  # pylint: disable=invalid-name

urlpatterns = [
    re_path(r'^tox-info$', views.info_view, name='tox-info'),
]
