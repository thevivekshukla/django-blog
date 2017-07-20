from django.conf.urls import url

from . import views

app_name = 'posts'


urlpatterns = [
    url(r'^post/new/$', views.post_create, name='post_create'),
    url(r'^(?P<slug>[\w-]+)/$', views.post_detail, name='post_detail'),
    url(r'^$', views.post_list, name='post_list'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.post_update, name='post_update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.post_delete, name='post_delete'),
    url(r'^post/draft/$', views.post_draft, name="post_draft"),
    url(r'^post/published/$', views.post_published, name="post_published"),
]
