import csv
import json
import os
import xml.etree.ElementTree as ET
from person import Person

class PersonManager:
    def __init__(self):
        self.personen_liste = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def person_hinzufuegen(self, name, alter, adresse):
        person = Person(name, alter, adresse)
        self.personen_liste.append(person)
        print(f"{name} wurde vorübergehend im Speicher abgelegt.")

    def save_to_csv(self):
        if not self.personen_liste:
            print("Keine Personen im Arbeitsspeicher zum Speichern vorhanden.")
            return

        file_path = os.path.join(self.data_dir, "personen.csv")
        datei_existiert = os.path.exists(file_path)

        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            if not datei_existiert:
                writer.writerow(["Name", "Alter", "Adresse"])
            for p in self.personen_liste:
                writer.writerow([p.name, p.alter, p.adresse])

        print(f"{len(self.personen_liste)} Person(en) erfolgreich in data/personen.csv gespeichert.")
        self.personen_liste.clear()

    def save_to_xml(self):
        if not self.personen_liste:
            print("Keine Personen im Arbeitsspeicher zum Speichern vorhanden.")
            return

        file_path = os.path.join(self.data_dir, "personen.xml")
        datei_existiert = os.path.exists(file_path)

        if datei_existiert:
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
            except ET.ParseError:
                root = ET.Element("personen")
                tree = ET.ElementTree(root)
        else:
            root = ET.Element("personen")
            tree = ET.ElementTree(root)

        for p in self.personen_liste:
            person_elem = ET.SubElement(root, "person")
            ET.SubElement(person_elem, "name").text = str(p.name)
            ET.SubElement(person_elem, "alter").text = str(p.alter)
            ET.SubElement(person_elem, "adresse").text = str(p.adresse)

        ET.indent(tree, space="    ")
        with open(file_path, "wb") as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)

        print(f"{len(self.personen_liste)} Person(en) erfolgreich in data/personen.xml gespeichert.")
        self.personen_liste.clear()

    def save_to_json(self):
        if not self.personen_liste:
            print("Keine Personen im Arbeitsspeicher zum Speichern vorhanden.")
            return

        file_path = os.path.join(self.data_dir, "personen.json")
        bisherige_daten = []

        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    bisherige_daten = json.load(file)
            except json.JSONDecodeError:
                bisherige_daten = []

        neue_daten = [p.to_dict() for p in self.personen_liste]
        bisherige_daten.extend(neue_daten)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(bisherige_daten, file, indent=4, ensure_ascii=False)

        print(f"{len(self.personen_liste)} Person(en) erfolgreich in data/personen.json gespeichert.")
        self.personen_liste.clear()