# Automatisierung des Rechnungsprozesses für Heinrich Metallbau

Dieses kleine Programm unterstützt die Erstellung von **Lieferscheinen**, **Auftragsbestätigungen** und **Rechnungen** aus den Zeiterfassungsdaten von Heinrich Metallbau.
Es handelt sich um ein einfaches Kommandozeilen-Tool, das mit Python ausgeführt wird.

---

## Voraussetzungen

- Installiertes **Python 3.12** (oder neuer)
- Abhängigkeiten werden mit `pip` installiert (z. B. `python-docx` oder `docxtpl`)
- Ein vorhandenes **Projektverzeichnis** in `RHI/` (siehe unten)

---

## Ordnerstruktur

    Projektordner/
    ├── main.py
    ├── templates/
    │   └── Vordruck.docx          # Word-Vorlage mit Platzhaltern
    ├── RHI/
    │   └── 1243 - Eingreifschutz Rollenbahnen/
    │       ├── heinrich_zeiterfassung_2025-09-01.csv
    │       └── ...
    └── ...

- **RHI/**
  Enthält die Auftragsordner.
  Jeder Ordner beginnt mit einer vierstelligen Projektnummer und dem Projektnamen, z. B.
  `1243 - Eingreifschutz Rollenbahnen`.

- **CSV-Dateien**
  In jedem Auftragsordner liegt mindestens eine Datei nach dem Muster:
  `heinrich_zeiterfassung_YYYY-MM-DD.csv`.
  Das Programm sucht automatisch die **neueste** CSV-Datei.

- **templates/**
  Hier liegt die Word-Vorlage `Vordruck.docx`, die mit Daten aus der CSV befüllt wird.

---

## Verwendung

Das Programm wird im Projektordner aus der Kommandozeile gestartet.

### Lieferschein erzeugen

    python main.py 1243 liefer

- Liest die CSV im Ordner `RHI/1243 - .../`
- Befüllt die Vorlage `Vordruck.docx`
- Erstellt:
  - `Lieferschein Nr. 1243.docx`
  - `Lieferschein Nr. 1243.pdf` (PDF-Stub in der ersten Version)

### Auftragsbestätigung & Rechnung erzeugen

    python main.py 1243 rechnung 4504049161

- (Geplante Funktion, noch nicht implementiert)
- Liest den vorhandenen Lieferschein
- Erstellt:
  - `Auftragsbestätigung Nr. 1243 - 4504049161.docx/.pdf`
  - `Rechnung Nr. 1243 - 4504049161.docx/.pdf`

---

## Aktueller Stand

- **Funktion „Lieferschein“**: Grundgerüst funktioniert (CSV einlesen, Word-Dokument erzeugen, PDF-Stub).
- **Funktion „Rechnung“**: Platzhalter-Logik und Dateinamen sind vorgesehen, aber noch nicht umgesetzt.
- **Transformationen** der CSV-Daten und das echte PDF-Rendering sind als `TODO` markiert.

---

## Hinweise

- Das Tool ist für den **internen Gebrauch** von Heinrich Metallbau gedacht.
- Fokus liegt auf **Einfachheit und Verständlichkeit**, nicht auf Industriestandards.
- Die Projektordner `RHI/` werden von der Versionsverwaltung ausgeschlossen.
