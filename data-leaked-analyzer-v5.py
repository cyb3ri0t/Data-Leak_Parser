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
    """Parsing flessibile per diverse tipologie di formato data"""
    if pd.isna(date_string) or date_string == '':
        return None
    
    if isinstance(date_string, pd.Timestamp):
        return date_string.to_pydatetime()
    
    date_string = str(date_string).strip()
    formats = [
        "%m/%d/%Y, %I:%M:%S %p",
        "%m/%d/%Y, %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(date_string).to_pydatetime()
    except:
        print(f"Errore nel parsing della data: {date_string}")
        return None

def get_quarter(month):
    return (month - 1) // 3 + 1

class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}
    
    def initialize(self, items):
        for item in items:
            self.parent[item] = item
            self.rank[item] = 0
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        rx = self.find(x)
        ry = self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1

def build_hash_components(hashes):
    uf = UnionFind()
    uf.initialize(hashes)
    gram_to_hashes = defaultdict(set)
    
    for hash_val in hashes:
        hash_lower = hash_val.lower()
        if len(hash_lower) < 4:
            continue
        for i in range(len(hash_lower) - 3):
            gram = hash_lower[i:i+4]
            gram_to_hashes[gram].add(hash_val)
    
    for gram, hash_set in gram_to_hashes.items():
        if len(hash_set) < 2:
            continue
        hash_list = list(hash_set)
        root = hash_list[0]
        for i in range(1, len(hash_list)):
            uf.union(root, hash_list[i])
    
    components = defaultdict(set)
    for hash_val in hashes:
        root = uf.find(hash_val)
        components[root].add(hash_val)
    
    return components

# ------------------ NUOVA FUNZIONE ------------------
def count_identities_by_domain(series):
    """
    Estrae domini dalle stringhe in `series` (Indicator / Account) e ritorna Counter(domain -> count).
    - Trova tutte le email via regex in ogni cella (gestisce più email nella stessa cella).
    - Normalizza i domini (lowercase, rimuove spazi/punteggiatura attaccata).
    """
    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+', re.UNICODE)
    domain_counter = Counter()
    for val in series.fillna('').astype(str):
        if not val:
            continue
        # trova tutte le email presenti nella cella
        emails = email_pattern.findall(val)
        if not emails:
            # Se nella cella non ci sono email, prova a vedere se c'è un suffisso tipo "@domain" senza user?
            # Ma per semplicità ignoriamo valori non email
            continue
        for e in emails:
            # Estrai la parte dopo @ e normalizza
            parts = e.split('@', 1)
            if len(parts) != 2:
                continue
            domain = parts[1].strip().lower().rstrip('.,;:')
            if domain:
                domain_counter[domain] += 1
    return domain_counter
# ----------------------------------------------------

def analyze_excel(input_file, output_file):
    print(LOGO)
    print(f"Lettura del file Excel: {input_file}")

    identity_counter = Counter()
    identity_last_seen = defaultdict(list)
    quarterly_counter = defaultdict(int)
    hash_date_counter = defaultdict(list)
    all_hash_counter = Counter()
    hash_to_identity = defaultdict(set)
    current_year = datetime.now().year

    try:
        df = pd.read_excel(input_file)
        
        header_mapping = {
            'Event data': 'imported_at',
            'Indicator / Account': 'indicator_of_identity',
            'Hash /Password': 'hash',
            'Sources': 'source'
        }
        
        missing_headers = []
        for required_header in header_mapping.keys():
            if required_header not in df.columns:
                missing_headers.append(required_header)
        
        if missing_headers:
            print(f"Errore: Header mancanti nel file Excel: {missing_headers}")
            print(f"Header trovati: {list(df.columns)}")
            return
        
        df = df.rename(columns=header_mapping)
        
        print(f"Trovati {len(df)} record nel file Excel")
        
        for idx, row in df.iterrows():
            identity = str(row['indicator_of_identity']).strip() if pd.notna(row['indicator_of_identity']) else ''
            hash_value = str(row['hash']).strip() if pd.notna(row['hash']) else ''
            date_obj = parse_date(row['imported_at'])

            if identity and identity != 'nan':
                identity_counter[identity] += 1
                if date_obj:
                    identity_last_seen[identity].append(date_obj)

            if hash_value and hash_value != 'nan':
                all_hash_counter[hash_value] += 1
                if identity and identity != 'nan':
                    hash_to_identity[hash_value].add(identity)

            if date_obj:
                quarter = get_quarter(date_obj.month)
                quarter_key = f"{date_obj.year}-Q{quarter}"
                quarterly_counter[quarter_key] += 1

                if hash_value and hash_value != 'nan' and date_obj.year >= current_year - 1:
                    hash_date_counter[hash_value].append(date_obj)

    except FileNotFoundError:
        print(f"Errore: File '{input_file}' non trovato.")
        return
    except Exception as e:
        print(f"Errore durante la lettura del file Excel: {e}")
        return

    results = []
    total_identities = sum(identity_counter.values())

    # Nota: la richiesta è di rimuovere la riga "Indicator / Account più frequente"
    # quindi NON aggiungiamo più quella metrica al report.

    print("Creo una lista per i top 10 Indicator / Account ordinati per frequenza...")
    top_10_identities = identity_counter.most_common(10)
    for i, (identity, count) in enumerate(top_10_identities, 1):
        last_seen_date = max(identity_last_seen[identity]) if identity_last_seen[identity] else None
        last_seen_str = last_seen_date.strftime("%d/%m/%Y %H:%M:%S") if last_seen_date else "N/A"
        
        results.append({
            'Metrica': f'Top {i} Indicator / Account',
            'Valore': identity,
            'Count': count,
            'Ultima_Rilevazione': last_seen_str,
            'Simili': '',
            'Simili_Count': '',
            'Utenti Coinvolti': ''
        })

    print("Calcolo le occorrenze totali per ogni trimestre/anno...")
    sorted_quarters = sorted(quarterly_counter.items())
    for quarter_key, count in sorted_quarters:
        results.append({
            'Metrica': f'Occorrenze totali {quarter_key}',
            'Valore': quarter_key,
            'Count': count,
            'Ultima_Rilevazione': '',
            'Simili': '',
            'Simili_Count': '',
            'Utenti Coinvolti': ''
        })

    # --- Nuova sezione: conteggio globale raggruppato per anno (ultima riga)
    year_counter = defaultdict(int)
    for quarter_key, count in quarterly_counter.items():
        try:
            year = int(quarter_key.split('-')[0])
            year_counter[year] += count
        except Exception:
            continue

    if year_counter:
        # ordina per anno crescente e formatta come "YYYY: count"
        year_parts = [f"{yr}: {year_counter[yr]}" for yr in sorted(year_counter.keys())]
        year_summary = ", ".join(year_parts)
        total_all_years = sum(year_counter.values())
        # Aggiungiamo la riga finale come richiesto (ultima riga del file)
        results.append({
            'Metrica': 'Conteggio per anno',
            'Valore': year_summary,
            'Count': total_all_years,
            'Ultima_Rilevazione': '',
            'Simili': '',
            'Simili_Count': '',
            'Utenti Coinvolti': ''
        })

    print("Identifico i top 5 gruppi di hash più utilizzati nell'ultimo anno...")
    recent_hash_counter = Counter()
    for hash_value, dates in hash_date_counter.items():
        recent_count = sum(1 for d in dates if d.year >= current_year - 1)
        if recent_count > 0:
            recent_hash_counter[hash_value] = recent_count

    all_hashes = list(all_hash_counter.keys())
    components = build_hash_components(all_hashes)
    
    component_recent_freq = defaultdict(int)
    for root, comp_set in components.items():
        total = 0
        for hash_val in comp_set:
            total += recent_hash_counter.get(hash_val, 0)
        component_recent_freq[root] = total
    
    sorted_components = sorted(component_recent_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for i, (root, total_freq) in enumerate(sorted_components, 1):
        comp_set = components[root]
        sorted_hashes = sorted(comp_set, key=lambda h: (-recent_hash_counter.get(h, 0), h))
        top_hash = sorted_hashes[0] if sorted_hashes else ""
        
        group_size = len(comp_set)
        if group_size <= 1:
            similar_str = "No similar hashes"
        else:
            others = sorted_hashes[1:3]
            others_str = ", ".join([h[:20] + '...' if len(h) > 20 else h for h in others])
            if group_size > 3:
                similar_str = f"{group_size} hashes: {others_str} (and {group_size-3} more)"
            else:
                similar_str = f"{group_size} hashes: {others_str}"
        
        identities = set()
        for h in comp_set:
            identities.update(hash_to_identity.get(h, set()))
        identities_str = ", ".join(sorted(identities)) if identities else "-"
        
        results.append({
            'Metrica': f'Top {i} Group',
            'Valore': top_hash[:20] + '...' if len(top_hash) > 20 else top_hash,
            'Count': total_freq,
            'Ultima_Rilevazione': '',
            'Simili': similar_str,
            'Simili_Count': group_size,
            'Utenti Coinvolti': identities_str
        })

    # Salva i risultati
    try:
        if output_file.endswith('.xlsx'):
            output_df = pd.DataFrame(results)
            output_df.to_excel(output_file, index=False)
            print(f"\nAnalisi completata! Risultati salvati in '{output_file}' (formato Excel)")
        else:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Metrica', 'Valore', 'Count', 'Ultima_Rilevazione', 'Simili', 'Simili_Count', 'Utenti Coinvolti']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"\nAnalisi completata! Risultati salvati in '{output_file}' (formato CSV)")

        print("\n=== RIEPILOGO ANALISI ===")
        print(f"Totale record analizzati: {total_identities}")
        print(f"Indicator / Account unici: {len(identity_counter)}")
        print(f"Hash unici nell'ultimo anno: {len(recent_hash_counter)}")
        print(f"Trimestri analizzati: {len(quarterly_counter)}")

    except Exception as e:
        print(f"Errore durante la scrittura del file di output: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analizza un file Excel con dati di identity indicators')
    parser.add_argument('input_file', help='Path del file Excel di input (.xlsx)')
    parser.add_argument('-o', '--output', default='risultati_analisi.xlsx',
                        help='Path del file di output (default: risultati_analisi.xlsx). Usa .xlsx per Excel o .csv per CSV')
    args = parser.parse_args()

    if not args.input_file.endswith(('.xlsx', '.xls')):
        print("Attenzione: Il file di input dovrebbe essere in formato Excel (.xlsx o .xls)")

    import os
    base_name = os.path.basename(args.input_file)   # es: Uccio - dati_breach_2024.xlsx
    prefix = base_name.split(" - ")[0]              # es: Uccio
    _, ext = os.path.splitext(args.output)          # es: .xlsx
    output_file = f"{prefix} - risultati_analisi{ext}"

    print(f"Analisi del file: {args.input_file}")
    analyze_excel(args.input_file, output_file)
    
if __name__ == "__main__":
    main()


