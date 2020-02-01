from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views

app_name='accounts'

urlpatterns = [
    path('', views.index,name='index'),
    path('login/', views.logIn,name='login'),
    path('signup/', views.signUp,name='signup'),
    path('logout/', views.logOut,name='logout'),
    path('<slug:username>/', views.profile,name='profile'),
    path('<slug:username>/edit', views.edit,name='edit'),
    path('<slug:username>/store', views.store,name='store'),
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',views.activate_account,name='activate'),
    path('explore', views.explore,name='explore'),
    path('vote',views.vote,name='vote'),
    path('storeElo',views.storeElo,name='storeElo'),
    path('search',views.search,name='search'),
    path('<int:id>/detail',views.detail,name='detail')
]