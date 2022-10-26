from django.urls import path
from . import views
from .views import ApiView

urlpatterns = [
    path('', views.index, name='index'),
    path('downloadCourse', ApiView.as_view())
]
