""" urls.py """

from django.urls import re_path, include

from tox_core import views

app_name = 'tox_core'  # pylint: disable=invalid-name

urlpatterns = [
    re_path(r'^tox-info$', views.info_view, name='tox-info'),
    re_path(r'^api/', include('tox_core.api.urls', namespace='tox-api')),
]
