from django.test import TestCase
from datetime import datetime, timedelta
from .models import *
import json
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class testyREST(TestCase):
    data_czas = datetime.strptime('2018-06-17', '%Y-%m-%d')

    def setUp(self):
        for i in range(10):
            samolot = Samolot.objects.create(nr_rej=str(i), ile_miejsc=42)
            zaloga = Zaloga.objects.create(kapitanImie='Imie' + str(i), kapitanNazwisko='Nazwisko' + str(i))
            Lot.objects.create(samolot=samolot, poczatek_lotnisko='a', koniec_lotnisko='b',
                               poczatek_czas=self.data_czas + timedelta(hours=3*i),
                               koniec_czas=self.data_czas + timedelta(hours=3*(i+2)), zaloga=zaloga)


    def test_zmien_pilotow_kod(self):
        User.objects.create_user(username='admin', password='admin111')
        response = self.client.get('/ajax/zamien_zaloge', data={
            'login': 'admin',
            'haslo': 'admin111',
            'pilot_pk': 1,
            'lot_pk': 5
        })
        self.assertEqual(response.status_code, 301) # redirect

    def test_zmien_pilotow_poprawnosc(self):
        User.objects.create_user(username='admin', password='admin111')
        response = self.client.post('/ajax/zamien_zaloge/', data={
            'login': 'admin',
            'haslo': 'admin111',
            'pilot_pk': 1,
            'lot_pk': 6,
        })
        self.assertEqual(1, Lot.objects.get(pk=6).zaloga.pk)

    def test_user_istnieje(self):
        try:
            odp = self.client.post('ajax/ajax_loguj/', {
                'login': 'admin',
                'haslo': 'admin111',
            })
        except Exception as e:
            self.assertEqual(1, 0)


class SeleniumTest(StaticLiveServerTestCase):
    date = datetime.strptime('2018-06-17', '%Y-%m-%d')

    def testSelenium(self):
        User.objects.create_user(username='admin', password='admin111')
        Pasazer.objects.create(imie='pas', nazwisko='azer')
        for i in range(10):
            samolot = Samolot.objects.create(nr_rej=str(i), ile_miejsc=42)
            samolot.save()
            zaloga= Zaloga.objects.create(kapitanImie='pil' + str(i), kapitanNazwisko='ot' + str(i))
            zaloga.save()
            lot = Lot.objects.create(samolot=samolot, poczatek_lotnisko='a', koniec_lotnisko='b', poczatek_czas=self.date + timedelta(hours=3 * i),
                                     koniec_czas=self.date + timedelta(hours=3 * (i + 2)), zaloga=zaloga)
            lot.save()

        driver = WebDriver()

        driver.get('{}/static/linie_lotnicze/strona.html'.format(self.live_server_url))
        driver.find_element_by_id('login').click()
        driver.find_element_by_id('id_login').send_keys('admin')
        driver.find_element_by_id('id_haslo').send_keys('admin111')
        driver.find_element_by_id('wyslij').click()

        popup = driver.switch_to.alert
        popup.accept()

        driver.find_element_by_id('nav_piloci').click()
        driver.find_element_by_id('id_data_lotu').send_keys('2018-06-17')
        driver.find_element_by_id('form_wyslij').click()
        driver.find_elements_by_xpath('//td')[9].click()
        Select(driver.find_element_by_id('pilot_pk')).select_by_value('1')
        driver.find_element_by_id('wyslij').click()

        popup = driver.switch_to.alert
        self.assertIn("nie powiodło", popup.text)
        popup.accept()

        Select(driver.find_element_by_id('pilot_pk')).select_by_value('2')
        driver.find_element_by_id('wyslij').click()

        popup = driver.switch_to.alert
        self.assertIn("Udało się", popup.text)
        popup.accept()

        driver.close()
