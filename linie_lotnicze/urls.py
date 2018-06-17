from django.urls import path, re_path
from . import views
from django.contrib import admin

app_name = 'linie_lotnicze'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.lista_lotow, name='lista_lotow'),
    re_path(r'lot/([0-9]+)/', views.lot, name='lot'), # konkretny lot
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    re_path(r'kup_bilet/([0-9]+)/', views.kup_bilet, name='kup_bilet'),
    # ajax
    path('ajax/', views.home, name='home'),
    path('ajax/login/', views.ajax_loguj, name='ajax_login'),
    # TODO logout
    path('ajax/piloci/', views.daj_liste_pilotow, name='piloci'),
    path('ajax/loty/', views.daj_liste_lotow, name='loty'),
    path('ajax/zamien_zaloge/', views.zamien_zaloge, name='zamien_zaloge'),
    path('ajax/rejestruj_pilota/', views.rejestruj_pilota, name='rejestruj_pilota'),
]