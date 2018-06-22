from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import Http404
from django.views.decorators.http import require_POST
from datetime import datetime
from django.contrib.auth import authenticate, login as login_to_session
from django.contrib.auth.views import logout as djangoLogout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.db.models import Value as V, Q, Count
from django.db.models.functions import Concat
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

def main(request):
    return render(request, 'linie_lotnicze/main.html', {})


################ ZARZĄDZANIE KONTEM UŻYTKOWNIKA ###############

# jest zrobione konto l: admin
#                     h: admin111

def login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login_to_session(request, user)
            return HttpResponse("Zalogowano pomyślnie")
        else:
            return HttpResponse("Błąd logowania")
    else: # GET
        form = LoginForm()
    return render(request, 'linie_lotnicze/login.html', locals())


def logout(request):
    if request.user.is_authenticated:
        djangoLogout(request)
        return HttpResponse("Wylogowano pomyślnie")
    else:
        return HttpResponse("Nie można wylogować")


@transaction.atomic
def register(request):
    if request.method == "POST":
        if User.objects.all().filter(username=request.POST['username']).exists():
            return HttpResponse("Taki użytkownik już istnieje!")
        else:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password']) # samo robi save
                login_to_session(request, user) # zmienilem nazwe bo sie pokrywaly
                return HttpResponse("Zarejestrowano pomyślnie!")
            return HttpResponse("Wypełnij formularz poprawnie!")
    else: # GET
        form = RegistrationForm()
        return render(request, 'linie_lotnicze/register.html', locals())


######################## OBSLUGA LOTÓW ##########################

def lista_lotow(request):
    if request.GET.get('dzien'): # wybrano konkretną datę
        data = datetime.strptime(request.GET['dzien'], '%Y-%m-%d')
        loty = Lot.objects.filter(poczatek_czas__day=data.day,
                                  poczatek_czas__month=data.month,
                                  poczatek_czas__year=data.year,
                                  ).order_by('poczatek_czas') # cos mi nie dzialalo inaczej
    else:
        loty = Lot.objects.all().order_by('poczatek_czas')
    loty = list(loty)
    return render(request, 'linie_lotnicze/main.html', locals())


def lot(request, pk_lotu):
    # szczegoly wybranego lotu
    lot = get_object_or_404(Lot, pk=pk_lotu)
    kupione_bilety = Bilet.objects.filter(lot=lot)
    wolne_miejsca = Samolot.objects.get(pk=lot.samolot.pk).ile_miejsc - kupione_bilety.count()
    return render(request, 'linie_lotnicze/lot.html', {'lot': lot,
                                                       'bilety': list(kupione_bilety),
                                                        'wolne': wolne_miejsca})


@transaction.atomic
@login_required(login_url='/login')
def kup_bilet(request, pk_lotu):
    if request.method == "POST":
        pasazer = Pasazer.objects.get_or_create(imie=request.POST['imie'],
                                            nazwisko=request.POST['nazwisko'])[0]
        Bilet.objects.create(lot=Lot.objects.get(pk=pk_lotu), pasazer=pasazer)
        return redirect('linie_lotnicze:lot', pk_lotu)
    else:
        form = PasazerForm()
    return render(request, 'linie_lotnicze/kup_bilet.html', {'form': form})




# --------------- ZADANIE 3 ------------------


def home(request):
    return render(request)

@require_POST
@csrf_exempt
def ajax_loguj(request):
    if 'login' not in request.POST or 'haslo' not in request.POST:
        raise PermissionDenied
    user = authenticate(username=request.POST['login'], password=request.POST['haslo'])
    # authenticate nie ustawia sesji (bestanowe)
    if user is None:
        raise PermissionDenied
    return HttpResponse()



def daj_liste_pilotow(request):
    response = serializers.serialize("json", Zaloga.objects.all())
    return HttpResponse(response, content_type='application/json')

def daj_liste_lotow(request):
    if request.GET['data'] is None:
        response = serializers.serialize("json", Lot.objects.none())
        return HttpResponse(response, content_type='application/json')
    data = datetime.strptime(request.GET['data'], '%Y-%m-%d')
    #return JsonResponse({"loty": Lot.objects.filter(poczatek_czas=data).order_by('poczatek_czas')})
    response = serializers.serialize("json", Lot.objects.all().order_by('poczatek_czas'))
    return HttpResponse(response, content_type='application/json')


def zalogi_data(request):
    if 'day' not in request.GET or 'month' not in request.GET or 'year' not in request.GET:
        raise PermissionDenied

    wyn = []
    loty = Lot.objects.filter(
        Q(poczatek_czas__day=request.GET['day'], poczatek_czas__month=request.GET['month'],
          poczatek_czas__year=request.GET['year']) |
        Q(koniec_czas__day=request.GET['day'], koniec_czas__month=request.GET['month'],
          koniec_czas__year=request.GET['year']))
    for lot in loty.filter(zaloga_isnull=False): # przypisana załoga
        wyn.append({'lotID': lot.pk, 'zaloga': lot.zaloga.kapitanImie + " " + lot.zaloga.kapitanNazwisko})
    return JsonResponse({'zalogi': wyn})


@require_POST
@csrf_exempt
@transaction.atomic
def zamien_zaloge(request):
    if 'lot_pk' not in request.POST or 'pilot_pk' not in request.POST\
            or 'login' not in request.POST or 'haslo' not in request.POST:
        raise PermissionDenied

    user = authenticate(username=request.POST['login'], password=request.POST['haslo'])
    if user is None:
        raise PermissionDenied

    zaloga = get_object_or_404(Zaloga, pk=request.POST['pilot_pk'])
    lot = get_object_or_404(Lot, pk=request.POST['lot_pk'])
    lot.zaloga = zaloga
    try:
        lot.full_clean()
        lot.save()
    except ValidationError as e:
        raise PermissionDenied
    return HttpResponse()
