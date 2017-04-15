from django.conf.urls import url

from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from apiviews import *
from userapiviews import *
from syndicateapiviews import *
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

router = DefaultRouter(trailing_slash=False)
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
    url(r'^register/$', views.register, name='register'),

    # user api views (view by name, view and update logged in user, create new user, view logged in user transactions
    url(r'^api/user/name/(?P<username>[a-zA-Z0-9]+)/$', UserDetail.as_view(),name='user-detail'),
    url(r'^api/user/$',UserViewModify.as_view(),name='user-view-and-modify'),
    url(r'^api/user/create/$',UserCreate.as_view(),name='user-create'),
    url(r'^api/user/transactions/$',UserTransactions.as_view(),name='user-transactions'),
    url(r'^api/user/bonds/$',UserBonds.as_view(),name='user-bonds'),
    url(r'^api/user/haveiwon/$',UserHaveIWon.as_view(),name='user-haveiwon'),

    
    url(r'^api/syndicate/(?P<pk>[0-9]+)/$', SyndicateDetail.as_view(),name='syndicate-detail'),
    url(r'^api/syndicates/$', SyndicateList.as_view(),name='syndicate-list'),
    url(r'^api/syndicate/(?P<syndicate_pk>[0-9]+)/bonds/$', BondsList.as_view(),name='bonds-list'),
    url(r'^api/syndicate/(?P<syndicate_pk>[0-9]+)/haveiwon/$', SyndicateHaveIWon.as_view(),name='syndicate-haveiwon'),
    url(r'^api/syndicate/(?P<syndicate_pk>[0-9]+)/manage/remove_member/$', RemoveUser.as_view(),name='remove-user'),
     url(r'^api/syndicate/(?P<syndicate_pk>[0-9]+)/manage/add_member/$', AddUser.as_view(),name='add-user'),

    
    url(r'^api/accounts/$', AccountList.as_view(),name='account-list'),
    url(r'^api/account/(?P<pk>[0-9]+)/$', AccountDetail.as_view(),name='account-detail'),
    url(r'^api/account/(?P<pk>[0-9]+)/withdraw/$', AccountWithdrawal.as_view(),name='account-withdrawal'),
    url(r'^api/account/(?P<pk>[0-9]+)/deposit/$', AccountDeposit.as_view(),name='account-deposit'),
    url(r'^api/account/(?P<pk>[0-9]+)/transfer/$', AccountTransfer.as_view(),name='account-transfer'),
    url(r'^api/account/(?P<pk>[0-9]+)/transactions/$', AccountTransactions.as_view(),name='account-transactions'),

    url(r'^api/productinfo/$', ProductInfoList.as_view(),name='product-list'),

    url(r'^api/auth/',include('rest_auth.urls')),
    url(r'^api/docs/',include_docs_urls(title='Comp204P Team 18 API')),

    url(r'^api/',APIRoot.as_view()),
]


