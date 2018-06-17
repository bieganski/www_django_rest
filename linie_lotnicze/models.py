from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Zaloga(models.Model):
    kapitanImie = models.CharField(max_length=30)
    kapitanNazwisko = models.CharField(max_length=50)

    class Meta:
        unique_together = ['kapitanImie', 'kapitanNazwisko']

    def __str__(self):
        return "Zaloga %s %s" % (self.kapitanImie, self.kapitanNazwisko)


class Samolot(models.Model):
    nr_rej = models.CharField(max_length=50, primary_key=True)
    ile_miejsc = models.IntegerField()

    def clean(self):
        if self.ile_miejsc < 1:
            raise ValidationError("Ilośc miejsc musi być dodania!")

    def __str__(self):
        return "Samolot %s" % self.nr_rej


class Pasazer(models.Model):
    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=50)

    class Meta:
        unique_together = ('imie', 'nazwisko') # kluczem jest para

    def __str__(self):
        return 'Pasazer %s %s' % (self.imie, self.nazwisko)

class Lot(models.Model):
    poczatek_lotnisko = models.CharField(max_length=255)
    koniec_lotnisko = models.CharField(max_length=255)
    poczatek_czas = models.DateTimeField()
    koniec_czas = models.DateTimeField()
    samolot = models.ForeignKey(Samolot, on_delete=models.CASCADE)
    zaloga = models.ForeignKey(Zaloga, on_delete=models.CASCADE, blank=True, null=True)
    # na poczatku zaloga moze byc niezainicjalizowana

    def clean(self):
        if self.poczatek_czas >= self.koniec_czas:
            raise ValidationError("Ujemny czas lotu!")
        for jakis_lot in Lot.objects.filter(samolot=self.samolot).exclude(id=self.id):
            if jakis_lot.poczatek_czas <= self.poczatek_czas <= jakis_lot.koniec_czas \
                    or jakis_lot.poczatek_czas <= self.koniec_czas <= jakis_lot.koniec_czas:
                raise ValidationError("Dwa loty w jednym czasie!")
        if Zaloga is not None:
            lotyZalogi = Lot.objects.filter(zaloga=self.zaloga)
            loty1 = lotyZalogi.filter(poczatek_czas > self.poczatek_czas and poczatek_czas < self.koniec_czas)
            loty2 = lotyZalogi.filter(koniec_czas < self.koniec_czas and koniec_czas > self.poczatek_czas)
            if loty1.count() + loty2.count() > 0:
                raise ValidationError("Zaloga nie moze sie rozdwoić!")

        lotyDanegoDnia = Lot.objects.filter(poczatek_czas__day=self.poczatek_czas.day)
        if lotyDanegoDnia.values('pk').distinct().count() == 4:
            raise ValidationError("Samolot nie może latać 4 razy dziennie!")

    def __str__(self):
        return 'Lot z %s do %s o starcie %s' % (self.poczatek_lotnisko, self.koniec_lotnisko,
                                                self.poczatek_czas.__str__())


class Bilet(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    pasazer = models.ForeignKey(Pasazer, on_delete=models.CASCADE)

    def clean(self):
        kupioneBilety = Bilet.objects.filter(lot=self.lot).count()
        miejsca = Lot.objects.get(pk=self.lot.pk).samolot.ile_miejsc
        if kupioneBilety == miejsca:
            raise ValidationError("Brak wolnych miejsc na ten lot!")

