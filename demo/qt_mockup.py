"""Qt-Entwurf der geplanten Oberfläche — reines Frontend, keine Backend-Logik."""

import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Dokumenttyp -> (Belegnummer-Regel, Liefertermin-Vorbelegung in Tagen)
DOC_TYPES = {
    "Angebot": ("keine", 21),
    "Lieferschein": ("optional", 0),
    "Rechnung": ("pflicht", 0),
    "Auftragsbestätigung": ("pflicht", 0),
}

STYLE = """
QMainWindow { background: #ffffff; }
QWidget#Page { background: #ffffff; }
QWidget#Row { background: transparent; }
QListWidget#Sidebar { background: #f4f4f6; border: none; border-right: 1px solid #e2e2e6;
                      outline: 0; padding-top: 8px; }
QListWidget#Sidebar::item { padding: 9px 16px; border: none; color: #33333a; }
QListWidget#Sidebar::item:selected { background: #e0e0e8; color: #111118; }
QListWidget#Sidebar::item:hover { background: #eaeaf0; }
#Title { font-size: 24px; font-weight: 600; }
#Subtitle { color: #666; }
#Card { background: #fbfbfc; border: 1px solid #e2e2e6; border-radius: 6px; }
#SectionLabel { font-size: 15px; font-weight: 600; margin-top: 4px; }
QPushButton { padding: 7px 16px; border: 1px solid #cfcfd6; border-radius: 5px; background: #fff; }
QPushButton:hover { background: #f2f2f5; }
QPushButton#Primary { background: #2f2f36; color: #fff; border: 1px solid #2f2f36; }
QPushButton#Primary:hover { background: #45454e; }
QLineEdit, QComboBox { padding: 6px 8px; border: 1px solid #cfcfd6; border-radius: 5px;
                       background: #fff; }
QLineEdit:disabled { background: #f2f2f4; color: #999; }
QPlainTextEdit { border: 1px solid #e2e2e6; border-radius: 5px; background: #f7f7f9; }
QTableWidget { border: 1px solid #e2e2e6; gridline-color: #ececf0; background: #fff; }
QHeaderView::section { background: #f4f4f6; border: none; border-bottom: 1px solid #e2e2e6;
                       padding: 6px; }
#Hint { color: #777; font-size: 12px; }
"""

DEMO_TIMESHEET = [
    ("01.08.2025", "4504049161", "Geländer montiert", "8,0", "59,90", "0,00", "479,20"),
    ("02.08.2025", "4504049161", "Materialkauf Stahl", "0,0", "59,90", "212,40", "212,40"),
    ("04.08.2025", "4504049161", "Schweißarbeiten", "6,5", "59,90", "0,00", "389,35"),
    ("05.08.2025", "123", "Notiz ohne Auftrag", "2,0", "59,90", "0,00", "119,80"),
    ("07.08.2025", "4504049161", "Endmontage", "4,0", "72,00", "48,90", "336,90"),
]

DEMO_HOURS = [
    ("1235", "01.08.2025", "4504049161", "Meisterstunde", "8,0", "59,90 €", "479,20 €"),
    ("1235", "04.08.2025", "4504049161", "Meisterstunde", "6,5", "59,90 €", "389,35 €"),
    ("1235", "07.08.2025", "4504049161", "Meisterstunde", "4,0", "72,00 €", "288,00 €"),
    ("1236", "12.08.2025", "4504059903", "Helferstunde", "7,5", "35,00 €", "262,50 €"),
    ("1253", "09.09.2025", "4504072524", "Meisterstunde", "9,0", "59,90 €", "539,10 €"),
]


# — Hilfsfunktionen ————————————————————————————————————————————————————————————


def _row(*widgets: QWidget, stretch: bool = False) -> QWidget:
    """Waagerechter Container ohne eigenen Hintergrund."""
    container = QWidget()
    container.setObjectName("Row")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    for widget in widgets:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch()
    return container


def _card(*widgets: QWidget) -> QFrame:
    """Umrandeter Block, entspricht den Formularkästen der Streamlit-Version."""
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)
    for widget in widgets:
        layout.addWidget(widget)
    return frame


def _section(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("SectionLabel")
    return label


def _hint(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Hint")
    label.setWordWrap(True)
    return label


def _table(headers: list[str], rows: list[tuple]) -> QTableWidget:
    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(value))
    return table


# — Seite: Dokumente ———————————————————————————————————————————————————————————


class DocumentsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.doc_type = QComboBox()
        self.doc_type.addItems(DOC_TYPES.keys())
        self.doc_type.currentTextChanged.connect(self._on_doc_type_changed)

        self.project_number = QLineEdit(placeholderText="z. B. 1235")
        self.receipt_number = QLineEdit(placeholderText="z. B. 4504049161")

        self.delivery_days = QSpinBox(minimum=0, maximum=365, suffix=" Tage")
        self.delivery_days.setMinimumWidth(110)
        self.delivery_days.valueChanged.connect(self._on_days_changed)

        self.delivery_date = QDateEdit(calendarPopup=True)
        self.delivery_date.setDisplayFormat("dd.MM.yyyy")
        self.delivery_date.setMinimumWidth(130)
        self.delivery_date.dateChanged.connect(self._on_date_changed)

        delivery_row = _row(
            self.delivery_days, QLabel("entspricht"), self.delivery_date, stretch=True
        )

        form = QWidget()
        form.setObjectName("Row")
        form_layout = QFormLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        form_layout.addRow("Dokumenttyp", self.doc_type)
        form_layout.addRow("Projektnummer", self.project_number)
        form_layout.addRow("Belegnummer", self.receipt_number)
        form_layout.addRow("Liefertermin", delivery_row)

        self.generate_button = QPushButton("Dokument erzeugen")
        self.generate_button.setObjectName("Primary")
        self.generate_button.clicked.connect(self._on_generate)

        button_row = _row(self.generate_button, stretch=True)

        self.output = QPlainTextEdit(readOnly=True)
        self.output.setFont(QFont("monospace", 9))
        self.output.setMinimumHeight(180)
        self.output.setPlainText("Noch kein Dokument erzeugt.")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(_section("Dokument erzeugen"))
        layout.addWidget(_card(form, button_row))
        layout.addWidget(_section("Verlauf"))
        layout.addWidget(self.output)

        self._on_doc_type_changed(self.doc_type.currentText())

    def _on_doc_type_changed(self, doc_type: str):
        rule, default_days = DOC_TYPES[doc_type]
        self.receipt_number.setEnabled(rule != "keine")
        if rule == "keine":
            self.receipt_number.clear()
            self.receipt_number.setPlaceholderText("für Angebot nicht erforderlich")
        elif rule == "optional":
            self.receipt_number.setPlaceholderText("optional — z. B. 4504049161")
        else:
            self.receipt_number.setPlaceholderText("erforderlich — z. B. 4504049161")
        self.delivery_days.setValue(default_days)

    def _on_days_changed(self, days: int):
        self.delivery_date.blockSignals(True)
        self.delivery_date.setDate(QDate.currentDate().addDays(days))
        self.delivery_date.blockSignals(False)

    def _on_date_changed(self, value: QDate):
        self.delivery_days.blockSignals(True)
        self.delivery_days.setValue(max(0, QDate.currentDate().daysTo(value)))
        self.delivery_days.blockSignals(False)

    def _on_generate(self):
        doc_type = self.doc_type.currentText()
        project = self.project_number.text().strip() or "1235"
        self.output.setPlainText(
            "\n".join(
                [
                    f"Projektordner gefunden: RHI/{project} - Allgemein Juli",
                    "CSV Datei gefunden: heinrich_zeiterfassung_2025-08-01.csv",
                    "Achtung: Überspringe Zeile 4 mit ungültiger Auftrags-Nr. 123",
                    f"{doc_type} erzeugt: {doc_type} Nr. {project}.docx",
                    f"PDF erzeugt: {doc_type} Nr. {project}.pdf",
                ]
            )
        )


# — Seite: Zeiterfassung ———————————————————————————————————————————————————————


class TimesheetPage(QWidget):
    def __init__(self):
        super().__init__()

        headers = [
            "Datum", "Auftrags-Nr.", "Beschreibung", "Dauer (Std)",
            "Stundensatz (€)", "Material (€)", "Gesamtkosten (€)",
        ]
        table = _table(headers, DEMO_TIMESHEET)

        path_row = _row(
            QLabel("Datei:"),
            QLineEdit("heinrich_zeiterfassung_2025-08-01.csv", readOnly=True),
            QPushButton("Andere Datei…"),
        )

        save = QPushButton("Änderungen speichern")
        save.setObjectName("Primary")
        button_row = _row(save, QPushButton("Verwerfen"), stretch=True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(_section("Zeiterfassung bearbeiten"))
        layout.addWidget(path_row)
        layout.addWidget(table)
        layout.addWidget(
            _hint(
                "Änderungen werden in dieselbe Datei zurückgeschrieben — im "
                "ursprünglichen Format, ohne Umweg über Excel."
            )
        )
        layout.addWidget(button_row)


# — Seite: Stunden —————————————————————————————————————————————————————————————


class HoursPage(QWidget):
    def __init__(self):
        super().__init__()

        headers = ["Projekt", "Datum", "Auftrags-Nr.", "Art", "Stunden", "Satz", "Betrag"]
        table = _table(headers, DEMO_HOURS)

        total = QLabel("Gesamt: 35,0 Stunden · 1.958,15 €")
        total.setObjectName("SectionLabel")

        export = QPushButton("Als CSV exportieren")
        export.setObjectName("Primary")
        button_row = QWidget()
        button_row.setObjectName("Row")
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(export)
        button_layout.addStretch()
        button_layout.addWidget(total)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(_section("Erfasste Stunden — alle Projekte"))
        layout.addWidget(table)
        layout.addWidget(
            _hint(
                "Wird bei jedem Öffnen neu aus den Projektordnern berechnet und ist "
                "damit immer aktuell."
            )
        )
        layout.addWidget(button_row)


# — Seite: Einstellungen ———————————————————————————————————————————————————————


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.data_root = QLineEdit("C:\\Users\\max\\OneDrive\\RHI", readOnly=True)
        browse = QPushButton("Ordner wählen…")
        browse.clicked.connect(self._on_browse)

        root_row = _row(self.data_root, browse)

        form = QWidget()
        form.setObjectName("Row")
        form_layout = QFormLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        form_layout.addRow("RHI-Ordner", root_row)
        form_layout.addRow("Konfiguration", QLineEdit("RHI/heinrich_config.json", readOnly=True))
        form_layout.addRow("Word-Vorlage", QLineEdit("RHI/Vordruck.docx", readOnly=True))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(_section("Einstellungen"))
        layout.addWidget(_card(form))
        layout.addWidget(
            _hint(
                "Nur der RHI-Ordner wird auf diesem Rechner gespeichert. Konfiguration "
                "und Word-Vorlage liegen im RHI-Ordner selbst und stehen dadurch über "
                "OneDrive auf allen Rechnern zur Verfügung. Die Konfiguration wird im "
                "Texteditor bearbeitet."
            )
        )
        layout.addStretch()

    def _on_browse(self):
        chosen = QFileDialog.getExistingDirectory(self, "RHI-Ordner wählen")
        if chosen:
            self.data_root.setText(chosen)


# — Hauptfenster ———————————————————————————————————————————————————————————————


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heinrich App — RHI Abrechnung")
        self.resize(1040, 720)

        title = QLabel("RHI Abrechnung")
        title.setObjectName("Title")
        subtitle = QLabel(
            "Angebote, Lieferscheine, Rechnungen und Auftragsbestätigungen "
            "direkt aus den Zeiterfassungsdaten."
        )
        subtitle.setObjectName("Subtitle")

        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        text_column.addWidget(title)
        text_column.addWidget(subtitle)

        logo = QLabel()
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            logo.setPixmap(
                QPixmap(str(logo_path)).scaledToHeight(
                    44, Qt.TransformationMode.SmoothTransformation
                )
            )

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 22, 28, 14)
        header_layout.addLayout(text_column)
        header_layout.addStretch()
        header_layout.addWidget(logo)

        self.nav = QListWidget()
        self.nav.setObjectName("Sidebar")
        self.nav.addItems(["Dokumente", "Zeiterfassung", "Stunden", "Einstellungen"])
        self.nav.setFixedWidth(180)
        self.nav.setCurrentRow(0)

        self.pages = QStackedWidget()
        for page in (DocumentsPage(), TimesheetPage(), HoursPage(), SettingsPage()):
            container = QWidget()
            container.setObjectName("Page")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(28, 8, 28, 24)
            container_layout.addWidget(page)
            self.pages.addWidget(container)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self.nav)
        body_layout.addWidget(self.pages)

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(header)
        central_layout.addWidget(body)
        self.setCentralWidget(central)

        self.statusBar().showMessage("Entwurf — ohne Backend-Logik")


# — Einstieg ———————————————————————————————————————————————————————————————————


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = MainWindow()

    if "--screenshot" in sys.argv:
        target = sys.argv[sys.argv.index("--screenshot") + 1]
        page = int(sys.argv[sys.argv.index("--page") + 1]) if "--page" in sys.argv else 0
        window.nav.setCurrentRow(page)
        window.show()
        app.processEvents()
        window.grab().save(target)
        print(f"gespeichert: {target}")
        return

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
