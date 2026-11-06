import argparse
from manager import PersonManager
from person import Person

def main():
    parser = argparse.ArgumentParser(description="Person Management Application")
    parser.add_argument("-c", "--csv", metavar="FILENAME", help="CSV Dateiname")
    parser.add_argument("-a", "--add", nargs=3, metavar=("NAME", "AGE", "EMAIL"), help="Person hinzufügen")
    args = parser.parse_args()

    manager = PersonManager()

    if args.add:
        if not args.csv:
            parser.error("-a erfordert -c FILENAME")
        name, age, email = args.add
        person = Person(name, int(age), email)
        manager.persons.append(person)
        manager.save_csv(args.csv)
        print(f"Person '{name}' erfolgreich hinzugefügt und in {args.csv} gespeichert.")
        return

    while True:
        print("\n-------------------")
        print("    Persons Manager")
        print("-------------------")
        print("1. Add Person")
        print("2. Save to CSV")
        print("3. Save to XML")
        print("4. Save to JSON")
        print("5. Show Persons")
        print("6. Exit")

        choice = input("\nOption wählen: ").strip()

        match choice:
            case "1":
                manager.add_person()
            case "2":
                manager.save_csv()
            case "3":
                manager.save_xml()
            case "4":
                manager.save_json()
            case "5":
                manager.show_persons()
            case "6":
                print("\nProgramm beendet.")
                break
            case _:
                print("\nOption nicht erlaubt.")

if __name__ == "__main__":
    main()