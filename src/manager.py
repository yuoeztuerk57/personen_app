"""Verwaltung der Personen: Laden und Speichern als CSV, JSON und XML."""
from dataclasses import asdict
from pathlib import Path
import csv
import json
import xml.etree.ElementTree as ET

from person import Person

# Trennzeichen beim SPEICHERN von CSV (";" öffnet sich in deutschem Excel sauber).
# Beim LADEN wird das Trennzeichen automatisch erkannt (; , oder Tab).
CSV_DELIMITER = ";"

FIELDS = ["name", "age", "email"]

# Akzeptierte Spaltennamen je Feld (klein geschrieben).
# Dadurch werden auch ältere Dateien wie "Name;Alter;Adresse" gelesen.
FIELD_ALIASES = {
    "name": ("name",),
    "age": ("age", "alter"),
    "email": ("email", "e-mail", "mail", "adresse"),
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def person_from_dict(data: dict) -> Person:
    """Baut eine Person aus einem Dict (Groß-/Kleinschreibung egal, alte Namen erlaubt)."""
    data = {str(key).strip().lower(): value for key, value in data.items() if key is not None}

    values = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if data.get(alias) is not None:
                values[field] = str(data[alias]).strip()
                break
        else:
            raise ValueError(f"Feld '{field}' fehlt (erwartet: {' / '.join(aliases)})")

    try:
        age = int(values["age"])
    except ValueError:
        raise ValueError(f"Alter '{values['age']}' ist keine ganze Zahl") from None

    return Person(values["name"], age, values["email"])


def person_key(person: Person) -> tuple:
    """Schlüssel zum Erkennen von Duplikaten (ohne Groß-/Kleinschreibung)."""
    return (person.name.strip().lower(), str(person.age).strip(), person.email.strip().lower())


def _write_atomic(path: Path, writer) -> None:
    """Schreibt erst in eine temporäre Datei und ersetzt dann die echte Datei.
    So bleibt die alte Datei heil, falls beim Schreiben etwas schiefgeht."""
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        writer(tmp_path)
        tmp_path.replace(path)
    finally:
        tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Lesen / Schreiben je Format
# ---------------------------------------------------------------------------
def _read_csv(path: Path) -> list:
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        first_line = file.readline()
        file.seek(0)
        delimiter = max(";,\t", key=first_line.count)  # häufigstes Trennzeichen der Kopfzeile
        reader = csv.DictReader(file, delimiter=delimiter)

        persons = []
        for line_no, row in enumerate(reader, start=2):
            if not any(value for value in row.values() if value):
                continue  # leere Zeile
            try:
                persons.append(person_from_dict(row))
            except ValueError as error:
                raise ValueError(f"Zeile {line_no}: {error}") from None
    return persons


def _write_csv(path: Path, persons: list) -> None:
    # utf-8-sig: Excel erkennt Umlaute damit korrekt
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, delimiter=CSV_DELIMITER)
        writer.writeheader()
        for person in persons:
            writer.writerow(asdict(person))


def _read_json(path: Path) -> list:
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Die Datei muss eine Liste von Personen enthalten.")

    persons = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Eintrag {index} ist kein Objekt.")
        try:
            persons.append(person_from_dict(item))
        except ValueError as error:
            raise ValueError(f"Eintrag {index}: {error}") from None
    return persons


def _write_json(path: Path, persons: list) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump([asdict(person) for person in persons], file, indent=4, ensure_ascii=False)


def _read_xml(path: Path) -> list:
    root = ET.parse(path).getroot()

    persons = []
    for index, element in enumerate(root.findall("person"), start=1):
        data = {child.tag: (child.text or "") for child in element}
        try:
            persons.append(person_from_dict(data))
        except ValueError as error:
            raise ValueError(f"Person {index}: {error}") from None
    return persons


def _write_xml(path: Path, persons: list) -> None:
    root = ET.Element("persons")
    for person in persons:
        element = ET.SubElement(root, "person")
        ET.SubElement(element, "name").text = person.name
        ET.SubElement(element, "age").text = str(person.age)
        ET.SubElement(element, "email").text = person.email

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


# Format -> (Anzeigename, Lesefunktion, Schreibfunktion)
FORMATS = {
    "csv": ("CSV", _read_csv, _write_csv),
    "json": ("JSON", _read_json, _write_json),
    "xml": ("XML", _read_xml, _write_xml),
}

# Fehler, die beim Lesen einer Datei auftreten können
READ_ERRORS = (OSError, ValueError, ET.ParseError)  # JSONDecodeError und UnicodeDecodeError sind ValueErrors


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------
class PersonManager:
    def __init__(self) -> None:
        self.persons = []
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

    def path_for(self, filename: str) -> Path:
        """Dateien liegen immer im data-Ordner (Pfadanteile im Namen werden ignoriert)."""
        return self.data_dir / Path(filename).name

    def add_person_obj(self, name: str, age: int, email: str) -> bool:
        """Fügt eine Person hinzu. Gibt False zurück, wenn es sie schon gibt."""
        person = Person(name, age, email)
        if person_key(person) in {person_key(p) for p in self.persons}:
            return False
        self.persons.append(person)
        return True

    # --- allgemeine Funktionen ------------------------------------------------
    def load(self, fmt: str, filename: str = None):
        """Ersetzt self.persons durch den Dateiinhalt. Bei Fehlern bleibt alles unverändert."""
        label, reader, _ = FORMATS[fmt]
        path = self.path_for(filename or f"persons.{fmt}")
        if not path.exists():
            return False, f"Datei '{path.name}' existiert nicht."
        try:
            persons = reader(path)
        except READ_ERRORS as error:
            return False, f"{label} Ladefehler in '{path.name}': {error}"
        self.persons = persons
        return True, f"{len(persons)} Person(en) aus {label} geladen."

    def save(self, fmt: str, filename: str = None):
        """Schreibt self.persons komplett in die Datei (überschreibt sie)."""
        label, _, writer = FORMATS[fmt]
        path = self.path_for(filename or f"persons.{fmt}")
        try:
            _write_atomic(path, lambda tmp: writer(tmp, self.persons))
        except OSError as error:
            return False, f"{label}-Fehler: {error}"
        return True, f"{label} gespeichert: {path.name}"

    def add_to_file(self, fmt: str, filename: str, new_persons: list):
        """Liest die bestehende Datei, hängt die neuen Personen an (ohne Duplikate)
        und schreibt alles zurück. Danach entspricht self.persons dem Dateiinhalt."""
        label, reader, writer = FORMATS[fmt]
        path = self.path_for(filename or f"persons.{fmt}")

        merged = []
        if path.exists() and path.stat().st_size > 0:
            try:
                merged = reader(path)
            except READ_ERRORS as error:
                return False, (f"{label}: Die bestehende Datei '{path.name}' konnte nicht gelesen "
                               f"werden. Es wurde nichts überschrieben.\n\n{error}")

        known = {person_key(p) for p in merged}
        added = 0
        for person in new_persons:
            if person_key(person) not in known:
                merged.append(person)
                known.add(person_key(person))
                added += 1

        try:
            _write_atomic(path, lambda tmp: writer(tmp, merged))
        except OSError as error:
            return False, f"{label}-Fehler: {error}"

        self.persons = merged
        return True, f"{label} gespeichert: {path.name}\n{added} neue Person(en), insgesamt {len(merged)}."

    # --- einfache Kurzformen (wie bisher) ------------------------------------
    def save_csv(self, filename="persons.csv"):
        return self.save("csv", filename)

    def save_json(self, filename="persons.json"):
        return self.save("json", filename)

    def save_xml(self, filename="persons.xml"):
        return self.save("xml", filename)

    def load_csv(self, filename="persons.csv"):
        return self.load("csv", filename)

    def load_json(self, filename="persons.json"):
        return self.load("json", filename)

    def load_xml(self, filename="persons.xml"):
        return self.load("xml", filename)