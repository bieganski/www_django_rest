
#
##
# URUCHOMIENIE TEGO SKRYPTU W SHELLU DJANGO WCZYTUJE BAZĘ DANYCH
##
#

from linie_lotnicze.models import Samolot, Lot
from random import randint
from datetime import datetime as dt, timedelta
from django.utils import timezone
from django.db import transaction

miasta = [str("miasto " + str(i)) for i in range(10)]


@transaction.atomic
def generuj():
    for i in range(50):
        num = 3 * i + 1
        jakisSamolot = Samolot.objects.create(nr_rej=num, ile_miejsc=randint(20, 50))
        for j in range(50):
            pocz = randint(0, 9)
            kon = randint(0, 9)
            while pocz == kon: # maja sie roznic
                kon = randint(0, 9)
            poczCzas = dt.now(tz=timezone.utc) + timedelta(days=randint(5, 111), hours=randint(0, 24))
            konCzas = poczCzas + timedelta(minutes=randint(30, 300))
            try:
                Lot.objects.create(samolot=jakisSamolot, poczatek_lotnisko=miasta[pocz], koniec_lotnisko=miasta[kon],
                                   poczatek_czas=poczCzas, koniec_czas=konCzas)
            except:
                print("cos nie tak")

generuj()
