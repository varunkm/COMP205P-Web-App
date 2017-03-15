from django.conf.urls import url

from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from apiviews import *
from rest_framework.routers import SimpleRouter


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^syndicate/(?P<syn_id>[0-9]+)/$', views.syndicateView, name='syndicateView'),
    url(r'^syndicate/(?P<syn_id>[0-9]+)/manage',views.syndicateManage,name='syndicateManage'),
    url(r'^syndicate/(?P<syn_id>[0-9]+)/invest',views.invest,name='syndicateInvest'),
    url(r'^syndicate/(?P<syn_id>[0-9]+)/delete',views.syndicateDelete,name='syndicateDelete'),
    url(r'^syndicate/(?P<syn_id>[0-9]+)/messages',views.newMessage,name='newMessage'),
    url(r'^syndicate/new',views.syndicateNew,name='syndicateNew'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^api/user/(?P<pk>[0-9]+)/$', UserDetail.as_view()),
    url(r'^api/syndicate/(?P<pk>[0-9]+)/$', SyndicateDetail.as_view()),
    url(r'^api/syndicate/(?P<syndicate_pk>[0-9]+)/bonds/$', SyndicateDetail.as_view()),
    url(r'^api/syndicates/$', SyndicateList.as_view()),
    url(r'^api/accounts/$', AccountList.as_view()),
    url(r'^api/account/(?P<pk>[0-9]+)/$', AccountDetail.as_view()),
]
