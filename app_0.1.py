import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu

#Konfiguracja nagłówka strony
st.set_page_config(page_title="Budrol", page_icon=":racing_car:")

#Łączenie się z bazą danych
conn = sqlite3.connect("budrol.db")
c = conn.cursor()

#Klasa auta
class Auto:
    def __init__(self, rejestracja, marka, model, silnik):
        self.rejestracja = rejestracja
        self.marka = marka
        self.model = model
        self.silnik = silnik

#Ustawienia SideBar
with st.sidebar:
    selected = option_menu(
        menu_title = "Budrol",
        options = ["Strona główna", "Panel zarządzania", "Spis napraw"],
        icons = ["house", "pencil-square", "card-text"],
        menu_icon="car-front-fill",
        default_index = 0,
    )

#Pobieranie informacji o samochodach
def pobierzAuto():
    auta = []
    c.execute("SELECT rejestracja, marka, model, silnik FROM pojazdy")
    for elem in c.fetchall():
        auto = Auto(elem[0], elem[1], elem[2], elem[3])
        info = f"{auto.rejestracja} | {auto.marka} {auto.model} | {auto.silnik}"
        auta.append(info)
    return auta

#Dodawanie aut
def dodajAuto():
    with st.container(border=True):
        daColumn = st.columns([1,1])
        with daColumn[0]:
            rejestracja = st.text_input("Podaj rejestrację")
            marka = st.text_input("Podaj markę samochodu")
            silnik = st.text_input("Podaj silnik")
        with daColumn[1]:
            wlasciciel = st.text_input("Podaj właściciela")
            model = st.text_input("Podaj model samochodu")
            rocznik = st.text_input("Podaj rok produkcji")
        vin = st.text_input("Podaj VIN")
    wprowadz_auto = st.button("Zatwierdź")
    if wprowadz_auto:
        if rejestracja and wlasciciel and marka and model and silnik and rocznik:
            try:    #Wprowadzanie danych do bazy danych o pojeździe
                c.execute("INSERT INTO pojazdy (rejestracja, wlasciciel, marka, model, silnik, rocznik, vin) VALUES (?,?,?,?,?,?,?)", (rejestracja, wlasciciel, marka, model, silnik, rocznik, vin))
                conn.commit()
                st.success("Wprowadzono dane")
            except sqlite3.Error as e:
                st.error(f"Wystąpił błąd: {e}")
        else:
            st.warning("Wprowadź wszystkie dane")

#Dodawanie napraw
def dodajNaprawe():
    auta = pobierzAuto()
    with st.container(border=True):
        auto = st.selectbox("Wybierz auto", [row for row in auta]) #Wszystkie auta z bazy będą wyświetlanie jako option w selectbox'ie
        dzien = st.date_input("Podaj date")
        cena = st.number_input("Wprowadź cenę")
        usluga = st.text_area("Wykonana naprawa")
        uwagi = st.text_area("Uwagi")
    wprowadz_naprawe = st.button("Zatwierdz")
 
if (selected == "Strona główna"):
    st.header("Ostatnie wpisy")
    st.write("Tu będą wypisane ostatnie wpisy")
    
if (selected == "Panel zarządzania"):
    dodaj_auto, dodaj_naprawe, edytuj_auto, edytuj_naprawe = st.tabs(["DODAJ SAMOCHÓD :car:", "DODAJ NAPRAWĘ :toolbox:", "EDYTUJ SAMOCHÓD :pencil:", "EDYTUJ NAPRAWĘ :pencil2:"])
    with dodaj_auto:
        dodajAuto()
    with dodaj_naprawe:
        dodajNaprawe()