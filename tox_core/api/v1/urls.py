""" urls.py """

from django.urls import path

from tox_core.api.v1 import views

app_name = 'tox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('user/accounts/<int:pk>/', views.AccountView.as_view(), name='account-update'),
]
