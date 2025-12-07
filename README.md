# Automatisierung des Rechnungsprozesses für Heinrich Metallbau

Dieses Programm unterstützt die Erstellung von **Lieferscheinen**, **Auftragsbestätigungen** und **Rechnungen** aus den Zeiterfassungsdaten von Heinrich Metallbau.
Es handelt sich zur Zeit um ein Kommandozeilen-Tool, das mit Python ausgeführt wird.

---

## Voraussetzungen

- Installiertes **Python 3.12** (oder neuer)
- Abhängigkeiten wurden mit `pip install -r requirements` installiert
- Ein vorhandenes **Projektverzeichnis** in `/Pfad/zu/RHI/` (siehe unten)

---

## Ordnerstruktur

    heinrich-tool/
    ├── main.py
    ├── templates/
    │   └── Vordruck.docx       # Word-Vorlage mit Platzhaltern
    ├── output/                 # Output Ordner für temporäres Rechnungstemplate
    │   ├── 1235/
    │   │   └── Vordruck_Rechnung_1235.docx
    │   ├── 1253/
    │   │   └── Vordruck_Rechnung_1253.docx
    │   └── ...
    /Pfad/zu/RHI/
    ├── 1235 - Allgemein Juli/
    │   ├── heinrich_zeiterfassung_2025-09-01.csv
    │   ├── Lieferschein Nr. 1235.docx  # Output des Tools für mode "liefer"
    │   ├── Rechnung Nr. 1235 - 4504049161.docx # Output des Tools für mode "rechnung"
    │   └── ...
    └── ...

- **RHI/**
  Enthält die Auftragsordner.
  Jeder Ordner beginnt mit einer vierstelligen Projektnummer und dem Projektnamen, z. B.
  `1243 - Eingreifschutz Rollenbahnen`.

- **CSV-Dateien**
  In jedem relevanten Auftragsordner liegt mindestens eine Datei nach dem Muster:
  `heinrich_zeiterfassung_YYYY-MM-DD.csv`.
  Das Programm sucht automatisch die **neueste** CSV-Datei.

- **templates/**
  Hier liegt die Word-Vorlage `Vordruck.docx`, die mit Daten aus der CSV befüllt wird.

---

## Verwendung

Das Programm wird im Projektordner aus der Kommandozeile gestartet.

### Lieferschein erzeugen

    python main.py 1235 liefer

- Liest die CSV im Ordner `RHI/1235 - .../`
- Befüllt die Vorlage `Vordruck.docx`
- Erstellt im selben Ordner `RHI/1235 - .../`:
  - `Lieferschein Nr. 1235.docx`
  - `Lieferschein Nr. 1235.pdf`

### Auftragsbestätigung & Rechnung erzeugen

    python main.py 1235 rechnung 4504049161

- Liest das erstellte Rechnungstemplate aus dem `output` Ordner
- Erstellt im Ordner `RHI/1235 - .../`:
  - `Auftragsbestätigung Nr. 1235 - 4504049161.docx`
  - `Auftragsbestätigung Nr. 1235 - 4504049161.pdf`
  - `Rechnung Nr. 1235 - 4504049161.docx`
  - `Rechnung Nr. 1235 - 4504049161.pdf`

---

## Initialer Copilot Prompt

Folgender Prompt diente zum initialen Projekt Scaffolding mit Copilot (Prompt erstellt mithilfe von ChatGPT):

    You are inside the already created project folder (from git clone). Do not create an extra subfolder — put all files directly into the current folder. Create a minimal Python 3.12.5 project called “heinrich-metallbau”. It’s a small CLI utility that generates documents from CSV + a Word template. Keep it simple and readable, with basic logging. No tests or packaging. ⚠️ Do not generate a README.md. ⚠️ Create also a pyproject.toml for dependency management. Usage (run from the project folder): - python main.py 1235 liefer - python main.py 1235 rechnung 4504049161 Arguments: 1) PROJECT_NUMBER → exactly 4 digits (e.g., 1235) 2) MODE → either liefer or rechnung 3) ORDER_NUMBER → required only if MODE = rechnung Data & paths: - Data root folder: RHI/ (git-ignored). - Each order folder is named: RHI/[PROJECT_NUMBER] - [PROJECT_NAME]/ - Search the CSV inside the folder whose name starts with the given PROJECT_NUMBER (exact 4-digit prefix match). - In that folder, pick the latest file matching: heinrich_zeiterfassung_[YYYY-MM-DD].csv - Template folder: templates/ with a template named Vordruck.docx. Modes: - liefer: - Read the CSV (use csv.DictReader, no pandas). - Load the Word template (Vordruck.docx). - Fill the placeholders in the Word template with data from the CSV. - Produce two outputs: - Lieferschein Nr. [PROJECT_NUMBER].docx - Lieferschein Nr. [PROJECT_NUMBER].pdf (PDF can be a stub for now). - rechnung (scaffold only for now): - Read the existing Lieferschein (or reuse CSV data). - Prepare to generate: - Auftragsbestätigung Nr. [PROJECT_NUMBER] - [ORDER_NUMBER].docx/.pdf - Rechnung Nr. [PROJECT_NUMBER] - [ORDER_NUMBER].docx/.pdf - Do not implement ORDER_NUMBER logic yet; just log a placeholder message and add TODOs. Implementation notes: - Split into multiple files to keep main.py small: - args module for parsing and validation, - path/file discovery (find order folder, latest CSV, template path), - CSV loading (with csv.DictReader), - Word document loading + rendering (placeholder fill) and PDF creation (stub). - Use small, focused functions (argument parsing, path resolution, CSV load, render). - Add TODO: markers for CSV transformations, placeholder mapping, ORDER_NUMBER handling, and real PDF conversion. Code style: - Type hints and docstrings. - Basic logging via logging.basicConfig(...). - No global variables (global constants like paths are fine).
