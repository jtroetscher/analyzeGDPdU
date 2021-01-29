# analyzeGDPdU

AUTHOR: Jens Troetscher, JTTechConsult GmbH

## DISCLAIMER:

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

## PURPOSE:

Python command-line application to
enrich transaction data stored in GDPdU export format that has been created by
the windows application `Friseur`,
a checkout program by Kühnemann Informatik,
Strassacker 10, D-87487 Wiggensbach.
The windows application `Friseur` is referred to as **KI-Kasse**.

## USAGE:

analyzeGDPdU.py is run from the command line and has been tested with
Python version 3.8.3.


```
usage: analyzeGDPdU.py [-h] -f FILE [-p start_date end_date] [-t TEXT] [-v]

optional arguments:

  -h, --help            show this help message and exit
  -f FILE, --file FILE  Name der CSV Datei mit dem KI-Kasse GDPdU export
  -p start_date end_date, --period start_date end_date
                        Analyse zwischen zwei Daten
                        (Format: YYYY-MM-DD YYYY-MM-DD)
                        Datum > start_date 00:00:00 &
                        Datum <= end_date 00:00:00
  -t TEXT, --text TEXT  Buchungstext Sammelbuchungen
  -v, --verbose         Weitere Information ausgeben:
                        Zusätzlich CSV Datei mit Transaktionen schreiben
```


If no period is specified, all transactions in the input file will be included in the analysis.
If a period is specified, `analyzeGDPdU.py`  creates
collective posting output file names
according to the following naming convention

    ${file%.*}_Sammelbuchungen_vom_2018-01-01_bis_2018-02-01

It is recommended to use a shell script to generate monthly postings from a
GDPdU export that contains transactions from a full year.
See last section for an example.

### Input:

GDPdU export file (csv-format) with the following columns

1.  Bon_Nummer
2.  Datum
3.  Uhrzeit
4.  Umsatz Br.
5.  Anzahl
6.  Produkt
7.  Einzel VK Br.
8.  MwSt-Satz
9.  MwSt
10. Dst/Ware


### format of the input file

analyzeGDPdU is expecting the following formats to be used in the input file

*   Columns are separated by `;`
*   Decimal separator is `,`
*   Quoting; not used, strings are not enclosed in quotes.
    It is assumed that strings are filtered to not include the column separator
*   **Bon_Nummer** is numeric
*   **Datum**: Date format is `DD.MM.YYYY`; example `02.01.2018`
*   **Uhrzeit**: Time format is `HH:MM:SS` in 24h format; example `16:46:22`
*   **Umsatz Br.**: revenue in EUR: decimal, not formatted to a fixed number of decimal digits. Can be positive or negative
    examples: `18`, `18,5`,
*   **Anzahl**: numeric, can be positive or negative
    examples: `1`, `-1`,  
*   **Produkt**: Textual description of the service or good.
    examples: `Milchkaffee`, `Weizen alkf. (A)`, `02:01`
*   **Einzel VK Br.**: decimal, not formatted to a fixed number of decimal digits.
*   **MwSt-Satz**: tax percentage: decimal, not formatted to a fixed number of decimal digits.
*   **MwSt**: tax amount in EUR
*   **Dst/Ware**: Identifies the type of revenue
    examples: `Dienst`, `Ware`

Note: Since the checkout program runs on Microsoft Windows,
some formats depend on the global Windows settings on the computer where the export is created.

Note: Text fields are exported unquoted. This bears the risk that the text
can contain characters that are (mis-)interpreted as column separators.
In the 2018 export we found two records out of 60.000 where this was the case.
The field "Produkt" contained a text that was entered manually!

#### sample lines of the GDPdU_export files

```
46337;02.01.2018;14:10:56;18;1;02:01;18;19;2,87;Dienst;
46338;02.01.2018;14:29:02;18,5;1;Erwachsene;18,5;19;2,95;Dienst;
46375;02.01.2018;18:48:37;11,6;1;Milchkaffee;2,6;19;1,85;Ware;
46375;02.01.2018;18:48:37;11,6;-1;Kaffee;2;19;1,85;Ware;
59322;01.07.2018;16:15:05;7,8;1;Weizen alkf. (A);3,9;19;1,25;Ware;

```

## output


analyzeGDPdU will add columns 11 and following to the input file

| No |   Input         |     Output        |  ProSoldo           |
| -- | --------------- | ----------------- |  ------------------ |  
| 1  |   Bon_Nummer    |  Bon_Nummer       |  Referenz           |
| 2  |   Datum         |  Datum            |  Datum              |
| 3  |   Uhrzeit       |  Uhrzeit          |  no Import          |
| 4  |   Umsatz Br.    |  Umsatz Br.       |  no Import          |
| 5  |   Anzahl        |  Anzahl           |  no Import          |
| 6  |   Produkt       |  Produkt          |  Text               |
| 7  |   Einzel VK Br. |  Einzel VK Br.    |  no Import          |
| 8  |   MwSt-Satz     |  MwSt-Satz        |  no Import          |
| 9  |   MwSt          |  MwSt             |  no Import          |
| 10 |   Dst/Ware      |  Dst/Ware         |  Notiz              |
| 11 |                 |  Soll/Haben       |  no Import          |
| 12 |                 |  Umsatz           |  Betrag             |
| 13 |                 |  Konto            |  KontoSoll          |
| 14 |                 |  Gegenkonto       |  KontoHaben         |
| 15 |                 |  St-SL            |  Steuersatz         |
| 16 |                 |  DateTime         |  no Import          |
| 17 |                 |  ChangeLog        |  no Import          |



## Rules for derived values in output file

### Umsatz (Turnover)

Monetary amounts derived by multiplying column `Einzel VK Br.` with `Anzahl`.
The goal is to have only positive monetary amounts in the input column `Umsatz`.

### Konto, Gegenkonto, St-SL

In the next steps of the processing, we assign accounts, set the debit credit indicator and convert the monetary amount to be always positive!
(for details see next sections)

**debit account (Konto)**

The debit account for each record is always set to `1600`
which is the standard account for the cash register in account plan SKR04.

The export data does not contain information to distinguish between cash payment and bank transfer.

**credit account and tax key (Gegenkonto)**

The debit / credit indicator for each record is created based on data
in column `MwSt-Satz` and `Dst/Ware`.

We create a subset of the dataframe to contain only transactions with
`Dst/Ware` = `Ware`.

We set the credit account by using the data in column `MwSt-Satz`
as the key and take the value from the following dictionary

```
dCAGoods = {
    '-':     '4000',   # Umsatzsteuerfrei
    '50':    '4000',   # Umsatzsteuerfrei
    'USt5':  '4300',   # Umsatzsteuer 5%
    'USt7':  '4300',   # Umsatzsteuer 7%
    'USt16': '4400',   # Umsatzsteuer 16%
    'USt19': '4400'    # Umsatzsteuer 19%
}

```
We create a subset of the dataframe to contain only transactions with
`Dst/Ware` = `Dienst`.

We set the credit account by using the data in column `MwSt-Satz`
as the key and take the value from the following dictionary


```
dCAService = {
    '-':     '4001',   # Umsatzsteuerfrei
    '50':    '4001',   # Umsatzsteuerfrei
    'USt5':  '4301',   # Umsatzsteuer 5%
    'USt7':  '4301',   # Umsatzsteuer 7%
    'USt16': '4401',   # Umsatzsteuer 16%
    'USt19': '4401'    # Umsatzsteuer 19%
}
```

We merge the dataframes and compare the number of transactions to the original dataframe.
If there is a mismatch, we issue a warning.
Such a mismatch would mean that there a records with an entry in `Dst/Ware`
that is not in the set (`Ware`,`Dienst`).

**Tax Keys in ProSaldo**

We create the tax key in column `St-SL` by using the data
in column `MwSt-Satz` as the key and take the value from the following dictionary


```
dTaxKey = {
    '0': '-',       # Umsatzsteuerfrei
    '5': 'USt5',    # Umsatzsteuer 5% (see note below)
    '7': 'USt7',    # Umsatzsteuer 7%
    '16': 'USt16'   # Umsatzsteuer 16% (see note below)
    '19': 'USt19'   # Umsatzsteuer 19%
}
```

A reduced tax rate was introduces during COVID-19 pandemie.
The normal USt7 and USt19 are valid before 30.06.2020 and after 01.01.2021.

**debit / credit indicator (Soll/Haben-Kennzeichen)**

The debit / credit indicator for each record is created based on data in column `Umsatz` according to the following rule

*   debit / credit indicator = "S" if the content of  `Umsatz` is greater or equal to zero
*   debit / credit indicator = "H" if the content of  `Umsatz` is less than zero

We consider the selling goods or service a regular transactions.
For regular transactions we set the debit / credit indicator to "S".
With debit / credit indicator = "S" the posting follows the rule
"debit to credit".

*   Konto is the debit account
*   Gegenkonto is the credit account

With debit / credit indicator = "H" the Konto and Gegenkonto will be reversed.
and the `Umsatz` amount will be inverted. In this way, we ensure that entries in `Umsatz` are always positive.

## ProSaldo Import Settings (Import Textdateien)

When importing in MonkeyOffice FIBU by ProSaldo,
use **Import Textdateien** and the following general settings

| Parameter                     |   Wert                |
| ----------------------------- | --------------------- |    
| Trennzeichen für Felder:      |  Semikolon            |
| Trennzeichen für Datensätze:  |  LF                   |
| Textbregrenzung:              |  keine                |
| Zeichensatz:                  |  IsoLatin1 (Windows)  |
