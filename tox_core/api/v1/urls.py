""" urls.py """

from django.urls import path

from tox_core.api.v1 import views

app_name = 'tox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path('course-ids/', views.CourseIdListView.as_view(), name='course-ids-list'),
]
