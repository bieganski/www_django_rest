$(document).ready(function () {
    ustaw_nav();
    ustaw_main();
});

function czysc_main() {
    $('main').empty();
}

function ustaw_main() {
    //czysc_main();
    $('main').app('strona główna - tu nic nie ma');
}

function wyslij_dane() {
    let login = $('#id_login').val();
    let haslo = $('#id_haslo').val();
    if (login === '') {
        alert('Podaj nazwę użytkownika!');
    } else if (haslo === '') {
        alert('Podaj hasło!');
    } else {
        $.post("/ajax/login/", {'login': login, 'haslo': haslo}, function (odp) {
            if (odp.istnieje == 'false') {
                // alert("taki użytkownik nie istnieje!");
                $('main').append("mordo nie istnieje");
            } else {
                $('main').append("mordo istnieje");
                // localStorage.setItem('login', login);
                // localStorage.setItem('haslo', haslo);
                // $('#login').attr("onclick", "wyloguj();");
                // $('#login').text("Wyloguj");
                //alert('Witaj ' + login);
                //ustaw_main();
            }
        });
    }
}

function zaloguj() {
    czysc_main();

    $('main').html('<form method="POST">' +
        '<input type="text" name="login" id="id_login" required maxlength="254" autofocus />\n' +
        '<input type="password" name="haslo" required id="id_haslo" />\n' +
        '<button type="submit" onclick="wyslij_dane();" id="wyslij">Wyślij</button>\n'  +
        '</form>');
}

function wyloguj() {
    czysc_main();
    $('#login').attr("onclick", "zaloguj();");
    $('#login').text("Zaloguj");
    localStorage.removeItem('login');
    localStorage.removeItem('haslo');
    $('main').html('Wylogowano pomyślnie');
}



function wyslij_date() {
    let data = $('#id_data_lotu').val();
    if (data === '') {
        alert('Uzupełnij formularz!');
    }
    else {
        let login = localStorage.getItem('login');
        let haslo = localStorage.getItem('haslo');
        $.post("/ajax/login/", {'login': login, 'haslo': haslo}, function (odp) {
            let zalogowany = odp.istnieje;
            $.getJSON("/ajax/loty/", {'data': data}, function (odp2) {
                clear_main();
                $('main').html('<table id="flights">\n' +
                          '<tr>\n' +
                          '<th>Skąd</th>\n' +
                          '<th>Odlot</th>\n' +
                          '<th>Dokąd</th>\n' +
                          '<th>Przylot</th>\n' +
                          '<th>Pilot</th>\n' +
                          '</tr>\n' +
                          '</table>');
                for (let i = 0; i < odp2.length; ++i) {
                    let pilot_imie = "";
                    if (zalogowany === 'false') {
                        pilot_imie = "brak";
                        if (odp2[i].kapitanImie != null) {
                            pilot_imie = odp2[i].kapitanImie;
                        }
                    } else {
                        if (odp2[i].kapitanImie != null) {
                            pilot_imie = odp2[i].kapitanImie + ' (kliknij, aby zmienić)';
                        } else {
                            pilot_imie = 'brak (kliknij, aby przypisać)';
                        }
                    }
                    let id = "flight_" + odp2[i].pk;
                    $('#flights').append('<tr>\n' +
                                         '<td>' + odp2[i].poczatek_lotnisko + '</td>\n' +
                                         '<td>' + odp2[i].poczatek_czas + '</td>\n' +
                                         '<td>' + odp2[i].koniec_lotnisko + '</td>\n' +
                                         '<td>' + odp2[i].koniec_czas+ '</td>\n' +
                                         '<td id="' + id + '">' + pilot_imie + '</td>\n' +
                                         '</tr>');
                    if (zalogowany === 'true') {
                        let pk = odp2[i].pk;
                        let lot = odp2[i].poczatek_lotnisko + ' (' + odp2[i].poczatek_czas + ') -> ' + odp2[i].koniec_lotnisko + '( ' + data[i].koniec_czas + ')';
                        let pilot = odp2[i].kapitanImie;
                        if (pilot == null) {
                            pilot = 'brak';
                        }
                        document.getElementById(id).onclick = function () {
                            clear_main();
                            $.getJSON("/ajax/piloci/", {}, function (piloci) {
                                $('main').html('<p>Lot: ' + lot + '</p>\n' +
                                           '<p>Pilot: ' + pilot + '</p>\n' +
                                           '<div class="form-group">\n' +
                                           '<div id="flight_pk" hidden>' + pk + '</div>\n' +
                                           '<label for="pilot_pk">Przypisz załogę:</label>\n' +
                                           '<select id="pilot_pk" name="pilot_pk"></select>\n' +
                                           '</div>\n' +
                                           '<button type="submit" class="btn btn-primary" onclick="send_pilot();" id="form_send">Wyślij</button>\n');

                                for (let j = 0; j < piloci.length; ++j) {
                                    $('#pilot_pk').append('<option value="' + piloci[j].pk + '">' + piloci[j].first_name + ' ' + piloci[j].last_name + '</option>');
                                }
                            });
                        };
                    }
                }
            });
        });
    }
}

function main_piloci() {
    czysc_main();
    $('main').html('wybierz datę lotu:' +
        '<form>' +
        '<input type="date" name="data_lotu" required id="id_data_lotu" />\n' +
        '<button type="submit" onclick="wyslij_date();" id="form_wyslij">Wyślij</button>\n' +
        '</form>'
        );
}

function ustaw_nav() {
    $('nav').append('<a href="#" onclick="ustaw_main();">Strona główna\n</a>');
    $('nav').append('<a href="#" onclick="main_piloci();" id="nav_filter">Pokaż loty</a>');
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
    let lot_pk = parseInt($('#flight_pk').text());
    let login = localStorage.getItem('login');
    let haslo = localStorage.getItem('haslo');
    $.post("/ajax/rejestruj_pilota/", {'login': login, 'haslo': haslo, 'pilot_pk': pilot_pk, 'lot_pk': lot_pk}, function (odp) {
        if (odp.zarejestrowano === "false") {
            alert("Błąd rejestracji");
        } else {
            alert("Udało się zarejestrować pilota");
            main_home();
        }
    });
}