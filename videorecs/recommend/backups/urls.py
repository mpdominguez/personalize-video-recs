from django.conf.urls import url

from . import views, view_detail

app_name = 'recommend'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^selectuser/$', views.selectuser, name='selectuser'),
    url(r'^(?P<user>[0-9]+)/$', view_detail.userDetail, name='userDetail'),
]
