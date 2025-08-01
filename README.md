# Flare Data-Leak Parser
This Python script analyzes CSV files containing "identity indicators" data (such as compromised credentials), generating statistical reports and identifying relevant patterns.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

Uno strumento avanzato per analizzare dati di identità compromesse, identificare pattern critici e generare report statistici dettagliati.


## Caratteristiche Principali

- 🔍 **Analisi indicatori di identità** (top 10 più frequenti)
- 📅 **Raggruppamento trimestrale** dei dati (formato YYYY-QX)
- 🔑 **Identificazione hash compromessi** più utilizzati nell'ultimo anno
- 🧩 **Rilevamento hash simili** tramite corrispondenza di sottostringhe
- 👥 **Associazioni utenti-hash** per tracciare l'impatto delle compromissioni
- 📊 **Generazione report CSV** con metriche dettagliate

## Prerequisiti

- Python 3.7 o superiore
- Solo librerie standard Python (nessuna installazione aggiuntiva richiesta)

## Installazione

```bash
git clone https://github.com/tuorepo/data-leaked-analyzer.git
cd data-leaked-analyzer
```

## Utilizzo

```bash
python data-leaked-analyzer-v5.py input_file.csv [-o output_file.csv]
```

**Parametri:**
- `input_file.csv`: Percorso del file CSV di input (obbligatorio)
- `-o output_file.csv`: Percorso del file CSV di output (default: `risultati_analisi.csv`)

## Formato Input

Il file CSV deve contenere queste colonne:

```csv
imported_at,indicator_of_identity,hash,source
```

**Esempio:**
```csv
01/15/2023, 08:30:45 AM,user@example.com,5f4dcc3b5aa765d61d8327deb882cf99,breach2023
```

## Output Generato

Il tool genera un CSV con le seguenti colonne:

| Metrica                          | Valore                      | Count | Simili                   | Simili_Count | Utenti Coinvolti         |
|----------------------------------|-----------------------------|-------|--------------------------|--------------|--------------------------|
| Top 1 Indicator of Identity      | admin@example.com           | 142   | -                        | -            | -                        |
| Occorrenze totali 2023-Q1        | 2023-Q1                     | 89    | -                        | -            | -                        |
| Top 1 Hash ultimo anno           | 5f4dcc3b5aa765d61d83...     | 42    | 6b7a6a7c8d9e0f1a2b3c... | 15           | admin@example.com, ...   |

## Note Tecniche

1. **Supporto formati data:**
   - `MM/DD/YYYY, HH:MM:SS AM/PM`
   - `MM/DD/YYYY, HH:MM:SS` (formato 24h)

2. **Algoritmo hash simili:**  
   Identifica corrispondenze parziali confrontando sottostringhe di 4 caratteri

3. **Filtro temporale:**  
   Considera come "recenti" gli hash apparsi nell'anno corrente e precedente

## Esempio di Esecuzione

```bash
python data-leaked-analyzer-v5.py sample_data.csv -o analisi_2023.csv
```

**Output terminale:**
```
Analisi del file: sample_data.csv
Cerco l'indicator_of_identity con più occorrenze...
Creo una lista per i top 10 indicator_of_identity...
Calcolo le occorrenze totali per ogni trimestre/anno...
Identifica i top 5 hash più utilizzati nell'ultimo anno...
Analisi completata! Risultati salvati in 'analisi_2023.csv'

=== RIEPILOGO ANALISI ===
Totale record analizzati: 3842
Indicator of Identity unici: 217
Hash unici nell'ultimo anno: 89
Trimestri analizzati: 8
```

## Contributi

I contributi sono benvenuti! Apri una issue o una pull request per suggerire miglioramenti.

## Licenza

Distribuito con licenza MIT - vedi il file [LICENSE](LICENSE) per i dettagli.
```

Per scaricare direttamente il file, puoi:

1. Copiare tutto il testo sopra
2. Incollarlo in un nuovo file chiamato `README.md`
3. Salvare il file nella tua directory di progetto

Oppure usa questo comando curl (se hai un repository pubblico):

```bash
curl -o README.md https://gist.githubusercontent.com/fakeuser/fakegist/raw/README.md
```

Nota: sostituisci "tuorepo" con l'effettivo URL del tuo repository GitHub nella sezione Installazione.
