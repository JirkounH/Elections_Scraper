"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Jiri Hubacek
email: hubacek108@gmail.com
"""

import sys
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
from typing import List, Tuple, Dict


def validate_args(args: List[str]) -> Tuple[str, str]:
    """
    Ověří správnost argumentů příkazové řádky.

    Args:
        args: Seznam argumentů ze sys.argv.

    Returns:
        Tuple obsahující URL a výstupní název CSV souboru.

    Raises:
        SystemExit: Pokud jsou argumenty neplatné.
    """
    if len(args) != 3:
        print("Chyba: musíš zadat dva argumenty: <URL> <výstupní_soubor.csv>")
        sys.exit(1)
    if not args[1].startswith("https://www.volby.cz/pls/ps2017nss/ps32"):
        print("Chyba: první argument musí být odkaz na stránku územního celku (např. ps32...)")
        sys.exit(1)
    if not args[2].endswith(".csv"):
        print("Chyba: druhý argument musí být název výstupního souboru s příponou .csv")
        sys.exit(1)
    return args[1], args[2]


def fetch_html(url: str) -> BeautifulSoup:
    """
    Stáhne HTML stránku a vrátí ji jako BeautifulSoup objekt.

    Args:
        url: URL adresa ke stažení.

    Returns:
        Objekt typu BeautifulSoup s obsahem stránky.

    Raises:
        RuntimeError: Pokud dojde k chybě při HTTP požadavku.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        raise RuntimeError(f"Chyba při stahování URL {url}: {e}")


def extract_obec_links(soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str, str]]:
    """
    Z HTML extrahuje kódy, názvy a odkazy na jednotlivé obce ze všech tabulek.

    Args:
        soup: Parsovaný obsah stránky.
        base_url: Základní URL pro spojení relativních odkazů.

    Returns:
        Seznam trojic (kód, název, úplný odkaz).
    """
    tables = soup.find_all("table", class_="table")
    if not tables:
        raise ValueError("Nebyla nalezena žádná tabulka s obcemi.")

    links: List[Tuple[str, str, str]] = []

    for table in tables:
        for row in table.find_all("tr")[2:]:  # přeskoč hlavičky
            tds = row.find_all("td")
            if len(tds) >= 2:
                code = tds[0].text.strip()
                name = tds[1].text.strip()
                a_tag = tds[0].find("a")
                if a_tag and "href" in a_tag.attrs:
                    link = urljoin(base_url, a_tag["href"])
                    links.append((code, name, link))

    return links


def parse_summary_table(table: BeautifulSoup) -> Tuple[int, int, int]:
    """
    Zpracuje první tabulku se souhrnnými daty o voličích.

    Args:
        table: HTML tabulka se statistikami.

    Returns:
        Trojice: počet registrovaných, obálek a platných hlasů.

    Raises:
        ValueError: Pokud tabulka neobsahuje očekávaná data.
    """
    tds = table.find_all("td")
    if len(tds) < 8:
        raise ValueError("Souhrnná tabulka neobsahuje dostatek dat.")
    return (
        int(tds[3].text.replace('\xa0', '').replace(' ', '')),
        int(tds[4].text.replace('\xa0', '').replace(' ', '')),
        int(tds[7].text.replace('\xa0', '').replace(' ', ''))
    )


def parse_party_results(tables: List[BeautifulSoup]) -> Dict[str, int]:
    """
    Zpracuje tabulky s výsledky politických stran.

    Args:
        tables: Seznam HTML tabulek s výsledky.

    Returns:
        Slovník {název strany: počet hlasů}.
    """
    parties: Dict[str, int] = {}
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                party = cols[1].text.strip()
                try:
                    votes = int(cols[2].text.replace('\xa0', '').replace(' ', ''))
                except ValueError:
                    votes = 0
                parties[party] = votes
    return parties


def scrape_obec(url: str) -> Tuple[int, int, int, Dict[str, int]]:
    """
    Zpracuje jednu obec a vrátí souhrnné údaje a hlasy pro strany.

    Args:
        url: Odkaz na stránku s výsledky jedné obce.

    Returns:
        Čtyřice: registrovaní, obálky, platné hlasy, výsledky stran.
    """
    soup = fetch_html(url)
    tables = soup.find_all("table", class_="table")
    if len(tables) < 2:
        raise ValueError("Nedostatek tabulek na stránce obce.")
    
    registered, envelopes, valid = parse_summary_table(tables[0])
    parties = parse_party_results(tables[1:])
    return registered, envelopes, valid, parties


def save_to_csv(filename: str, fieldnames: List[str], data_rows: List[Dict[str, int]]) -> None:
    """
    Uloží data do CSV souboru s hlavičkou.

    Args:
        filename: Název cílového souboru.
        fieldnames: Seznam názvů sloupců.
        data_rows: Data k uložení ve formě seznamu slovníků.
    """
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)


def main() -> None:
    """
    Hlavní vstupní bod skriptu. Zpracuje vstupní argumenty,
    načte data z webu a uloží je do CSV.
    """
    url, output_file = validate_args(sys.argv)
    soup = fetch_html(url)
    obce = extract_obec_links(soup, url)

    print(f"Nalezeno obcí: {len(obce)}")

    all_party_names: set[str] = set()
    data_rows: List[Dict[str, int]] = []

    for code, name, link in obce:
        try:
            registered, envelopes, valid, parties = scrape_obec(link)
            all_party_names.update(parties.keys())
            row: Dict[str, int | str] = {
                "code": code,
                "location": name,
                "registered": registered,
                "envelopes": envelopes,
                "valid": valid,
                **parties
            }
            data_rows.append(row)
            print(f"Načteno: {code} - {name}")
        except Exception as e:
            print(f"Chyba při zpracování obce {name} ({code}): {e}")

    sorted_parties = sorted(all_party_names)
    fieldnames = ["code", "location", "registered", "envelopes", "valid"] + sorted_parties

    for row in data_rows:
        for party in sorted_parties:
            row.setdefault(party, 0)

    save_to_csv(output_file, fieldnames, data_rows)
    print(f"Hotovo. Výsledky uloženy do: {output_file}")


if __name__ == "__main__":
    main()

