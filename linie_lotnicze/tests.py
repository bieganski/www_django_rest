from django.test import TestCase
from datetime import datetime, timedelta
from .models import *
# from selenium.webdriver.firefox.webdriver import WebDriver
# from selenium.webdriver.support.select import Select
# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import json

class testyREST(TestCase):
    data_czas = datetime.strptime('2018-06-17', '%Y-%m-%d')

    def setUp(self):
        for i in range(10):
            samolot = Samolot.objects.create(nr_rej=str(i), ile_miejsc=42)
            zaloga = Zaloga.objects.create(kapitanImie='Imie' + str(i), kapitanNazwisko='Nazwisko' + str(i))
            Lot.objects.create(samolot=samolot, poczatek_lotnisko='a', koniec_lotnisko='b',
                               poczatek_czas=self.data_czas + timedelta(hours=3*i),
                               koniec_czas=self.data_czas + timedelta(hours=3*(i+2)), zaloga=zaloga)

    def test_daj_loty(self):
        response = self.client.get('/ajax/loty', data={
            'data': '2018-06-17'
        })
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(content), 7)

    def test_akcept_pilot(self):
        response = self.client.post('ajax/rejestruj_pilota/', data={
            'username': 'admin',
            'password': 'admin111',
            'pilot_pk': 1,
            'lot_pk': 1
        })
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['zarejestrowano'], 'true')

    def test_nieakcept_pilot(self):
        response = self.client.post('ajax/rejestruj_pilota/', data={
            'username': 'admin',
            'password': 'admin111',
            'pilot_pk': 1,
            'lot_pk': 2
        })
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['zarejestrowano'], 'false')