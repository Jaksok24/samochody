import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu
import pandas as pd

#Konfiguracja nagłówka strony
st.set_page_config(page_title="Budrol", page_icon=":racing_car:", layout="wide")

#Łączenie się z bazą danych
conn = sqlite3.connect("budrol.db")
c = conn.cursor()

#Klasa auta
class Auto:
    def __init__(self, pID, rejestracja, marka, model, silnik):
        self.pID = pID
        self.rejestracja = rejestracja
        self.marka = marka
        self.model = model
        self.silnik = silnik

class Wpis():
    def __init__(self, rejestracja, marka, model, usluga, dzien, cena):
        self.rejestracja = rejestracja
        self.marka = marka
        self.model = model
        self.usluga = usluga
        self.dzien = dzien
        self.cena = cena
    
#Ustawienia SideBar
with st.sidebar:
    selected = option_menu(
        menu_title = "Budrol",
        options = ["Strona główna", "Panel zarządzania", "Spis napraw"],
        icons = ["house", "pencil-square", "card-text"],
        menu_icon="car-front-fill",
        default_index = 0,
    )

#Funkcja wyciągająca dane do strony główej
def drukujDane():
    c.execute("""
            SELECT pojazdy.rejestracja, pojazdy.marka, pojazdy.model, naprawa.usluga, naprawa.dzien, naprawa.cena
            FROM pojazdy
            INNER JOIN naprawa ON pojazdy.pID=naprawa.pID
            WHERE dzien BETWEEN date('now', '-1 month') AND date('now');
              """)
    for elem in c.fetchall():
        wpis = Wpis(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5])
        st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #87CEFA; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 16%; border: 0">{wpis.dzien}</td>
                        <td style="width: 16%; border: 0">{wpis.rejestracja}</td>
                        <td style="width: 16%; border: 0;">{wpis.marka}</td>
                        <td style="width: 16%; border: 0">{wpis.model}</td>
                        <td style="width: 16%; border: 0">{wpis.cena} PLN</td>
                        <td style="width: 16%; border: 0">{wpis.usluga}</td>
                        </tr></table><br>''', unsafe_allow_html=True)

#Dodawanie aut
def dodajAuto():
    with st.container(border=True):
        daColumn = st.columns([1,1])
        with daColumn[0]:
            rejestracja = st.text_input("Tablica rejestracjna")
            nr_tel = st.text_input("Numer telefonu")
            marka = st.text_input("Marka samochodu")
            silnik = st.text_input("Silnik")
        with daColumn[1]:
            vin = st.text_input("VIN")
            wlasciciel = st.text_input("Właściciela")
            model = st.text_input("Model samochodu")
            rocznik = st.text_input("Rok produkcji")
    wprowadz_auto = st.button("Zatwierdź")
    if wprowadz_auto:
        if rejestracja and wlasciciel and nr_tel and marka and model and silnik and rocznik:
            try:    #Wprowadzanie danych do bazy danych o pojeździe
                c.execute("INSERT INTO pojazdy (rejestracja, wlasciciel, nr_tel, marka, model, silnik, rocznik, vin) VALUES (?,?,?,?,?,?,?,?)", (rejestracja, wlasciciel, nr_tel, marka, model, silnik, rocznik, vin))
                conn.commit()
                st.success("Wprowadzono dane")
            except sqlite3.Error as e:
                st.error(f"Wystąpił błąd: {e}")
        else:
            st.warning("Wprowadź wszystkie dane")

#Dodawanie napraw
def dodajNaprawe():
    auta = []   #Wyciąganie danych do selectbox'a
    c.execute("SELECT pID, rejestracja, marka, model, silnik FROM pojazdy")
    for elem in c.fetchall():
        samochod = Auto(elem[0], elem[1], elem[2], elem[3], elem[4])
        info = f"{samochod.rejestracja} | {samochod.marka} {samochod.model} | {samochod.silnik}"
        auta.append(info)
    with st.container(border=True):
        auto = st.selectbox("Wybierz auto", [row for row in auta]) #Wszystkie auta z bazy będą wyświetlanie jako option w selectbox'ie
        dzien = st.date_input("Podaj date")
        cena = st.number_input("Wprowadź cenę")
        usluga = st.text_area("Wykonana naprawa")
        uwagi = st.text_area("Uwagi")
    wprowadz_naprawe = st.button("Zatwierdz")
    if wprowadz_naprawe:
        if auto and dzien and usluga:
            try:    #Wprowadzanie danych do bazy danych o pojeździe
                c.execute("INSERT INTO naprawa (pID, dzien, cena, usluga, uwagi) VALUES (?,?,?,?,?)", (samochod.pID, dzien, cena, usluga, uwagi))
                conn.commit()
                st.success("Wprowadzono dane")
            except sqlite3.Error as e:
                st.error(f"Wystąpił błąd: {e}")
        else:
            st.warning("Wprowadź wszystkie dane")

#Pobiera wszystkie dane
def szczegoly():
    dane = []
    zapytanie = """
                SELECT pojazdy.rejestracja, pojazdy.wlasciciel, pojazdy.nr_tel, pojazdy.vin, pojazdy.marka, pojazdy.model, pojazdy.rocznik, pojazdy.silnik, naprawa.usluga, naprawa.dzien, naprawa.cena, naprawa.uwagi
                FROM pojazdy
                INNER JOIN naprawa ON pojazdy.pID=naprawa.pID
                WHERE 1=1
                """
    c.execute(zapytanie)
    for elem in c.fetchall():
        dane.append(elem)
    df = pd.DataFrame(dane, columns=("Rejestracja", "Właściciel", "Numer telefonu", "VIN", "Marka", "Model", "Rocznik", "Silnik", "Usługa", "Dzień", "Cena [PLN]", "Uwagi")) 
    return df
    
#Filtrowanie danych
def Filtr(filtr, start, koniec):
    dane = []
    zapytanie = """
                SELECT pojazdy.rejestracja, pojazdy.wlasciciel, pojazdy.nr_tel, pojazdy.vin, pojazdy.marka, pojazdy.model, pojazdy.rocznik, pojazdy.silnik, naprawa.usluga, naprawa.dzien, naprawa.cena, naprawa.uwagi
                FROM pojazdy
                INNER JOIN naprawa ON pojazdy.pID=naprawa.pID
                WHERE 1=1
                """
    if filtr:
        zapytanie += f"AND (rejestracja LIKE '%{filtr}%' OR wlasciciel LIKE '%{filtr}%' OR nr_tel LIKE '%{filtr}%' OR vin LIKE '%{filtr}%' OR marka LIKE '%{filtr}%' OR model LIKE '%{filtr}%' OR rocznik LIKE '%{filtr}%' OR silnik LIKE '%{filtr}%' OR usluga LIKE '%{filtr}%' OR dzien LIKE '%{filtr}%' OR cena LIKE '%{filtr}%' OR uwagi)"
    if start and koniec:
        zapytanie += f" AND dzien BETWEEN '{start}' AND '{koniec}'"
    c.execute(zapytanie)
    for elem in c.fetchall():
        dane.append(elem)
    df = pd.DataFrame(dane, columns=("Rejestracja", "Właściciel", "Numer telefonu", "VIN", "Marka", "Model", "Rocznik", "Silnik", "Usługa", "Dzień", "Cena [PLN]", "Uwagi")) 
    return df
    
if (selected == "Strona główna"):
    st.header("Ostatnie naprawy")
    st.divider()
    drukujDane()

if (selected == "Panel zarządzania"):
    dodaj_auto, dodaj_naprawe, edytuj_auto, edytuj_naprawe = st.tabs(["DODAJ SAMOCHÓD :car:", "DODAJ NAPRAWĘ :toolbox:", "EDYTUJ SAMOCHÓD :pencil:", "EDYTUJ NAPRAWĘ :pencil2:"])
    with dodaj_auto:
        dodajAuto()
    with dodaj_naprawe:
        dodajNaprawe()
        
if (selected == "Spis napraw"):
    with st.container(border=True):
        fcol = st.columns([1,1])
        with fcol[0]:
            filtr = st.text_input("Filtruj")
        with fcol[1]:
            fcol2 = st.columns([1,1])
            with fcol2[0]:
                start = st.date_input("Początek")
            with fcol2[1]:
                koniec = st.date_input("Koniec")
        przycisk_col = st.columns([1,1,1,1])
        with przycisk_col[0]:
            szukaj = st.button("Szukaj")
        with przycisk_col[3]:
            wyczysc = st.button("Wyczyść filtr")
    if wyczysc:
        df = szczegoly()
    if szukaj:
        df = Filtr(filtr, start, koniec)
    else:
        df = szczegoly()
    st.write(f"Filtr: {filtr}")
    st.dataframe(df, use_container_width=True)
