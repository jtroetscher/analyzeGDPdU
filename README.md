# analyzeGDPdU# analyzeGDPdU

AUTHOR: Jens Troetscher, JTTechConsult GmbH

## DISCLAIMER:

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

## PURPOSE:

enrich transaction data stored in GDPdU export format that has been created by
the windows application `Friseur`,
a checkout program by Kühnemann Informatik,
Strassacker 10, D-87487 Wiggensbach

### input:

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
*   **Umsatz Br.**: revenue in EUR: decimal, not formatted to a fixed number of decimal digits.
    It appears to be always positive.
    Negative amounts are booked via a negative value in column `Anzahl`
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
| 3  |   Uhrzeit       |  Uhrzeit          |  kein Import        |
| 4  |   Umsatz Br.    |  Umsatz Br.       |  Betrag             |
| 5  |   Anzahl        |  Anzahl           |  kein Import        |
| 6  |   Produkt       |  Produkt          |  Text               |
| 7  |   Einzel VK Br. |  Einzel VK Br.    |  kein Import        |
| 8  |   MwSt-Satz     |  MwSt-Satz        |  kein Import        |
| 9  |   MwSt          |  MwSt             |  kein Import        |
| 10 |   Dst/Ware      |  Dst/Ware         |  Notiz              |
| 11 |                 |  Soll/Haben       |  kein Import        |
| 12 |                 |  Konto            |  KontoSoll          |
| 13 |                 |  Gegenkonto       |  KontoHaben         |
| 14 |                 |  St-SL            |  Steuersatz         |
| 15 |                 |  DateTime         |  kein Import        |
| 16 |                 |  ChangeLog        |  kein Import        |

## ProSaldo Import Settings (Import Textdateien)

### General

| Parameter                     |   Wert                |
| ----------------------------- | --------------------- |    
| Trennzeichen für Felder:      |  Semikolon            |
| Trennzeichen für Datensätze:  |  LF                   |
| Textbregrenzung:              |  keine                |
| Zeichensatz:                  |  IsoLatin1 (Windows)  |

## debit / credit indicator (Soll/Haben-Kennzeichen)

All monetary amounts in the input column `Umsatz Br.` are positive
(greater or equal to zero).

The debit / credit indicator for each record is created based on data in column `Anzahl`
according to the following rule
*   debit / credit indicator = "S" if the content of  `Anzahl` is greater or equal to zero
*   debit / credit indicator = "H" if the content of  `Anzahl` is less than zero

We consider the selling goods or service a regular transactions.
For regular transactions we set the debit / credit indicator to "S".
With debit / credit indicator = "S" the posting follows the rule
"debit to credit".

*   Konto is the debit account
*   Gegenkonto is the credit account

With debit / credit indicator = "H" the Konto and Gegenkonto will be reversed
in the posting follows and the positive amount in `Umsatz Br.` is preserved.

## debit account (Konto)

The debit account for each record is always set to `1600`
which is the standard account for the cash register in account plan SKr 04 (abridged)

The export data does not contain information to distinguish between cash payment and bank transfer.

## credit account and tax key (Gegenkonto)

The debit / credit indicator for each record is created based on data
in column `MwSt-Satz` and `Dst/Ware`.

We create a subset of the dataframe to contain only transactions with
`Dst/Ware` = `Ware` and set the credit account according to the key   
in column `MwSt-Satz` and  value taken from the following dictionary

```
dCAGoods = {
    '0': '4000',       # Umsatzsteuerfrei
    '7': '4300',    # Umsatzsteuer 7%
    '19': '4400'   # Umsatzsteuer 19%
}
```


We create a subset of the dataframe to contain only transactions with
`Dst/Ware` = `Dienst` and set the credit account according to the key   
in column `MwSt-Satz` and  value taken from the following dictionary


```
dCAService = {
    '0': '4001',    # Umsatzsteuerfrei
    '7': '4301',    # Umsatzsteuer 7%
    '19': '4401'   # Umsatzsteuer 19%
}
```

We merge the dataframes and compare the number of transactions to the original dataframe.
If there is a mismatch, we issue a warning.
Such a mismatch would mean that there a records with an entry in `Dst/Ware`
that is not in the set (`Ware`,`Dienst`).

## Tax Keys in ProSaldo

We create the tax key in column `St-SL` according to the key   
in column `MwSt-Satz` and  value taken from the following dictionary


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
