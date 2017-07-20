from django.conf.urls import url

from . import views

app_name = "comments"


urlpatterns = [
        url(r'^thread/(?P<id>\d+)/$', views.comment_thread, name='comment_thread'),
        url(r'^delete/(?P<id>\d+)/$', views.comment_delete, name='comment_delete'),
]
