$(document).ready(function () {
    ustaw_nav();
    ustaw_main();
});

function czysc_main() {
    $('main').empty();
}

function ustaw_main() {
    //czysc_main();
    $('main').text('strona główna - tu nic nie ma');
}

function wyslij_dane() {
    let login = $('#id_login').val();
    let haslo = $('#id_haslo').val();
    if (login === '') {
        alert('Podaj nazwę użytkownika!');
    } else if (haslo === '') {
        alert('Podaj hasło!');
    } else {
        $.post('/ajax/login/', {'login': login, 'haslo': haslo})
            .done(function(msg){
                localStorage.setItem('login', login);
                localStorage.setItem('haslo', haslo);
                $('#login').attr("onclick", "wyloguj(); return false;");
                $('#login').text("Wyloguj");
                alert('Witaj ' + login);
                ustaw_main();
            }).fail(function(xhr, status, error) {
                alert("taki użytkownik nie istnieje!");
            });
    }
}

function zaloguj() {
    czysc_main();

    $('main').html('<form method="POST">' +
        '<input type="text" name="login" id="id_login" required maxlength="254" autofocus />\n' +
        '<input type="password" name="haslo" required id="id_haslo" />\n' +
        '<button type="submit" onclick="wyslij_dane(); return false;" id="wyslij">Wyślij</button>\n'  +
        '</form>');
}

function wyloguj() {
    czysc_main();
    $('#login').attr("onclick", "zaloguj(); return false;");
    $('#login').text("Zaloguj");
    localStorage.removeItem('login');
    localStorage.removeItem('haslo');
    $('main').html('Wylogowano pomyślnie');
}


function ustaw_klikowalnosc(id, pk, pilot, lot) {
    document.getElementById(id).onclick = function () {
                            czysc_main();
                            $.getJSON("/ajax/piloci", {}, function (piloci) {
                                alert("dostalem pilotow!");
                                $('main').html('<p>Lot: ' + lot + '</p>\n' +
                                           '<p>Pilot: ' + pilot + '</p>\n' +
                                           '<div class="form-group">\n' +
                                           '<div id="lot_pk" hidden>' + pk + '</div>\n' +
                                           '<label for="pilot_pk">Przypisz załogę:</label>\n' +
                                           '<select id="pilot_pk" name="pilot_pk"></select>\n' +
                                           '</div>\n' +
                                           '<button type="submit" onclick="dodaj_pilota();" id="wyslij">Ustaw</button>\n');
                                for (let j = 0; j < piloci.length; ++j) {
                                    $('#pilot_pk').append('<option value="' + piloci[j].pk + '">'
                                        + piloci[j].fields.kapitanImie + ' ' + piloci[j].fields.kapitanNazwisko + '</option>');
                                }
                            });
                        };
}


function stworz_tabele_lotow(data) {
    $.getJSON("/ajax/loty/", {'data': data})
        .done(function (lista_lotow) {
            alert("odebralem liste lotow!");
            czysc_main();
            $('main').html('<table id="tabela_loty">\n' +
                      '<tr>\n' +
                      '<th>Skąd</th>\n' +
                      '<th>Odlot</th>\n' +
                      '<th>Dokąd</th>\n' +
                      '<th>Przylot</th>\n' +
                      '<th>Pilot</th>\n' +
                      '</tr>\n' +
                      '</table>');
            for (let i = 0; i < lista_lotow.length; ++i) {
                if (lista_lotow[i].kapitanImie != null) {
                    pilot_imie = lista_lotow[i].kapitanImie + ' (kliknij, aby zmienić)';
                }
                else {
                    pilot_imie = 'brak (kliknij, aby przypisać)';
                }
                let id = "lot_" + lista_lotow[i].pk;
                $('#tabela_loty').append('<tr>\n' +
                                     '<td>' + lista_lotow[i].fields.poczatek_lotnisko + '</td>\n' +
                                     '<td>' + lista_lotow[i].fields.poczatek_czas + '</td>\n' +
                                     '<td>' + lista_lotow[i].fields.koniec_lotnisko + '</td>\n' +
                                     '<td>' + lista_lotow[i].fields.koniec_czas+ '</td>\n' +
                                     '<td id="' + id + '">' + pilot_imie + '</td>\n' +
                                     '</tr>');
                let pk = lista_lotow[i].pk;
                let lot = lista_lotow[i].fields.poczatek_lotnisko + ' (' + lista_lotow[i].fields.poczatek_czas + ') -> '
                    + lista_lotow[i].fields.koniec_lotnisko + '( ' + lista_lotow[i].fields.koniec_czas + ')';
                let pilot = lista_lotow[i].fields.kapitanImie;
                if (pilot == null) {
                    pilot = 'brak';
                }
                ustaw_klikowalnosc(id, pk, pilot, lot);
        }})
        .fail(function () {
            alert("niestety nie odebralem listy lotow!");
        });
}

function wyslij_date() {
    let data = $('#id_data_lotu').val();
    if (data === '') {
        alert('Uzupełnij formularz!');
    }
    else {
        let login = localStorage.getItem('login');
        let haslo = localStorage.getItem('haslo');
        $.post("/ajax/login/", {'login': login, 'haslo': haslo})
            .done(function (wyn) {
                alert("zalogowany!");
                stworz_tabele_lotow(data);
            })
            .fail(function(xhr, status, error) {
                alert("najpierw się zaloguj!");
            });
    }
}

function main_piloci() {
    czysc_main();
    $('main').html('wybierz datę lotu:' +
        '<form method="POST">' +
        '<input type="date" name="data_lotu" required id="id_data_lotu" />\n' +
        '<button type="submit" onclick="wyslij_date(); return false;" id="form_wyslij">Wyślij</button>\n' +
        '</form>'
        );
}

function ustaw_nav() {
    $('nav').append('<a href="#" onclick="ustaw_main();">Strona główna\n</a>');
    $('nav').append('<a href="#" onclick="main_piloci(); return false;" id="nav_filter">Pokaż loty</a>');
    let login = localStorage.getItem('login');
    let haslo = localStorage.getItem('haslo');
    if (login !== null && haslo !== null) {
        $.post("/ajax/login/", {'login': login, 'haslo': haslo}, function (odp) {
            if (odp.istnieje === 'true') {
                $('nav').append('<a id="login" href="#" onclick="wyloguj();">Wyloguj</a>');
            }
            else {
                localStorage.removeItem('login');
                localStorage.removeItem('haslo');
                $('nav').append('<a id="login" href="#" onclick="zaloguj();">Zaloguj</a>');
            }
        });
    } else {
        localStorage.removeItem('login');
        localStorage.removeItem('haslo');
        $('nav').append('<a id="login" href="#" onclick="zaloguj();">Zaloguj</a>');
    }
}

function dodaj_pilota() {
    let pilot_pk = $('#pilot_pk').val();
    let lot_pk = parseInt($('#lot_pk').text());
    let login = localStorage.getItem('login');
    let haslo = localStorage.getItem('haslo');
    $.post("/ajax/rejestruj_pilota/", {'login': login, 'haslo': haslo, 'pilot_pk': pilot_pk, 'lot_pk': lot_pk}, function (odp) {
        if (odp.zarejestrowano === "false") {
            alert("Błąd rejestracji");
        } else {
            alert("Udało się zarejestrować pilota");
            ustaw_main();
        }
    });
}