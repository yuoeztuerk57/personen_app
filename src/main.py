import sys
from manager import PersonManager

manager = PersonManager()

def person_eingeben():
    print("Neue Person hinzufügen")
    name = input("Name: ").strip()
    alter = input("Alter: ").strip()
    adresse = input("Adresse: ").strip()
    manager.person_hinzufuegen(name, alter, adresse)

def menu():
    while True:
        print("PERSONEN VERWALTUNG")
        print("1. Add person")
        print("2. Save to CSV")
        print("3. Save to XML")
        print("4. Save to JSON")
        print("5. Exit")
        wahl = input("Wahl (1-5): ").strip()

        if wahl == "1":
            person_eingeben()
        elif wahl == "2":
            manager.save_to_csv()
        elif wahl == "3":
            manager.save_to_xml()
        elif wahl == "4":
            manager.save_to_json()
        elif wahl == "5":
            print("Programm beendet.")
            sys.exit(0)
        else:
            print("Ungültige Eingabe, bitte 1-5 wählen.")

if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "-a":
        cli_name = sys.argv[2]
        cli_alter = sys.argv[3]
        cli_adresse = sys.argv[4]
        manager.person_hinzufuegen(cli_name, cli_alter, cli_adresse)
        menu()
    else:
        menu()