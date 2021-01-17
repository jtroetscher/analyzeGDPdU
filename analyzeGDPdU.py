#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, argparse
import datetime as dt
import pandas as pd
import numpy as np

programVersion = '1.4'
lastModified = '17-01-2021'

#
# PURPOSE: autocomplete GDPdU to allow import in MonkeyOffice
#
# AUTHOR: Jens Troetscher, JTTechConsult GmbH
#
# Note: The home dir ~/Scripts/Github-Private-Repositories/analyzeGDPdU/
# is not part of our $PATH for executing shell scripts!
# don't forget to copy the final version to ~/Scripts
#
# cp ~/Scripts/Github-Private-Repositories/analyzeGDPdU/analyzeGDPdU.py ~/Scripts/analyzeGDPdU.py
#
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

defTaxKey = '-'
noTaxKey = '50'             # MwSt Satz fehlt im Input
defAccountNo = '0000'
defDebitAccountNo = '1600'

# Datenformat des GDPdU Exports

dtypeGDPdU_KI = {
    'Bon_Nummer': "string",
    'Datum': "string",
    'Uhrzeit': "string",
    'Umsatz Br.': "float64",
    'Anzahl': "string",
    'Produkt': "string",
    'Einzel VK Br.': "float64",
    'MwSt-Satz': "string",
    'MwSt': "float64",
    'Dst/Ware': "string"
}

# Alle Felder sind erforderlich und werden eingelesen

dRequiredFields = {
    'Bon_Nummer': "string",
    'Datum': "string",
    'Uhrzeit': "string",
    'Umsatz Br.': "string",
    'Anzahl': "string",
    'Produkt': "string",
    'Einzel VK Br.': "string",
    'MwSt-Satz': "string",
    'MwSt': "string",
    'Dst/Ware': "string"
}

# Dictionary MWSt Satz -> Prosaldo Steuerschlüssel

dTaxKey = {
    '0': '-',           # Umsatzsteuerfrei
    '5': 'USt5',        # Umsatzsteuer 5% (see note below)
    '7': 'USt7',        # Umsatzsteuer 7%
    '16': 'USt16',      # Umsatzsteuer 16% (see note below)
    '19': 'USt19'       # Umsatzsteuer 19%
}

# Dictionary Prosaldo Steuerschlüssel -> Erlöskonto Dienstleistungen

dCAService = {
    '-': '4001',        # Umsatzsteuerfrei
    '50': '4001',       # Steuersatz nicht definiert
    'USt5': '4301',     # Umsatzsteuer 5%
    'USt7': '4301',     # Umsatzsteuer 7%
    'USt16': '4401',    # Umsatzsteuer 16%
    'USt19': '4401'     # Umsatzsteuer 19%
}

# Dictionary Prosaldo Steuerschlüssel -> Erlöskonto Waren

dCAGoods = {
    '-': '4000',        # Umsatzsteuerfrei
    '50': '4000',       # Steuersatz nicht definiert
    'USt5': '4300',     # Umsatzsteuer 5%
    'USt7': '4300',     # Umsatzsteuer 7%
    'USt16': '4400',    # Umsatzsteuer 16%
    'USt19': '4400'     # Umsatzsteuer 19%
}

# read csv file containing all GDPdU output
# we read required columns only
# we read all values as string and do the datatype conversion later
# we are prepared to locate the required columns using their names
#
# Note: According to pandas documentation, it should be possible to
# specify fieldnames in the read_csv command: usecols=fieldNames
# However, this was not working at the time of writing.
# The workaround is to read the header and find out at wich position (column)
# we find the required data.

def readCSV(infile):

# Load only the column names from csv file
# Note: This will result in an empty dataframe!

    try:
        da = pd.read_csv(infile, sep=';', encoding='latin-1', skiprows=None, nrows=0)
    except:
        print("Fehler beim Lesen des CSV Headers vom enforePOS GDPdU output {}: {}".format(infile, sys.exc_info()[0]))
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
        da = pd.read_csv(infile, sep=';', skiprows=[0], encoding='latin-1', decimal=",", usecols=fieldPositions,  names=fieldNames, dtype=dRequiredFields)
    except:
        print("Fehler beim Einlesen der Daten von der CSV Datei {}: {}".format(infile, sys.exc_info()[0]))
        exit(1)

# print first 100 lines
# uncomment for debugging only

#    print(da.head(10))

    df=da[~da['Dst/Ware'].isin(["Dienst", "Ware"])]
    if not df.empty:
        print("WARNUNG: Der GDPdU Export enhält unbekannte Dienst / Ware Kennzeichen.")
        print(da['Dst/Ware'].unique().to_numpy())
        print("Mögliche Ursache ist die Verwendung von Trennzeichen im der Spalte Produkt")
        print(df.head(10))

    return(da)

# read the dataframe from csv file containing all GDPdU output
# tested with GDPdU output from enforePOS
# we specifiy a format for each column (mostly string)
# and use float64 for monetary amounts

def readCSV_All(infile):
    try:
        da = pd.read_csv(infile, sep=';', encoding='latin-1', skiprows=[0],  decimal=",", dtype=dtypeGDPdU_KI)
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

# before converting monetary values to float, we need a cleanup the strings
# the amounts are formatted to use a thousands separator and use decimal ,
# first we replace thousands separator, then decimal , by .
# the cleaned string can be converted to float.

def convertColumnToFloat (df, cName):

    print("\tNeuer Datentyp für Spalte {} ist float".format(cName))
    df[cName] = df[cName].str.replace('.','').str.replace(',','.').astype(float)

#
# Look up the ProSaldo TaxKey,
# print warning if key is not defined.

def getProSaldoTaxKey (taxKey):

    try:
        pTaxKey = dTaxKey[taxKey]
    except KeyError:
        print("\tWARNUNG: Der Steuerschlüssel >{}< konnte nicht gefunden werden".format(taxKey))
        print("\tWARNUNG: Ersatzweise wird der Steuerschlüssel >{}< verwendet".format(noTaxKey))
        pTaxKey = noTaxKey #  Individueller USt-Schlüssel'

    return pTaxKey

#
# Look up the Credit Account for Services
# print warning if key is not defined.

def getCreditAccountServices (taxKey):

    try:
        pCreditAccount = dCAService[taxKey]
    except KeyError:
        print("\tWARNUNG: Das Gegenkonto für Services und Steuerschlüssel {} konnte nicht gefunden werden".format(taxKey))
        pCreditAccount = defAccountNo

    return pCreditAccount

#
# Look up the Credit Account for Goods
# print warning if key is not defined.

def getCreditAccountGoods (taxKey):

    try:
        pCreditAccount = dCAGoods[taxKey]
    except KeyError:
        print("\tWARNUNG: Das Gegenkonto für Waren und Steuerschlüssel {} konnte nicht gefunden werden".format(taxKey))
        pCreditAccount = defAccountNo

    return pCreditAccount


# The following modificactions are made to the dataframe containing the GDPdU Export
# 1.  strip whitespace from all strings
# 2.  Convert column 'Anzahl' to datatype integer
# 3.  Convert columns 'Umsatz Br.' 'Einzel VK Br.' 'MwSt' to datatype float
# Other than format conversions and string cleaning,
# the content of the input columns is not modified!
# The following colums are added to the dataframe:
# 4.  column name
#       'Soll/Haben',
#       'Umsatz',
#       'Konto' with default entry defDebitAccountNo
#       'Gegenkonto',
#       'St-SL',
#       'DateTime',
#       'ChangeLog'
# 5.  Fill column 'Umsatz' (datatype float). At this stage positive or negative
# 6.  fill the column 'Soll/Haben' depending on column 'Umsatz'
# 7.  fill the column 'St-SL' with ProSaldo tax rate identifier (Steuersatz)
# 8.  fill column 'Gegenkonto' depending on 'St-SL' and 'Dst/Ware'
# 9.  swap debit and credit account if debit credit indicator == "H"
# 10. invert amount in column 'Umsatz' for transaction with debit credit indicator == "H"
#     after this step the column 'Umsatz' is always positive
# 11. fill column 'DateTime' with dtype datetime64 using the columns 'Datum' and 'Uhrzeit'
# create entries in 'ChangeLog' in case of irregularities

def preprocessDataframe(da):

#    print(da.head())

    df = da.copy() # deep copy of dataframe

# strip whitespace from strings

    df_obj = df.select_dtypes(['string'])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

# print stats

    print("\n###### Informationen zum Dataframe\n")
    print("Gesamt Anz. Transaktionen\t {:>8d}".format( df.shape[0]))
    uniqueDstWare = df['Dst/Ware'].unique().to_numpy()
    print("\nDie folgenden Transaktionstypen sind im Dataframe vorhanden:\n")
    print("{}".format(uniqueDstWare))

# Insert additional Columns

    lastCol=len(dRequiredFields)
    df.insert(lastCol, 'Soll/Haben', np.NaN)
    lastCol +=1
    df.insert(lastCol, 'Umsatz', np.PZERO )
    lastCol +=1
    df.insert(lastCol, 'Konto', defDebitAccountNo)
    lastCol +=1
    df.insert(lastCol, 'Gegenkonto', np.NaN)
    lastCol +=1
    df.insert(lastCol, 'St-SL', np.NaN)
    lastCol +=1
    df.insert(lastCol, 'DateTime', np.NaN)
    lastCol +=1
    df.insert(lastCol, 'ChangeLog', np.NaN)

    print ("\n### {}\n".format("Konvertiere Datentypen"))

# Convert column 'Anzahl' to datatype integer

    print("\tNeuer Datentyp für Spalte {} ist integer".format('Anzahl'))

    df['Anzahl'] = df['Anzahl'].astype(int)

# Convert columns 'Umsatz Br.' 'Einzel VK Br.' 'MwSt' to datatype float

    convertColumnToFloat(df,'Umsatz Br.')
    convertColumnToFloat(df,'Einzel VK Br.')
    convertColumnToFloat(df,'MwSt')

# Fill column 'Umsatz' (datatype float). At this stage positive or negative

    df['Umsatz'] = df[["Einzel VK Br.", "Anzahl"]].product(axis=1)

# fill the column 'Soll/Haben' depending on column 'Umsatz'

    df['Soll/Haben'] = np.where(df['Umsatz'] >= 0, "S", "H")

# fill the column 'St-SL' with ProSaldo tax rate identifier (Steuersatz)

    print ("\n### {}\n".format("Generiere ProSaldo Steuerschlüssel"))

    uniqueTaxRate = df['MwSt-Satz'].unique().to_numpy()
    print("\tDie folgenden MwSt. Sätze sind im Dataframe vorhanden: {}\n".format(uniqueTaxRate))

    for eKey in uniqueTaxRate:
        pKey = getProSaldoTaxKey(eKey)
        df.loc[df['MwSt-Satz'] == eKey, 'St-SL'] = pKey

#  create an entry in ChangeLog that we have used a fall-back tax key.

    df.loc[df['St-SL'] == noTaxKey, 'ChangeLog'] = 'no tax key in input file'

    print ("\n### {}\n".format("Generiere ProSaldo Gegenkonten"))

# fill column 'Gegenkonto' depending on 'St-SL' and 'Dst/Ware'
# a. split transactions into service and others (goods)

    mask = df['Dst/Ware'] == 'Dienst'
    df_services = df[mask].copy()
    df_goods = df[~mask].copy()

    uniqueTaxKey = df['St-SL'].unique()
    print("Die folgenden Steuerschlüssel sind im Dataframe vorhanden: {}".format(uniqueTaxKey))

# fill column 'Gegenkonto' depending on 'St-SL' for Services

    for eKey in uniqueTaxKey:
        pAccount = getCreditAccountServices(eKey)
        df_services.loc[df['St-SL'] == eKey, 'Gegenkonto'] = pAccount

# fill column 'Gegenkonto' depending on 'St-SL' for Goods

    for eKey in uniqueTaxKey:
        pAccount = getCreditAccountGoods(eKey)
        df_goods.loc[df['St-SL'] == eKey, 'Gegenkonto'] = pAccount

#   put the dataframes back together

    frames = [df_services, df_goods]
    df = pd.concat(frames)
    df = df.sort_index()

#  swap debit and credit account if debit credit indicator == "H"

    df[['Konto','Gegenkonto']] = df[['Gegenkonto','Konto']].where(df['Soll/Haben'] == 'H', df[['Konto','Gegenkonto']].values)

#  invert amount in column 'Umsatz' for transaction with debit credit indicator == "H"

    mask = df['Soll/Haben'] == 'H'
    df.loc[mask, 'Umsatz'] = df['Umsatz'] * -1

# create a column with dtype datetime64. For the syntax of the format string
# see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

    print ("\n ### {}\n".format("Generiere kombinierte Date-Time Spalte "))

    df['DateTime'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], format='%d.%m.%Y %H:%M:%S')

# Hinweis: die Option mit infer_datetime_format=True ist erheblich langsamer!!
#
#    df['DateTime'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], infer_datetime_format=True)

#    print(df.head(10))

#  check whether we lost any transaction

    nOrigin = da.shape[0]
    nNew = df.shape[0]

    if nOrigin != nNew:
        print("WARNUNG: Der GDPdU Export enhält insgesamt {} Buchungen\t ".format(nOrigin))
        print("Bitte die Spalte Soll/Haben-Kennzeichen im GDPdU Export prüfen ")

#    print(df.columns.values.tolist())

    return df

# Purpose of printSaldenPerKonto: write summary postings for income accounts
# Assumption: PreProcessing has been done
# Output:   CSV file with summary postings.
#           If the flag writeTX is set (through the verbose option)
#           an additional CSV file with all transactions.

# Note: You could do rounding here, df_salden.round ({'Sales': 2})
# but defer it because we round off when writing the CSV output!
#
# Note: hierarchical column names after groupby.agg operation
# The groupby.agg operation creates a hierarchical name for axis 1 (columns)
# Index is the account 'Gegenkonto'
# The DataFrame df_salden has hierarchical names
# that look like the following
# [('Sales', 'sum'), ('Document date', 'min'), ('Document date', 'max')]
# use print (df_salden.columns.values.tolist ())
#
# We use the hierarchical names for the output on the console
# For the CSV file we only want a header line and with "flat" column names
# Hence the operation
# df_salden.columns = ['' .join (col) .strip () for col in df_salden.columns.values]
# Note: we must strip the whitespace for when there is no second index.

# Ausgabe einer Zusammenfassung der Buchungen auf Ertragskonten
# Annahme ist dass das PreProcessing ausgeführt wurde!

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

def printSaldenPerKonto(infile, heading, df, writeTX=False):

    if writeTX:
        newTX = pd.DataFrame() #creates a new dataframe that's empty

    mask = df['Soll/Haben'] == 'H'
    dfh = df[mask].copy()

    print("\n###### Haben-Transaktionen\n")
    print("Gesamt Anz. Haben Transaktionen\t {:>8d}".format( dfh.shape[0]))

    uniqueHKonto = dfh['Gegenkonto'].unique()
    uniqueHKonto = np.sort(uniqueHKonto)

    newHDF = pd.DataFrame() #creates a new dataframe that's empty

    for eKto in uniqueHKonto:
        is_eKto = dfh['Gegenkonto']==eKto
        df_eKto = dfh[is_eKto].copy()
        if writeTX:
            newTX = newTX.append(df_eKto)
        df_salden = df_eKto.groupby(['Konto','St-SL']).agg({'Umsatz': "sum",'DateTime' : ['min', 'max'] }).reset_index()

        if not df_salden.empty:
            print("\n###### Haben-Sammelbuchungen Konto {}\n".format(eKto))
            total = df_salden['Umsatz'].sum().values[0]
            df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
            df_salden.insert(1, 'Gegenkonto', eKto)
            print(df_salden)
            print("\n{: >8}{: >10}\t\t{:.2f}".format('Summe', eKto, total))
            newHDF = newHDF.append(df_salden) # Gegenkonto soll erhalten bleiben!

    mask = df['Soll/Haben'] == 'S'
    dfs = df[mask].copy()
    print("\n###### Soll-Transaktionen\n")

    print("Gesamt Anz. Soll Transaktionen\t {:>8d}".format( dfs.shape[0]))

    uniqueSKonto = dfs['Konto'].unique()
    uniqueSKonto = np.sort(uniqueSKonto)

    newSDF = pd.DataFrame() #creates a new dataframe that's empty

    for eKto in uniqueHKonto:
        is_eKto = dfs['Konto']==eKto
        df_eKto = dfs[is_eKto].copy()
        if writeTX:
            newTX = newTX.append(df_eKto)
        df_salden = df_eKto.groupby(['Gegenkonto','St-SL']).agg({'Umsatz': "sum",'DateTime' : ['min', 'max'] }).reset_index()

        if not df_salden.empty:
            print("\n###### Soll-Sammelbuchungen Konto {}\n".format(eKto))
            total = df_salden['Umsatz'].sum().values[0]
            df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
            df_salden.insert(0, 'Konto', eKto)
            print(df_salden)
            print("\n{: >8}{: >10}\t\t{:.2f}".format('Summe', eKto, total))
#            df_salden.columns = [' '.join(col).strip() for col in df_salden.columns.values]
            newSDF = newSDF.append(df_salden) # Gegenkonto soll erhalten bleiben!

#   Wir führen die Dataframes zusammen

    ndf = pd.concat([newHDF, newSDF])
    ndf = ndf.sort_index()

#   Wir erzeugen eine Spalte Datum

    ndf['Datum'] = ndf['DateTime max'].dt.strftime('%d.%m.%Y')
    ndf['Text'] = "Sammelbuchung" + heading

# drop columns that are no longer needed

    ndf.drop('DateTime max', axis=1, inplace=True)
    ndf.drop('DateTime min', axis=1, inplace=True)

# rename columns

    ndf = ndf.rename({"Umsatz sum": "Betrag"}, errors="raise", axis='columns')

    writeCSV(infile, heading + '_Sammelbuchungen' , ndf)
    if writeTX:
        writeCSV(infile, heading + '_Transaktionen' , newTX)

# Select a subset of the dataframe that is between two Date
# Note: The PreProcessing must run before to create the
# df['DateTime'] column

def selectReceiptDate(df, start_date, end_date):

# Make a boolean mask.
# start_date and end_date can be datetime.datetimes, np.datetime64s, pd.Timestamps, or even datetime strings:
# greater than the start date and smaller than the end date

    format = "%Y-%m-%d"

    try:
        dt.datetime.strptime(start_date, format)
        print("\tStart Date {} OK".format(start_date))
    except ValueError:
        print("\tStart Date {} format is incorrect. It should be YYYY-MM-DD".format(start_date))
        exit(1)

    try:
        dt.datetime.strptime(end_date, format)
        print("\tEnd Date   {} OK".format(end_date))
    except ValueError:
        print("\tEnd Date   {} format is incorrect. It should be YYYY-MM-DD".format(end_date))
        exit(1)

    mask = (df['DateTime'] > start_date) & (df['DateTime'] <= end_date)
    dfp = df.loc[mask].copy()
    return dfp

# Main function using argparse for commandline arguments and options
# Die Nummer des Wertgutscheins steht in Spalte "Beleginfo - Inhalt 6"
# Dies gilt sowohl bei Verkauf eines Gutscheins als auch bei Einlösung
# Beim Verkauf des Warengutscheins enthält die Spalte "Buchungstext"
# den Inhalt "Verkauf Warengutschein", Bei Einlösung "Verkauf"

def main():
    print("\n###### This is {} Version {} last modified {} ######".format(os.path.basename(sys.argv[0]), programVersion, lastModified))
    print("\nPython version is {}".format(sys.version))

    parser = argparse.ArgumentParser(description='Salden per Konto aus dem GDPdU Export von enforePOS')
    parser.add_argument('-f','--file', help='Name der CSV Datei mit dem enforePOS GDPdU export', required=True)
    parser.add_argument(
        '-p','--period',
        nargs=2,
        metavar=('start_date', 'end_date'),
        help='Analyse zwischen zwei Daten  (Format: YYYY-MM-DD YYYY-MM-DD) Datum > start_date 00:00:00 & Datum <= end_date 00:00:00',
        required=False)
    parser.add_argument('-v','--verbose', help='Weitere Information ausgeben: Zusätzlich CSV Datei mit Transaktionen schreiben',
        required=False, action='store_true', default=False)

    args = parser.parse_args()

    df = readCSV(args.file)

    if (args.period is None):
        dfp = preprocessDataframe(df)
        heading = '_All'
        writeCSV(args.file, heading + '_Import', dfp)
        printSaldenPerKonto(args.file, heading, dfp, args.verbose)
    else:
        print ("\n###### Analyse mit Filtern:\n")
        start_date, end_date = args.period
        heading = '_vom_' + start_date + '_bis_' + end_date
        print ("Periode vom {} bis {} ".format(start_date, end_date))
        dfp = preprocessDataframe(df)
        dfpp = selectReceiptDate(dfp, start_date, end_date)
        writeCSV(args.file, heading + '_Import' , dfpp)
        printSaldenPerKonto(args.file, heading, dfpp, args.verbose)

    print("\n###### Programm wurde normal beendet.\n")


# Driver code
if __name__ == '__main__':
    main()
