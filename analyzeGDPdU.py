#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, argparse
import pandas as pd
import numpy as np

programVersion = '1.0'
lastModified = '16-01-2021'

#
# PURPOSE: autocomplete GDPdU to allow import in MonkeyOffice
#
# AUTHOR: Jens Troetscher, JTTechConsult GmbH

# DISCLAIMER:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#
#  ProSaldo Import Settings (Import Textdateien)
#
#  Trennzeichen für Felder:         Semikolon
#  Trennzeichen für Datensätze:     LF
#  Textbregrenzung:                 keine
#  Zeichensatz:                     IsoLatin1 (Windows)
#
#   Output              ProSoldo
#   ------------  :     ------------
#   KontoSoll     :     KontoSoll
#   KontoHaben    :     KontoHaben
#   Betrag        :     Betrag
#   Datum         :     Datum
#   DateTime      :     kein Import
#   Buchungstext  :     Text
#   Steuer        :     Steuersatz

# Predefined list of income accounts to calculate total revenue
# Selection criteria: column 'Konto' must match

incomeAccounts = ['4200', '4300', '4400']

#  Counter Accounts used by enforePOS are
#  1000 - Verkauf
#  1210 - Rückgabe 'Soll/Haben-Kennzeichen'=='S', Verkauf bei  'Soll/Haben-Kennzeichen'=='H'
#  1461 - Kartentransaktionen
#  1600 - Verkauf bar
#  3786 - Einlösung Mehrzweckgutscheine
#
#  Fragen:
#  - in welchen Fällen wird 1210  als Gegenkonto benutzt?
#  - in welchen Fällen wird 1461  als Gegenkonto benutzt?
#  Beides scheinen Kartenzahlungen zu sein.
#  Oder ist 1210 eine SEPA Überweisung auf das Bankkonto?


# Datenformat des DATEV Exports

dtypeDATEV = {'Umsatz (ohne Soll/Haben-Kz)': "float64",
    'Soll/Haben-Kennzeichen': "string",
    'WKZ Umsatz': "string",
    'Kurs': "string",
    'Basis-Umsatz': "string",
    'WKZ Basis-Umsatz': "string",
    'Konto': "string",
    'Gegenkonto (ohne BU-Schlüssel)': "string",
    'BU-Schlüssel': "string",
    'Belegdatum': "string",
    'Belegfeld 1': "string", 'Belegfeld 2': "string",
    'Skonto': "string",
    'Buchungstext': "string",
    'Postensperre': "string",
    'Diverse Adressnummer': "string",
    'Geschäftspartnerbank': "string",
    'Sachverhalt': "string",
    'Zinssperre': "string",
    'Beleglink': "string",
    'Beleginfo - Art 1': "string", 'Beleginfo - Inhalt 1': "string",
    'Beleginfo - Art 2': "string", 'Beleginfo - Inhalt 2': "string",
    'Beleginfo - Art 3': "string", 'Beleginfo - Inhalt 3': "string",
    'Beleginfo - Art 4': "string", 'Beleginfo - Inhalt 4': "string",
    'Beleginfo - Art 5': "string", 'Beleginfo - Inhalt 5': "string",
    'Beleginfo - Art 6': "string", 'Beleginfo - Inhalt 6': "string",
    'Beleginfo - Art 7': "string", 'Beleginfo - Inhalt 7': "string",
    'Beleginfo - Art 8': "string", 'Beleginfo - Inhalt 8': "string",
    'KOST1 - Kostenstelle': "string",
    'KOST2 - Kostenstelle': "string",
    'Kost-Menge': "string",
    'EU-Land u. UStID': "string", 'EU-Steuersatz': "string",
    'Abw. Versteuerungsart': "string",
    'Sachverhalt L+L': "string",
    'Funktionsergänzung L+L': "string",
    'BU 49 Hauptfunktionstyp': "string",
    'BU 49 Hauptfunktionsnummer': "string",
    'BU 49 Funktionsergänzung': "string",
    'Zusatzinformation - Art 1': "string", 'Zusatzinformation- Inhalt 1': "string",
    'Zusatzinformation - Art 2': "string", 'Zusatzinformation- Inhalt 2': "string",
    'Zusatzinformation - Art 3': "string", 'Zusatzinformation- Inhalt 3': "string",
    'Zusatzinformation - Art 4': "string", 'Zusatzinformation- Inhalt 4': "string",
    'Zusatzinformation - Art 5': "string", 'Zusatzinformation- Inhalt 5': "string",
    'Zusatzinformation - Art 6': "string", 'Zusatzinformation- Inhalt 6': "string",
    'Zusatzinformation - Art 7': "string", 'Zusatzinformation- Inhalt 7': "string",
    'Zusatzinformation - Art 8': "string", 'Zusatzinformation- Inhalt 8': "string",
    'Zusatzinformation - Art 9': "string", 'Zusatzinformation- Inhalt 9': "string",
    'Zusatzinformation - Art 10': "string", 'Zusatzinformation- Inhalt 10': "string",
    'Zusatzinformation - Art 11': "string", 'Zusatzinformation- Inhalt 11': "string",
    'Zusatzinformation - Art 12': "string", 'Zusatzinformation- Inhalt 12': "string",
    'Zusatzinformation - Art 13': "string", 'Zusatzinformation- Inhalt 13': "string",
    'Zusatzinformation - Art 14': "string", 'Zusatzinformation- Inhalt 14': "string",
    'Zusatzinformation - Art 15': "string", 'Zusatzinformation- Inhalt 15': "string",
    'Zusatzinformation - Art 16': "string", 'Zusatzinformation- Inhalt 16': "string",
    'Zusatzinformation - Art 17': "string", 'Zusatzinformation- Inhalt 17': "string",
    'Zusatzinformation - Art 18': "string", 'Zusatzinformation- Inhalt 18': "string",
    'Zusatzinformation - Art 19': "string", 'Zusatzinformation- Inhalt 19': "string",
    'Zusatzinformation - Art 20': "string", 'Zusatzinformation- Inhalt 20': "string",
    'Stück': "string",
    'Gewicht': "string",
    'Zahlweise': "string",
    'Forderungsart': "string",
    'Veranlagungsjahr': "string",
    'Zugeordnete Fälligkeit': "string",
    'Skontotyp': "string",
    'Auftragsnummer': "string",
    'Buchungstyp': "string",
    'USt-Schlüssel(Anzahlungen)': "string",
    'EU-Mitgliedstaat(Anzahlungen)': "string",
    'Sachverhalt L+L(Anzahlungen)': "string",
    'EU-Steuersatz(Anzahlungen)': "string",
    'Erlöskonto(Anzahlungen)': "string",
    'Herkunft-Kz': "string",
    'Leerfeld': "string",
    'KOST-Datum': "string",
    'SEPA-Mandatsreferenz': "string",
    'Skontosperre': "string",
    'Gesellschaftername': "string",
    'Beteiligtennummer': "string",
    'Identifikationsnummer': "string",
    'Zeichnernummer': "string",
    'Postensperre bis': "string",
    'Bezeichnung SoBil-Sachverhalt': "string",
    'Kennzeichen SoBil-Buchung': "string",
    'Festschreibung': "string",
    'Leistungsdatum': "string",
    'Datum Zuord.Steuerperiode': "string"}

# Inhalt des DATEV Headers
#
# A = DATEV-Format (DTVF - von DATEV erzeugt, EXTF Fremdprogramm)
# B = Version des DATEV-Formats (141 bedeutet 1.41, aktuell ist 510 = 5.10; hat nichts mit der KARE-Version zu tun)
# C = Datenkategorie (21 = Buchungsstapel, 67 = Buchungstextkonstanten, 16 = Debitoren/Kreditoren, 20 = Kontenbeschriftungen usw.)
# D = Formatname (Buchungsstapel, Buchungstextkonstanten, Debitoren/Kreditoren, Kontenbeschriftungen usw.)
# E = Formatversion (bezogen auf Formatname)
# F = erzeugt am
# G = importiert am
# H = Herkunft (z. B. RE = wurde von KARE erzeugt)
# I = exportiert von
# J = importiert von
# K = Beraternummer
# L = Mandantennummer
# M = Wirtschaftsjahresbeginn
# N = Sachkontenlänge
# O = Datum Beginn Buchungsstapel
# P = Datum Ende Buchungsstapel
# Q = Bezeichnung (Vorlaufname, z. B. Buchungsstapel)
# R = Diktatkürzel
# S = Buchungstyp (bei Buchungsstapel = 1)
# T = Rechnungslegungszweck
# U = Festschreibung
# V = WKZ

dtypeDATEVHeader = {
    'DATEV-Format': "string",                # "EXTF"
    'Version': "int64",                      # 510
    'Datenkategorie': "int64",               # 21
    'Formatname': "string",                  # "Buchungsstapel"
    'Formatversion': "int64",                # 7
    'erzeugt am': "int64",                   # 20201105070305019
    'importiert am': "string",               # ""
    'Herkunft': "string",                    # ""
    'exportiert von': "string",              # "enforePOS"
    'importiert von': "string",              # ""
    'Beraternummer': "int64",                # 36410
    'Mandantennummer': "int64",              # 4047
    'Wirtschaftsjahresbeginn': "int64",      # 20200101
    'Sachkontenlänge': "int64",              # 4
    'Datum Beginn Buchungsstapel': "int64",  # 20200501
    'Datum Ende Buchungsstapel': "int64",    # 20200531
    'Bezeichnung': "string",                 # "Rechnungen Mai 2020"
    'Diktatkürzel': "string",                # "N4"
    'Buchungstyp': "int64",                  # 1
    'Rechnungslegungszweck': "int64",        # 0
    'Festschreibung': "int64",               # 1
    'WKZ': "string"                          # "EUR"

}

dRequiredFields = {
    'Umsatz (ohne Soll/Haben-Kz)': "float64",
    'Soll/Haben-Kennzeichen': "string",
#    'WKZ Umsatz': "string",
#    'Kurs': "string",
#    'Basis-Umsatz': "string",
#    'WKZ Basis-Umsatz': "string",
    'Konto': "string",
    'Gegenkonto (ohne BU-Schlüssel)': "string",
#    'BU-Schlüssel': "string",
    'Belegdatum': "string",
    'Belegfeld 1': "string",  # Coupon Information
#    'Belegfeld 2': "string",
#    'Skonto': "string",
    'Buchungstext': "string",
#    'Postensperre': "string",
#    'Diverse Adressnummer': "string",
#    'Geschäftspartnerbank': "string",
#    'Sachverhalt': "string",
#    'Zinssperre': "string",
#    'Beleglink': "string",
#    'Beleginfo - Art 1': "string",     # Buchungstyp
    'Beleginfo - Inhalt 1': "string",  # [Umsatz, Gutschein, ]
#    'Beleginfo - Art 2': "string",     # Verkaufskategorie
#    'Beleginfo - Inhalt 2': "string",  # [SPA, Leckeres aus unserer Küche, ...]
#    'Beleginfo - Art 3': "string",     # Produkt
    'Beleginfo - Inhalt 3': "string",   # [Pommes Frites, ...]
#    'Beleginfo - Art 4': "string",     # Menge
    'Beleginfo - Inhalt 4': "string",   # [1,2,...]
#    'Beleginfo - Art 5': "string",     # Artikelnummer
#    'Beleginfo - Inhalt 5': "string",  # (leer da wir keine vergeben haben )
#    'Beleginfo - Art 6': "string",     # Gutschein
    'Beleginfo - Inhalt 6': "string",   # [9910009058654, ...]
#    'Beleginfo - Art 7': "string",     # EAN
#    'Beleginfo - Inhalt 7': "string",  # (leer da wir keine vergeben haben )
#    'Beleginfo - Art 8': "string",     # Zugeh.Rechnung;
    'Beleginfo - Inhalt 8': "string",  # [2020/3740, ...]
#    'KOST1 - Kostenstelle': "string",
#    'KOST2 - Kostenstelle': "string",
#    'Kost-Menge': "string",
#    'EU-Land u. UStID': "string",
#    'EU-Steuersatz': "string",
#    'Abw. Versteuerungsart': "string",
#    'Sachverhalt L+L': "string",
#    'Funktionsergänzung L+L': "string",
#    'BU 49 Hauptfunktionstyp': "string",
#    'BU 49 Hauptfunktionsnummer': "string",
#    'BU 49 Funktionsergänzung': "string",
#    'Zusatzinformation - Art 1': "string",
#    'Zusatzinformation- Inhalt 1': "string",
#    'Zusatzinformation - Art 2': "string",
#    'Zusatzinformation- Inhalt 2': "string",
#    'Zusatzinformation - Art 3': "string",
    'Zusatzinformation- Inhalt 3': "string", # Coupon Information
#    'Zusatzinformation - Art 4': "string",
#    'Zusatzinformation- Inhalt 4': "string",
#    'Zusatzinformation - Art 5': "string",
#    'Zusatzinformation- Inhalt 5': "string",
#    'Zusatzinformation - Art 6': "string",
#    'Zusatzinformation- Inhalt 6': "string",
#    'Zusatzinformation - Art 7': "string",
#    'Zusatzinformation- Inhalt 7': "string",
#    'Zusatzinformation - Art 8': "string", '
#    Zusatzinformation- Inhalt 8': "string",
#    'Zusatzinformation - Art 9': "string",
#    'Zusatzinformation- Inhalt 9': "string",
#    'Zusatzinformation - Art 10': "string",
#    'Zusatzinformation- Inhalt 10': "string",
#    'Zusatzinformation - Art 11': "string",
#    'Zusatzinformation- Inhalt 11': "string",
#    'Zusatzinformation - Art 12': "string",
#    'Zusatzinformation- Inhalt 12': "string",
#    'Zusatzinformation - Art 13': "string",
#    'Zusatzinformation- Inhalt 13': "string",
#    'Zusatzinformation - Art 14': "string",
#    'Zusatzinformation- Inhalt 14': "string",
#    'Zusatzinformation - Art 15': "string",
#    'Zusatzinformation- Inhalt 15': "string",
#    'Zusatzinformation - Art 16': "string",
#    'Zusatzinformation- Inhalt 16': "string",
#    'Zusatzinformation - Art 17': "string",
#    'Zusatzinformation- Inhalt 17': "string",
#    'Zusatzinformation - Art 18': "string",
#    'Zusatzinformation- Inhalt 18': "string",
#    'Zusatzinformation - Art 19': "string",
#    'Zusatzinformation- Inhalt 19': "string",
#    'Zusatzinformation - Art 20': "string",
#    'Zusatzinformation- Inhalt 20': "string",
#    'Stück': "string",
#    'Gewicht': "string",
#    'Zahlweise': "string",
#    'Forderungsart': "string",
#    'Veranlagungsjahr': "string",
#    'Zugeordnete Fälligkeit': "string",
#    'Skontotyp': "string",
#    'Auftragsnummer': "string",
#    'Buchungstyp': "string",
#    'USt-Schlüssel(Anzahlungen)': "string",
#    'EU-Mitgliedstaat(Anzahlungen)': "string",
#    'Sachverhalt L+L(Anzahlungen)': "string",
#    'EU-Steuersatz(Anzahlungen)': "string",
#    'Erlöskonto(Anzahlungen)': "string",
#    'Herkunft-Kz': "string",
#    'Leerfeld': "string",
#    'KOST-Datum': "string",
#    'SEPA-Mandatsreferenz': "string",
#    'Skontosperre': "string",
#    'Gesellschaftername': "string",
#    'Beteiligtennummer': "string",
#    'Identifikationsnummer': "string",
#    'Zeichnernummer': "string",
#    'Postensperre bis': "string",
#    'Bezeichnung SoBil-Sachverhalt': "string",
#    'Kennzeichen SoBil-Buchung': "string",
#    'Festschreibung': "string",
#    'Leistungsdatum': "string",
#    'Datum Zuord.Steuerperiode': "string"
}


# read the DATEV header from a csv file containing DATEV output
# tested with DATEV output from enforePOS

def readDATEVHeader(infile):
    colNames = list(dtypeDATEVHeader.keys())
    try:
        da = pd.read_csv(infile, sep=';', encoding='latin-1',usecols=list(range(0, len(colNames))), skiprows=None,  quotechar='"', nrows=1, names=colNames, dtype=dtypeDATEVHeader )
    except:
        print("Fehler beim Lesen des DATEV Headers von {}: {}".format(infile, sys.exc_info()[0]))
        exit(1)
    return(da)

# read csv file containing all DATEV output
# we read only those columns that are needed for output!
# tested with output from Addison
# we specifiy a format for each column (string and float)
# we are prepared to locate the required columns using their names
# Note: According to pandas documentation, it should be possible to
# specify fieldnames in the read_csv command: usecols=fieldNames
# However, this was not working at the time of writing.
# The workaround is to read the header and find out at wich position (column)
# we find the required data.

def readCSV(infile):

# Load only the column names from csv file
# Note: This will result in an empty dataframe!

    try:
        da = pd.read_csv(infile, sep=';', encoding='latin-1', skiprows=[0], nrows=0)
    except:
        print("Fehler beim Lesen des CSV Headers vom enforePOS DATEV output {}: {}".format(infile, sys.exc_info()[0]))
        exit(1)

    availableColumns = da.columns.tolist()
    fieldNames = list(dRequiredFields.keys())
    fieldPositions = []
    print ("\nPrüfe CSV Datei auf erforderliche Daten {}\n".format(str(fieldNames)))

    for element in fieldNames:
        if element in availableColumns:
            position = availableColumns.index(element)
            fieldPositions.append(position)
        else:
            print("Die Spalte {} wurde nicht gefunden".format(element))


    if len(fieldPositions) < len(fieldNames):
        print("Die CSV Datei {} kann wegen {} fehlender Spalten nicht weiterverarbeitet werden.".format(infile, len(fieldPositions) - len(fieldNames)))
        exit(1)
    else:
        print("Die Spalten {} der CSV Datei {} werden eingelesen".format(str(fieldPositions), infile))

    try:
        da = pd.read_csv(infile, sep=';', skiprows=[0,1], encoding='latin-1', decimal=",", skipinitialspace=True, usecols=fieldPositions,  names=fieldNames, dtype=dRequiredFields)
    except:
        print("Fehler beim Einlesen der Daten von der CSV Datei {}: {}".format(infile, sys.exc_info()[0]))
        exit(1)

    return(da)

# read the dataframe from csv file containing all DATEV output
# tested with DATEV output from enforePOS
# we specifiy a format for each column (mostly string)
# and use float64 for monetary amounts

def readCSV_All(infile):
    try:
        da = pd.read_csv(infile, sep=';', encoding='latin-1', skiprows=[0],  decimal=",", dtype=dtypeDATEV)
    except:
        print("Fehler beim Lesen von {}: {}".format(infile, sys.exc_info()[0]))
        exit(1)
    return(da)

# write dataframe to csv file without index.
# Note: we apply rounding when we write the csv float_format='%.2f'

def writeCSV(infile, qualifier, df):
    outfile = os.path.splitext(infile)[0] + qualifier + os.path.splitext(infile)[1]
    try:
        df.to_csv(path_or_buf=outfile, sep=';', encoding='latin-1', decimal=",", float_format='%.2f', index=False)
    except:
        print("Dataframe konnte nicht gespeichert werden {}\n".format(outfile))
        pass

    print("\nDataframe als CSV Datei gespeichert: {}".format(outfile))

# Convenience Function;

def printUniqueKonto(df, nameKonto):

    uniqueKonto = df[nameKonto].unique().to_numpy()
    uniqueKonto = np.sort(uniqueKonto)
    print("{: >10}\t\t {}".format(nameKonto, uniqueKonto))


# The following modificactions are made to the dataframe containing the DATEV Export
# 1.) Rename a few columns to simplify access
# 2.) Create columns SollKonto und HabenKonto
# DATEV Dokumentation:
# Alle Beträge in Feld Umsatz (ohne Soll/Haben-Kz) sind positiv
# und mit einem Soll/Haben-Kennzeichen versehen.
# Das Soll/Haben-Kennzeichen gibt die Richtung der Buchung an und
# bezieht sich auf das Konto, das im Feld Konto angegeben wir.
#   S = Soll
#   H = Haben
# Wenn in dieser Spalte ein "S" ausgewiesen wird erfolgt die Buchung
# in der Systematik Konto - Gegenkonto "Soll an Haben".
# Die Alternative wäre den Betrag in Transaktionen mit
# 'Soll/Haben-Kennzeichen'=='S zu invertieren.
#    da_soll['Umsatz'] = da_soll['Umsatz'].apply(lambda x: x*-1)
# Wir möchten aber Sammelbuchungen für Soll und Haben Transaktionen getrennt erzeugen.

def preprocessDataframe(da):

# Wir splitten die Transaktionen nach Soll/Haben-Kennzeichen
# und erzeugen neue Spalten SollKonto und HabenKonto.
# Wir besetzen SollKonto und Habenkonto gemäß Soll/Haben-Kennzeichen

    mask = da['Soll/Haben-Kennzeichen']=='S'
    da_soll = da[mask].copy()
    da_haben = da[~mask].copy()

    mapDict = {"Umsatz (ohne Soll/Haben-Kz)": "Umsatz", "Gegenkonto (ohne BU-Schlüssel)": "Gegenkonto"}

    da_soll = da_soll.rename(mapDict, errors="raise", axis='columns')
    da_soll['SollKonto'] = da_soll['Konto']
    da_soll['HabenKonto'] = da_soll['Gegenkonto']

    da_haben = da_haben.rename(mapDict, errors="raise", axis='columns')
    da_haben['SollKonto'] = da_haben['Gegenkonto']
    da_haben['HabenKonto'] = da_haben['Konto']

#   Wir führen die Dataframes wieder zusammen

    frames = [da_soll, da_haben]
    df = pd.concat(frames)
    df = df.sort_index()

#   Statistik und Prüfung ob die Anzahl Buchungen der im Original DF entspricht.
#   Diese würde bedeuten dass der Original DF Zeilen enthält die weder das
#   'Soll/Haben-Kennzeichen']=='S' noch das 'Soll/Haben-Kennzeichen']=='H' haben.
#   Wir treffen die Annahme dass dies nicht der Fall ist,
#   wollen aber eine Warnung ausgeben falls es doch so sein sollte.

    nSoll = da_soll.shape[0]
    nHaben = da_haben.shape[0]
    nOrigin = da.shape[0]
    nNew = df.shape[0]

    print("\n###### Informationen zum Dataframe\n")
    print("Anz. Haben Buchungen\t {:>8d}".format(nHaben))
    print("Anz. Soll Buchungen\t {:>8d}".format(nSoll))
    print("Gesamt Anz. Buchungen\t {:>8d}".format(nNew))
    if nOrigin != nNew:
        print("WARNUNG: Der DATEV Export enhält insgesamt {} Buchungen\t ".format(nOrigin))
        print("Bitte die Spalte Soll/Haben-Kennzeichen im DATEV Export prüfen ")

    print("\nDie folgenden Konten sind im Dataframe vorhanden:\n")

    printUniqueKonto(df, 'Konto')
    printUniqueKonto(df, 'Gegenkonto')
    printUniqueKonto(df, 'SollKonto')
    printUniqueKonto(df, 'HabenKonto')

#    print(df.columns.values.tolist())

    return df

# Ausgabe einer Zusammenfassung der Buchungen auf vordefinierte Ertragskonten
# Annahme ist dass das PreProcessing ausgeführt wurde!

def printSaldenErtragskonten(infile, heading, df, writeTX=False):

    grandtotal = 0.0    # Nur für Ertragskonten!

    print("\n###### Zusammenfassung der Buchungen auf vordefinierte Ertragskonten\n")
    columnNames = ['Ertragskonto', 'Saldo', 'Umsatz H', 'Umsatz S',  'Anz. H', 'Anz. S', 'Anz. Gesamt']

#    print("\n{:12} \t {:16} \t {:>12}".format('Ertragskonto', 'Anzahl Buchungen', 'Umsatz' ))

    dfs = pd.DataFrame(columns = columnNames)

    iAccounts = np.sort(incomeAccounts)

    for eKto in iAccounts:
        is_eKto = df['HabenKonto']==eKto # Haben Sammelbuchungen
        df_eKto = df[is_eKto]
        nTxH = df_eKto.shape[0]
        totalH = df_eKto.sum().values[0] # Umsatz ist der erste und einzige float64 Wert!
        grandtotal += totalH

        is_eKto = df['SollKonto']==eKto # Soll Sammelbuchungen
        df_eKto = df[is_eKto]
        nTxS = df_eKto.shape[0]
        totalS = df_eKto.sum().values[0] # Umsatz ist der erste und einzige float64 Wert!
        grandtotal -= totalS

#        print("{:12} \t {:>16} \t {:12.2f}".format(eKto, nTx, total ))
        d = {}
        d["Ertragskonto"] = eKto
        d["Umsatz H"] = totalH
        d["Umsatz S"] = - totalS
        d["Saldo"] = totalH - totalS
        d["Anz. H"] = nTxH
        d["Anz. S"] = nTxS
        d["Anz. Gesamt"] = nTxH+nTxS
        dfs = dfs.append(d, ignore_index=True)         #append row to the dataframe

    print(dfs)
    print("\n{:>12}\t{:8.2f}".format('Gesamtumsatz', grandtotal ))
#    writeCSV(infile, '_Summen-Ertragskonten' + heading, dfs)

# Ausgabe von Salden per Konto
# Annahme ist dass das PreProcessing ausgeführt wurde!
# Hinweis: Mann könnte hier runden, df_salden.round({'Umsatz':2})
# Wir runden bei der CSV Ausgabe!
# Die groupby.agg operation erzeugt einen hierarchische Namen für axis 1 (columns)
# Index ist das Gegenkonto
# Der DataFrame df_salden hat folgende columns
# print(df_salden.columns.values.tolist())
# [('Umsatz', 'sum'), ('Belegdatum', 'min'), ('Belegdatum', 'max')]
# Für die Ausgabe auf der Konsole verwenden wir die hierarchischen Namen
# Für das CSV File wollen wir nur eine Kopfzeile und mit "flachen" Spaltennamen
# Daher die Operation
# df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
# Note: we must strip the whitespace for when there is no second index.
# Danach haben wir Gegenkonto;Konto;Umsatz sum;Belegdatum min;Belegdatum max
# Wenn das Flag writeTX gesetzt ist (durch die verbose option)
# wird auch eine CSV Datei mit den selektierten Transaktionen geschrieben.

def printSaldenPerKonto(infile, heading, df, bookingYear, standardText, sReferenz, writeTX=False):


    if writeTX:
        newTX = pd.DataFrame() #creates a new dataframe that's empty

    is_haben = df['Soll/Haben-Kennzeichen']=='H'
    dfh = df[is_haben]

    uniqueHKonto = dfh['HabenKonto'].unique().to_numpy()
    uniqueHKonto = np.sort(uniqueHKonto)

    newHDF = pd.DataFrame() #creates a new dataframe that's empty

    for eKto in uniqueHKonto:
        is_eKto = dfh['HabenKonto']==eKto
        df_eKto = dfh[is_eKto]
        if writeTX:
            newTX = newTX.append(df_eKto)
        df_salden = df_eKto.groupby('SollKonto').agg({'Umsatz': "sum",'Belegdatum' : [min, max] }).reset_index()

        if not df_salden.empty:
            print("\n###### Haben-Sammelbuchungen Konto {}\n".format(eKto))
            total = df_salden['Umsatz'].sum().values[0]
            df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
            df_salden.insert(1, 'HabenKonto', eKto)
            print(df_salden)
            print("\n{: >10}  \t{}\t\t{:.2f}".format('Summe', eKto, total))
            newHDF = newHDF.append(df_salden) # Gegenkonto soll erhalten bleiben!

    is_soll = df['Soll/Haben-Kennzeichen']=='S'
    dfs = df[is_soll]

    uniqueSKonto = dfs['SollKonto'].unique().to_numpy()
    uniqueSKonto = np.sort(uniqueSKonto)

    newSDF = pd.DataFrame() #creates a new dataframe that's empty

    for eKto in uniqueHKonto:
        is_eKto = dfs['SollKonto']==eKto
        df_eKto = dfs[is_eKto]
        if writeTX:
            newTX = newTX.append(df_eKto)
        df_salden = df_eKto.groupby('HabenKonto').agg({'Umsatz': "sum",'Belegdatum' : [min, max] }).reset_index()

        if not df_salden.empty:
            print("\n###### Soll-Sammelbuchungen Konto {}\n".format(eKto))
            total = df_salden['Umsatz'].sum().values[0]
            df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
            df_salden.insert(0, 'SollKonto', eKto)
            print(df_salden)
            print("\n{: >10}  \t{}\t\t{:.2f}".format('Summe', eKto, total))
#            df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
            newSDF = newSDF.append(df_salden) # Gegenkonto soll erhalten bleiben!

#   Wir führen die Dataframes zusammen

    ndf = pd.concat([newHDF, newSDF])
    ndf = ndf.sort_index()

#   Wir erzeugen eine Spalte Datum


    ndf['Datum'] = ndf['Belegdatum max'].str[:2] + '.' + ndf['Belegdatum max'].str[2:] + '.' + bookingYear

# create a column with dtype datetime64

    ndf['DateTime'] = pd.to_datetime(ndf['Datum'], format='%d.%m.%Y')

    sText = " " + standardText.split(None, 1)[1] # spit the string and use the second part
    ndf['Text'] = "Sammelbuchung" + sText

# create a column with tax rate

    ndf['Steuer'] = '-' # add the new column and set all rows to that value

# create column with reference to DATEV Input

    ndf['Referenz'] = sReferenz

# drop columns that are no longer needed

    ndf.drop('Belegdatum max', axis=1, inplace=True)
    ndf.drop('Belegdatum min', axis=1, inplace=True)

# rename columns

    ndf = ndf.rename({"Umsatz sum": "Betrag"}, errors="raise", axis='columns')

# modify text to better describe the type of transaction

    # new text for specific transactions

    ndf.loc[(ndf['HabenKonto'] == '3320') & (ndf['SollKonto'] == '3786'), 'Text'] = "Einloesung Einzweckgutscheine" + sText
    ndf.loc[(ndf['HabenKonto'] == '3786') & (ndf['SollKonto'] == '3320'), 'Text'] = "Verkauf Einzweckgutscheine" + sText
    ndf.loc[(ndf['HabenKonto'] == '3786') & (ndf['SollKonto'] == '1210'), 'Text'] = "Verkauf Wertgutschein" + sText
    ndf.loc[(ndf['HabenKonto'] == '3786') & (ndf['SollKonto'] == '1461'), 'Text'] = "Verkauf Wertgutschein" + sText + " (Karte)"
    ndf.loc[(ndf['HabenKonto'] == '3786') & (ndf['SollKonto'] == '1600'), 'Text'] = "Verkauf Wertgutschein" + sText + " (bar)"
    ndf.loc[(ndf['HabenKonto'] == '1600') & (ndf['SollKonto'] == '6969'), 'Text'] = "Kassenueberhang" + sText
    ndf.loc[(ndf['HabenKonto'] == '6969') & (ndf['SollKonto'] == '1600'), 'Text'] = "Kassenfehlbetrag" + sText
    ndf.loc[ndf['HabenKonto'] == '1370', 'Text'] = "Trinkgelder" + sText

# create text and tax tax rate for income accounts

    dTaxProSaldo = { '4300': "USt7", '4400': "USt19" } # vor 30.06.2020 und nach 31.12.2020

    iAccounts = ['4300', '4400']

    for eKto in iAccounts:
        ndf.loc[ndf['SollKonto'] == eKto, 'Steuer'] = dTaxProSaldo[eKto]
        ndf.loc[ndf['SollKonto'] == eKto, 'Text'] = "Umsatz " + dTaxProSaldo[eKto] + sText + " (Soll)"
        ndf.loc[ndf['HabenKonto'] == eKto, 'Steuer'] = dTaxProSaldo[eKto]
        ndf.loc[ndf['HabenKonto'] == eKto, 'Text'] = "Umsatz " + dTaxProSaldo[eKto] + sText + " (Haben)"

# Apply reduced tax rates if DateTime is > '2020-6-30' <= '2020-12-31'
# This might overwrite entries made above
# This rule (hopefully) applies for a limited time only.
# We ignore the waste of resources for the sake of simplicity.

    dCoronaTaxProSaldo = { '4300': "USt5", '4400': "USt16" } # Sonderregelung 01.07.2020 bis 31.12.2020

    for eKto in iAccounts:
        ndf.loc[(ndf['SollKonto'] == eKto) & (ndf['DateTime'] > '2020-6-30') & (ndf['DateTime'] <= '2020-12-31'), 'Steuer'] = dCoronaTaxProSaldo[eKto]
        ndf.loc[(ndf['SollKonto'] == eKto) & (ndf['DateTime'] > '2020-6-30') & (ndf['DateTime'] <= '2020-12-31'), 'Text'] = "Umsatz " + dCoronaTaxProSaldo[eKto] + sText + " (Soll)"
        ndf.loc[(ndf['HabenKonto'] == eKto) & (ndf['DateTime'] > '2020-6-30') & (ndf['DateTime'] <= '2020-12-31'), 'Steuer'] = dCoronaTaxProSaldo[eKto]
        ndf.loc[(ndf['HabenKonto'] == eKto) & (ndf['DateTime'] > '2020-6-30') & (ndf['DateTime'] <= '2020-12-31'), 'Text'] = "Umsatz " + dCoronaTaxProSaldo[eKto] + sText + " (Haben)"


    writeCSV(infile, '_Sammelbuchungen' + heading, ndf)
    if writeTX:
        writeCSV(infile, '_Transaktionen' + heading, newTX)

# Beim Verkauf eines Einzweckgutscheins werden die incomeAccounts gebucht
# Beim Einlösen eines Einzweckgutscheins wird ein Transferaccount 3320 gebucht.
# Die Transaktionen enthalten die Coupon Nummer und das verkaufte Produkt und die Menge
# Die folgenden Felder sind von Interesse
# 'Belegdatum'
# 'Zusatzinformation- Inhalt 3': 'Uhrzeit'
# 'Belegfeld 1': 'Rechnungsnummer' - Kann in enforePOS aufgerufen werden
# 'Beleginfo - Inhalt 6': 'Coupon Nummer'
# 'Beleginfo - Inhalt 3': 'Produkt' - z.B. 'Sauna - Erwachsene'
# 'Beleginfo - Inhalt 4': 'Menge' - Menge des verkauften Produktes
#

def printCouponUsage(infile, heading, df, writeTX=False):

    dfC  = pd.DataFrame() #creates a new dataframe that's empty

    if writeTX:
        writeCSV(infile, '_Transaktionen' + heading, df)

    newTX = pd.DataFrame() #creates a new dataframe that's empty

    for eKto in incomeAccounts: # Coupon sold
        is_eKto = df['Konto']==eKto
        df_eKto = df[is_eKto]
        if not df_eKto.empty:
            newTX = newTX.append(df_eKto)
            daCoupon = df_eKto[['Belegdatum',
                'Zusatzinformation- Inhalt 3',
                'Umsatz',
                'Belegfeld 1',
                'Beleginfo - Inhalt 1',
                'Beleginfo - Inhalt 6',
                'Beleginfo - Inhalt 4',
                'Beleginfo - Inhalt 3',
                'Beleginfo - Inhalt 8']].copy()
            daCoupon['Transaktion'] = "Verkauf"
            dfC = dfC.append(daCoupon)

# Coupon usage

    is_vKto = df['Konto']=='3320'
    df_vKto = df[is_vKto]
    if not df_vKto.empty:
        newTX = newTX.append(df_vKto)
        daCoupon = df_vKto[['Belegdatum',
            'Zusatzinformation- Inhalt 3',
            'Umsatz',
            'Belegfeld 1',
            'Beleginfo - Inhalt 1',
            'Beleginfo - Inhalt 6',
            'Beleginfo - Inhalt 4',
            'Beleginfo - Inhalt 3',
            'Beleginfo - Inhalt 8']].copy()
        daCoupon['Transaktion'] = "Benutzung"
        dfC = dfC.append(daCoupon)

# rename the columns
    mapDict = {'Zusatzinformation- Inhalt 3': 'Uhrzeit',
            'Belegfeld 1': 'Rechnungsnummer',
            'Beleginfo - Inhalt 1': 'Buchungstyp',
            'Beleginfo - Inhalt 6': 'Coupon Nummer',
            'Beleginfo - Inhalt 8': 'Zugeh.Rechnung',
            'Beleginfo - Inhalt 3': 'Produkt',
            'Beleginfo - Inhalt 4': 'Menge' }
    dfC = dfC.rename(mapDict, errors="raise", axis='columns')

# convert column "Menge" from string to numeric
# If ‘coerce’, then invalid parsing will be set as NaN.
#    dfC["Menge"] = pd.to_numeric(dfC["Menge"], errors="coerce")

    dfC = dfC.sort_values(by=['Belegdatum', 'Uhrzeit'], ascending=True)

#    dfC = dfC.reset_index()

    print("\n###### Coupon Benutzung {}\n".format(heading))
    print(dfC)
    writeCSV(infile, '_Coupon_Benutzung' + heading, dfC)


def selectAccount(df, account):
    is_account = df['Konto']==account
    ds = df[is_account]
    return ds

def selectReceiptDate(df, receiptdate):
    is_day = df['Belegdatum']==receiptdate
    ds = df[is_day]
    return ds


def selectCoupon(df, coupon):
    if coupon.upper() == "ALL": # select all coupons!
        is_coupon = df['Beleginfo - Inhalt 6'].notnull()
    else :
        is_coupon = df['Beleginfo - Inhalt 6']==coupon
    ds = df[is_coupon]
    return ds



# Main function using argparse for commandline arguments and options
# Die Nummer des Wertgutscheins steht in Spalte "Beleginfo - Inhalt 6"
# Dies gilt sowohl bei Verkauf eines Gutscheins als auch bei Einlösung
# Beim Verkauf des Warengutscheins enthält die Spalte "Buchungstext"
# den Inhalt "Verkauf Warengutschein", Bei Einlösung "Verkauf"

def main():
    print("\n###### This is {} Version {} last modified {} ######".format(os.path.basename(sys.argv[0]), programVersion, lastModified))
    print("\nPython version is {}".format(sys.version))

    parser = argparse.ArgumentParser(description='Salden per Konto aus dem DATEV Export von enforePOS')
    parser.add_argument('-f','--file', help='Name der CSV Datei mit dem enforePOS DATEV export', required=True)
    parser.add_argument('-d','--day', help='Analyse auf Zeilen mit bestimmten Belegdatum beschränken (Format: DDMM)', required=False)
    parser.add_argument('-a','--account', help='Analyse auf Zeilen mit bestimmten Konto beschränken', required=False)
    parser.add_argument('-c','--coupon', help='Analyse auf Coupons beschränken (Coupon Nr. oder all)', required=False)
    parser.add_argument('-v','--verbose', help='Weitere Information ausgeben: Zusätzlich CSV Datei mit Transaktionen schreiben',
        required=False, action='store_true', default=False)

    args = parser.parse_args()

    dfHeader = readDATEVHeader(args.file)
    print ("\n###### DATEV Header der Datei {}\n".format(args.file))

    print ("\t{: >30} : {}".format('Bezeichnung', dfHeader['Bezeichnung'].values[0]))
    print ("\t{: >30} : {}".format('erzeugt am', dfHeader['erzeugt am'].values[0]))
    print ("\t{: >30} : {}".format('Beginn Buchungsstapel', dfHeader['Datum Beginn Buchungsstapel'].values[0]))
    print ("\t{: >30} : {}".format('Ende Buchungsstapel', dfHeader['Datum Ende Buchungsstapel'].values[0]))

    wJahr = str(dfHeader['Wirtschaftsjahresbeginn'].values[0])[:4]
    print ("\t{: >30} : {}".format('Wirtschaftsjahr', wJahr))

    sExportiertVon = str(dfHeader['exportiert von'].values[0])
    sErzeugtAm = str(dfHeader['erzeugt am'].values[0])
    sReferenz = sExportiertVon + ' - ' + sErzeugtAm

    sBuchungsText = str(dfHeader['Bezeichnung'].values[0])

    if (args.day is None and  args.account is None and  args.coupon is None):
        print ("\n###### Analyse Soll und Habenbuchungen für alle Konten")
        df = readCSV(args.file)
        dfp = preprocessDataframe(df)
        heading = 'All'
        printSaldenPerKonto(args.file, heading, dfp, wJahr, sBuchungsText, sReferenz, args.verbose)
        printSaldenErtragskonten(args.file, heading, dfp, args.verbose)
    elif (args.coupon is not None) :
        if args.coupon.upper() == "ALL": # select all coupons!
            print ("Alle Coupons")
            heading = '_Alle_Coupons'
        else :
            print ("nur Coupon {}".format(args.coupon))
            heading = '_Coupon_' + args.coupon
        df = readCSV(args.file)
        df = selectCoupon(df, args.coupon)
        dfp = preprocessDataframe(df)
        printCouponUsage(args.file, heading, dfp, args.verbose)
    else:
        print ("\n###### Analyse Soll und Habenbuchungen mit Filtern:\n")
        df = readCSV(args.file)
        heading = ''
        if (args.day is not None) :
            print ("nur Belegdatum {}".format(args.day))
            df = selectReceiptDate(df, args.day)
            heading = heading + '_Belegdatum_' + args.day
        if (args.account is not None) :
            print ("nur Konto {}".format(args.account))
            df = selectAccount(df, args.account)
            heading = heading + '_Konto_' + args.account
        dfp = preprocessDataframe(df)
        printSaldenPerKonto(args.file, heading, dfp, wJahr, sBuchungsText, sReferenz, args.verbose)
        printSaldenErtragskonten(args.file, heading, dfp, args.verbose)

    print("\n###### Programm wurde normal beendet.\n")


# Driver code
if __name__ == '__main__':
    main()
