# README – Scraper výsledků voleb (Engeto projekt 3)

Tento Python skript slouží k hromadnému stažení a uložení výsledků parlamentních voleb z webu [volby.cz](https://www.volby.cz) pro všechny obce v jednom územním celku. Výstupem je CSV soubor obsahující strukturovaná data pro další analýzu.

## Autor
- **Jméno:** Jiří Hubáček
- **Email:** hubacek108@gmail.com

## Struktura projektu

```
main.py             # hlavní skript
README.md           # tento soubor
vystup.csv          # výstupní soubor (vzniká během běhu skriptu)
```

## Použití

Skript se spouští z příkazové řádky a očekává dva argumenty:
1. URL na stránku konkrétního územního celku – musí to být stránka obsahující přímo **seznam obcí** (tabulky s odkazy).
2. Název výstupního CSV souboru (musí končit na `.csv`)

> **Důležité:** Nepoužívej odkazy na kraj nebo mezistránky. Použij odkaz až na konkrétní okresní úroveň, kde se zobrazí seznam obcí ve formě tabulky.

### Jak najít správnou URL
1. Otevři [https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ)
2. Vyber Kraj
3. Klikni na název sloupce **Výběr obce** ve sloupci „X“
4. Zkopíruj URL adresu do příkazového řádku

### Funkční příklady spuštění

Zpracování okresu Beroun:
```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102" Beroun.csv
```

Zpracování okresu Benešov:
```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" Benesov.csv
```

Zpracování okresu Kladno:
```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103" Kladno.csv 
```

## Co skript dělá
1. Ověří správnost argumentů.
2. Načte vstupní stránku a vyhledá odkazy na jednotlivé obce.
3. Pro každou obec stáhne stránku s volebními výsledky.
4. Získá:
   - Počet registrovaných voličů
   - Počet vydaných obálek
   - Počet platných hlasů
   - Hlasy pro jednotlivé strany
5. Výsledky uloží do CSV souboru s oddělovačem `;` (kompatibilní s Excel).

## Struktura CSV výstupu

Sloupce:
- `code` – kód obce
- `location` – název obce
- `registered` – počet registrovaných voličů
- `envelopes` – vydané obálky
- `valid` – platné hlasy
- `...` – názvy politických stran (sloupce jsou dynamické dle výskytu)

## Ošetřené chyby
- Chybějící nebo špatné argumenty
- Neplatná URL
- Nepřístupná stránka obce
- Chyby při parsování dat

## Závislosti

Skript vyžaduje:
- Python 3.7+
- Knihovny:
  - `requests`
  - `beautifulsoup4`

### Instalace potřebných knihoven:
```bash
pip install -r requirements.txt
```

**Příklad `requirements.txt`:**
```
requests
beautifulsoup4
```

## Poznámky
- Skript funguje pouze s odkazy typu `ps32?...` ze stránky volby.cz obsahující tabulku obcí.
- Neprovádí deduplikaci ani pokročilou validaci dat.

## Licence
Tento projekt je vytvořen jako školní úkol pro Engeto Online Python Akademii a je volně dostupný pro studijní účely.




