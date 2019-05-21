from django.urls import path, re_path
from . import views


app_name = 'cal'
urlpatterns = [

    re_path(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),

]
