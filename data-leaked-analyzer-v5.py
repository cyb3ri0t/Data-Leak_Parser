#!/usr/bin/env python3
"""
Script per analizzare un file CSV con dati di identity indicators
con output arricchito e stampe delle fasi di analisi.
Autore: Riccardo M (cyberiot)
"""

import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime
import argparse
import re

LOGO = r"""
  _____        _               _                _                              _                    
 |  __ \      | |             | |              | |           /\               | |                   
 | |  | | __ _| |_ __ _ ______| |     ___  __ _| | ________ /  \   _ __   __ _| |_   _ _______ _ __ 
 | |  | |/ _` | __/ _` |______| |    / _ \/ _` | |/ /______/ /\ \ | '_ \ / _` | | | | |_  / _ \ '__|
 | |__| | (_| | || (_| |      | |___|  __/ (_| |   <      / ____ \| | | | (_| | | |_| |/ /  __/ |   
 |_____/ \__,_|\__\__,_|      |______\___|\__,_|_|\_\    /_/    \_\_| |_|\__,_|_|\__, /___\___|_|   
                                                                                  __/ |             
                                                                                 |___/      (cyberiot)   
                                                                                         
"""

def parse_date(date_string):
    try:
        date_string = date_string.strip()
        return datetime.strptime(date_string, "%m/%d/%Y, %I:%M:%S %p")
    except ValueError:
        try:
            return datetime.strptime(date_string, "%m/%d/%Y, %H:%M:%S")
        except ValueError:
            print(f"Errore nel parsing della data: {date_string}")
            return None

def get_quarter(month):
    return (month - 1) // 3 + 1

def find_similar_hashes(top_hashes, all_hashes, all_hash_counter):
    similar_dict = {}
    for top_hash in top_hashes:
        top_hash_lower = top_hash.lower()
        similar = {}
        for candidate in all_hashes:
            candidate_lower = candidate.lower()
            for i in range(len(candidate_lower) - 3):
                substring = candidate_lower[i:i+4]
                if substring in top_hash_lower and candidate != top_hash:
                    similar[candidate] = all_hash_counter.get(candidate, 0)
                    break
        similar_dict[top_hash] = similar
    return similar_dict

def analyze_csv(input_file, output_file):
    print(LOGO)

    identity_counter = Counter()
    quarterly_counter = defaultdict(int)
    hash_date_counter = defaultdict(list)
    all_hash_counter = Counter()
    hash_to_identity = defaultdict(set)
    current_year = datetime.now().year

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            expected_headers = ['imported_at', 'indicator_of_identity', 'hash', 'source']
            if not all(header.strip() in reader.fieldnames for header in expected_headers):
                print(f"Errore: Header mancanti. Header trovati: {reader.fieldnames}")
                return

            for row in reader:
                identity = row['indicator_of_identity'].strip()
                hash_value = row['hash'].strip()
                date_str = row['imported_at'].strip()
                date_obj = parse_date(date_str)

                if identity:
                    identity_counter[identity] += 1

                if hash_value:
                    all_hash_counter[hash_value] += 1
                    hash_to_identity[hash_value].add(identity)

                if date_obj:
                    quarter = get_quarter(date_obj.month)
                    quarter_key = f"{date_obj.year}-Q{quarter}"
                    quarterly_counter[quarter_key] += 1

                    if hash_value and date_obj.year >= current_year - 1:
                        hash_date_counter[hash_value].append(date_obj)

    except FileNotFoundError:
        print(f"Errore: File '{input_file}' non trovato.")
        return
    except Exception as e:
        print(f"Errore durante la lettura del file: {e}")
        return

    results = []
    total_identities = sum(identity_counter.values())

    print("Cerco l'indicator_of_identity con più occorrenze...")
    if identity_counter:
        most_common_identity = identity_counter.most_common(1)[0]
        results.append({
            'Metrica': 'Indicator of Identity più frequente',
            'Valore': most_common_identity[0],
            'Count': most_common_identity[1]
        })

    print("Creo una lista per i top 10 indicator_of_identity ordinati per frequenza")
    top_10_identities = identity_counter.most_common(10)
    for i, (identity, count) in enumerate(top_10_identities, 1):
        results.append({
            'Metrica': f'Top {i} Indicator of Identity',
            'Valore': identity,
            'Count': count
        })

    print("Calcolo le occorrenze totali per ogni trimestre/anno")
    sorted_quarters = sorted(quarterly_counter.items())
    for quarter_key, count in sorted_quarters:
        results.append({
            'Metrica': f'Occorrenze totali {quarter_key}',
            'Valore': quarter_key,
            'Count': count
        })

    print("Identifica i top 5 hash più utilizzati nell'ultimo anno")
    recent_hash_counter = Counter()
    for hash_value, dates in hash_date_counter.items():
        recent_count = sum(1 for d in dates if d.year >= current_year - 1)
        if recent_count > 0:
            recent_hash_counter[hash_value] = recent_count

    top_5_hashes = recent_hash_counter.most_common(5)
    similar_hashes = find_similar_hashes([h for h, _ in top_5_hashes], all_hash_counter.keys(), all_hash_counter)

    for i, (hash_value, count) in enumerate(top_5_hashes, 1):
        similars = similar_hashes[hash_value]
        similar_list = ", ".join(similars.keys()) if similars else "-"
        similar_count = sum(similars.values()) if similars else 0

        related_users = set()
        for h in [hash_value] + list(similars.keys()):
            related_users.update(hash_to_identity.get(h, []))

        results.append({
            'Metrica': f'Top {i} Hash ultimo anno',
            'Valore': hash_value[:20] + '...' if len(hash_value) > 20 else hash_value,
            'Count': count,
            'Simili': similar_list,
            'Simili_Count': similar_count,
            'Utenti Coinvolti': ", ".join(sorted(related_users)) if related_users else "-"
        })

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Metrica', 'Valore', 'Count', 'Simili', 'Simili_Count', 'Utenti Coinvolti']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"\nAnalisi completata! Risultati salvati in '{output_file}'")
        print("\n=== RIEPILOGO ANALISI ===")
        print(f"Totale record analizzati: {total_identities}")
        print(f"Indicator of Identity unici: {len(identity_counter)}")
        print(f"Hash unici nell'ultimo anno: {len(recent_hash_counter)}")
        print(f"Trimestri analizzati: {len(quarterly_counter)}")

    except Exception as e:
        print(f"Errore durante la scrittura del file di output: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analizza un file CSV con dati di identity indicators')
    parser.add_argument('input_file', help='Path del file CSV di input')
    parser.add_argument('-o', '--output', default='risultati_analisi.csv',
                        help='Path del file CSV di output (default: risultati_analisi.csv)')
    args = parser.parse_args()

    print(f"Analisi del file: {args.input_file}")
    analyze_csv(args.input_file, args.output)

if __name__ == "__main__":
    main()
