# Automatisierung des Rechnungsprozesses für Heinrich Metallbau

Dieses Programm unterstützt die Erstellung von **Lieferscheinen**, **Auftragsbestätigungen** und **Rechnungen** aus den Zeiterfassungsdaten von Heinrich Metallbau.

---

## Voraussetzungen

* Installiertes **Python 3.12** oder neuer
  (prüfbar in der Kommandozeile mit `python --version`)
* Installierte Abhängigkeiten: `pip install -r requirements.txt`
* Ein vorhandenes **Projektverzeichnis** mit den Projektordnern (`/Pfad/zu/RHI/`)
* Korrekt gesetzter Pfad in der Konfigurationsdatei: `"DATA_ROOT": "/Pfad/zu/RHI/"`

---

## Nutzung als App (Windows)

Das Heinrich Tool kann unter Windows als lokale Web-App genutzt werden, die per Doppelklick gestartet wird.

### Einrichtung

1. Erstelle eine **Desktopverknüpfung** der Datei `scripts/app_windows.vbs`
2. Rechtsklick auf die Verknüpfung → **Eigenschaften**
3. Reiter **Verknüpfung** → **Anderes Symbol…**
4. Wähle die Datei `assets/icon.ico`
5. Fertig

### Nutzung

* Ein Doppelklick auf die Desktopverknüpfung startet die Heinrich App.
* Die App öffnet sich automatisch im Standardbrowser.
* Ist die App bereits geöffnet, wird lediglich ein weiterer Browser-Tab geöffnet.

---

## Nutzung als CLI-Tool

Als CLI-Tool wird das Programm im Projektordner über die Kommandozeile gestartet.

### Lieferschein erzeugen

```
python cli.py 1235 delivery
```

---

### Rechnung & Auftragsbestätigung erzeugen

```
python cli.py 1235 invoice 4504049161
```

---

## Dokumenten-Workflows

Das Tool arbeitet mit klar getrennten Modi. Jeder Modus entspricht einem eigenen Verarbeitungspfad und einem definierten Ergebnis.

Zentral ist ein **zweistufiger Prozess**:

1. Erzeugung eines Lieferscheins inklusive Tabellenbefüllung und Berechnung
2. Ableitung von Rechnung und Auftragsbestätigung aus einem gespeicherten Zwischenstand

---

### Modus `delivery` – Lieferschein erzeugen

**Eingaben**

* `project_number`
* Zeiterfassungs-CSV im Projektordner (automatisch erkannt anhand `project_number`)

**Ablauf**

1. Die CSV-Datei des Projekts wird eingelesen (neueste Datei).
2. Die CSV-Zeilen werden in strukturierte Positionen (Line Items) umgewandelt.
3. Die originale Word-Vorlage (`Vordruck.docx`) wird geladen.
4. Die Positionstabelle wird mit den Line Items befüllt.
5. Ein Teil der Platzhalter wird gesetzt (z. B. Summen, Termine).
6. Ein **Intermediate Template** wird gespeichert.
7. Die restlichen Lieferschein-Platzhalter werden gesetzt.
8. Der Lieferschein wird als DOCX gespeichert.
9. Zusätzlich wird eine PDF-Version erzeugt.

**Ergebnisse**

* `Lieferschein Nr. <project_number>.docx`
* `Lieferschein Nr. <project_number>.pdf`
* Intermediate Template (intern, Grundlage für weitere Dokumente)

---

### Modus `invoice` – Rechnung und Auftragsbestätigung erzeugen

**Eingaben**

* `project_number`
* `receipt_number`
* zuvor erzeugtes Intermediate Template (automatisch erkannt anhand `project_number`)

**Ablauf**

1. Das Intermediate Template wird geladen.
2. Es werden zwei unabhängige Kopien des Dokuments erzeugt.
3. In Kopie A werden die Rechnung-Platzhalter gesetzt.
4. In Kopie B werden die Auftragsbestätigungs-Platzhalter gesetzt.
5. Beide Dokumente werden als DOCX gespeichert.
6. Beide Dokumente werden zusätzlich als PDF erzeugt.

**Ergebnisse**

* `Rechnung Nr. <project_number> - <receipt_number>.docx`
* `Rechnung Nr. <project_number> - <receipt_number>.pdf`
* `Auftragsbestätigung Nr. <project_number> - <receipt_number>.docx`
* `Auftragsbestätigung Nr. <project_number> - <receipt_number>.pdf`

---

## Geplante Erweiterungen (Ausblick)

* UI-basierte Erfassung von Positionen und Erzeugung von Angeboten
* Generierung von E-Rechnungen (z. B. XRechnung / ZUGFeRD)

---

## Test Cases

Project numbers:

- 1218
- 1223
- 1235
- 1236
- 1253

```
python cli.py 1218 delivery
python cli.py 1218 invoice 4504020708

python cli.py 1223 delivery
python cli.py 1223 invoice 4504030989

python cli.py 1235 delivery
python cli.py 1235 invoice 4504049161

python cli.py 1236 delivery
python cli.py 1236 invoice 4504059903

python cli.py 1253 delivery
python cli.py 1253 invoice 4504072524

```
