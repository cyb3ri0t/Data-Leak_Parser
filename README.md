# Flare_Data-Leak_Parser
This Python script analyzes CSV files containing "identity indicators" data (such as compromised credentials), generating statistical reports and identifying relevant patterns.

#### Descrizione
Questo script Python analizza file CSV contenenti dati di "identity indicators" (come credenziali compromesse), generando report statistici e individuando pattern rilevanti. Include funzionalità di:
- Analisi di frequenza degli indicatori di identità
- Raggruppamento dei dati per trimestre/anno
- Identificazione degli hash più utilizzati nell'ultimo anno
- Rilevamento di hash simili
- Associazione tra hash e utenti coinvolti

---

#### Prerequisiti
- **Python 3.x**
- Librerie standard richieste:
  - `csv`
  - `argparse`
  - `re`
  - `collections`
  - `datetime`

---


#### Utilizzo

python data-leaked-analyzer-v5.py input_file.csv [-o output_file.csv]

o

python3 data-leaked-analyzer-v5.py input_file.csv [-o output_file.csv]


**Parametri:**
- `input_file.csv`: File CSV in input (obbligatorio)
- `-o output_file.csv`: File CSV di output (default: `risultati_analisi.csv`)

---

#### Formato del CSV di Input
Il file CSV deve contenere queste colonne:
imported_at,indicator_of_identity,hash,source

Esempio:

"01/15/2023, 08:30:45 AM", user@example.com, 5f4dcc3b5aa765d61d8327deb882cf99, breach2023


---

#### Funzionalità Principali
1. **Top Identity Indicators**  
   Identifica gli indicatori di identità più frequenti (top 10).

2. **Analisi Trimestrale**  
   Conta le occorrenze per trimestre/anno (formato: `YYYY-QX`).

3. **Top Hash Recenti**  
   Seleziona i 5 hash più usati nell'ultimo anno, con:
   - Hash simili (corrispondenza di sottostringhe da 4 caratteri)
   - Conteggio occorrenze degli hash simili
   - Utenti associati agli hash

4. **Output Dettagliato**  
   Genera un CSV con queste colonne:

   Metrica,Valore,Count,Simili,Simili_Count,Utenti Coinvolti


---

#### Note Tecniche
1. **Formati Data Supportati:**
   - `MM/DD/YYYY, HH:MM:SS AM/PM`
   - `MM/DD/YYYY, HH:MM:SS` (24h)

2. **Algoritmo Hash Simili:**  
   Confronta sottostringhe di 4 caratteri tra gli hash per trovare corrispondenze parziali.

3. **Filtro Temporale:**  
   Gli hash "recenti" sono quelli apparsi negli ultimi **due anni** (anno corrente e precedente).

---

#### Report a Schermo
All'esecuzione, lo script mostra:
- Logo ASCII
- Progresso dell'analisi
- Riepilogo finale:
  Totale record analizzati: X
  Indicator of Identity unici: Y
  Hash unici nell'ultimo anno: Z
  Trimestri analizzati: K

---
