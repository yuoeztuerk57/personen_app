import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
from manager import PersonManager
from person import Person

manager = PersonManager()
neu_hinzugefuegte_personen = []

def validate_and_add():
    name = name_entry.get().strip()
    age_str = age_entry.get().strip()
    email = email_entry.get().strip()

    if not name or not age_str or not email:
        messagebox.showwarning("Fehler", "Bitte alle Felder ausfüllen.")
        return

    if any(char.isdigit() for char in name):
        messagebox.showerror("Fehler", "Name ungültig: Bitte keine Zahlen im Namen eingeben.")
        return

    try:
        age = int(age_str)
    except ValueError:
        messagebox.showerror("Fehler", "Alter ungültig: Bitte gib nur Zahlen ein.")
        return

    if age < 0 or age > 150:
        messagebox.showerror("Fehler", "Alter ungültig: Bitte einen Wert zwischen 0 und 150 eingeben.")
        return

    if not manager.add_person_obj(name, age, email):
        messagebox.showwarning("Hinweis", f"Die Person '{name}' existiert bereits.")
        return

    neu_hinzugefuegte_personen.append({"name": name, "age": age, "email": email})

    messagebox.showinfo("Erfolg", f"Person '{name}' wurde erfolgreich hinzugefügt.")

    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

    update_text_box()

def update_text_box():
    info_box.config(state="normal")
    info_box.delete("1.0", tk.END)
    
    info_box.insert(tk.END, "=== GELADENE PERSONEN (AUS DATEI) ===\n")
    if not manager.persons:
        info_box.insert(tk.END, "Keine Personen geladen.\n")
    else:
        for idx, person in enumerate(manager.persons, 1):
            ist_neu = any(n["name"] == person.name and n["age"] == person.age and n["email"] == person.email for n in neu_hinzugefuegte_personen)
            if not ist_neu:
                info_box.insert(tk.END, f"{idx}. Name: {person.name} | Alter: {person.age} | E-Mail: {person.email}\n")

    info_box.insert(tk.END, "\n=== NEU HINZUGEFÜGTE PERSONEN (NOCH NICHT GESPEICHERT) ===\n")
    if not neu_hinzugefuegte_personen:
        info_box.insert(tk.END, "Keine neuen Personen hinzugefügt.\n")
    else:
        for idx, item in enumerate(neu_hinzugefuegte_personen, 1):
            info_box.insert(tk.END, f"{idx}. Name: {item['name']} | Alter: {item['age']} | E-Mail: {item['email']}\n")

    info_box.config(state="disabled")

FORMATE = ("csv", "json", "xml")

def set_filename_entry(filename):
    file_entry.delete(0, tk.END)
    file_entry.insert(0, filename)

def get_filename(ext):
    """Liefert den Dateinamen passend zum Format.
    Die Endung im Feld wird immer durch die des gewählten Formats ersetzt,
    damit z.B. 'persons.csv' nie als XML gelesen wird."""
    name = file_entry.get().strip()
    if not name:
        return f"persons.{ext}"
    base, old_ext = os.path.splitext(name)
    if old_ext.lower().lstrip(".") in FORMATE:
        name = base
    return f"{name}.{ext}"

def do_load(ext):
    fname = get_filename(ext)
    success, msg = manager.load(ext, fname)
    if not success:
        messagebox.showerror("Fehler", msg)
        return

    # Noch nicht gespeicherte neue Personen bleiben erhalten.
    # Steht eine davon schon in der Datei, ist sie nicht mehr "neu".
    noch_neu = [item for item in neu_hinzugefuegte_personen
                if manager.add_person_obj(item["name"], item["age"], item["email"])]
    neu_hinzugefuegte_personen[:] = noch_neu

    set_filename_entry(fname)
    messagebox.showinfo("Laden", msg)
    update_text_box()

def do_save(ext):
    fname = get_filename(ext)
    neue = [Person(item["name"], item["age"], item["email"]) for item in neu_hinzugefuegte_personen]

    # Der Manager liest die bestehende Datei, hängt die neuen Personen an und schreibt sie zurück
    success, msg = manager.add_to_file(ext, fname, neue)
    if not success:
        messagebox.showerror("Fehler", msg)
        return

    neu_hinzugefuegte_personen.clear()
    set_filename_entry(fname)
    messagebox.showinfo("Speichern", msg)
    update_text_box()

def action_load_csv():  do_load("csv")
def action_load_json(): do_load("json")
def action_load_xml():  do_load("xml")
def action_save_csv():  do_save("csv")
def action_save_json(): do_save("json")
def action_save_xml():  do_save("xml")


# ---------------------------------------------------------------------------
# GUI-Aufbau (grid-Layout statt place -> alles richtet sich sauber aus)
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("Persons Manager GUI")

font_style = ("Arial", 11)
btn_bg = "#00a2ed"
btn_fg = "black"

# Festbreiten-Schrift, die auf jedem System vorhanden ist
mono_font = tkfont.nametofont("TkFixedFont").copy()
mono_font.configure(size=10)

# Hauptrahmen mit Rand rundherum
main = tk.Frame(root, padx=20, pady=20)
main.pack(fill="both", expand=True)

# --- Oberer Block: Eingabefelder links, Buttons rechts -------------------
top = tk.Frame(main)
top.pack(fill="x")
top.columnconfigure(2, weight=1)  # flexibler Abstand zwischen links und rechts

# Spalte 0: Beschriftungen (volle Breite, nichts abgeschnitten)
tk.Label(top, text="Name:", font=font_style, anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
tk.Label(top, text="Alter:", font=font_style, anchor="w").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
tk.Label(top, text="E-Mail:", font=font_style, anchor="w").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=6)

# Spalte 1: Eingabefelder (alle gleich breit)
name_entry = tk.Entry(top, font=font_style, width=24)
name_entry.grid(row=0, column=1, sticky="ew", pady=6)
age_entry = tk.Entry(top, font=font_style, width=24)
age_entry.grid(row=1, column=1, sticky="ew", pady=6)
email_entry = tk.Entry(top, font=font_style, width=24)
email_entry.grid(row=2, column=1, sticky="ew", pady=6)

# Hinzufügen-Button: gleiche Breite wie die Eingabefelder (sticky="ew"), unter E-Mail
add_btn = tk.Button(top, text="Hinzufügen", font=font_style, bg=btn_bg, fg=btn_fg,
                    activebackground=btn_bg, command=validate_and_add)
add_btn.grid(row=3, column=1, sticky="ew", pady=(12, 0))

# Spalten 3-5: Laden & Speichern (rechtsbündig am Rand der Info-Box)
def make_btn(text, command, row, col):
    tk.Button(top, text=text, font=font_style, bg=btn_bg, fg=btn_fg,
              activebackground=btn_bg, width=14, command=command
              ).grid(row=row, column=col, sticky="ew", padx=(8, 0), pady=6)

make_btn("CSV laden",      action_load_csv,  0, 3)
make_btn("XML laden",      action_load_xml,  0, 4)
make_btn("JSON laden",     action_load_json, 0, 5)
make_btn("CSV speichern",  action_save_csv,  1, 3)
make_btn("XML speichern",  action_save_xml,  1, 4)
make_btn("JSON speichern", action_save_json, 1, 5)

# Dateiname: Label in Spalte 3, Textfeld über Spalte 4-5 -> endet bündig mit "JSON speichern"
tk.Label(top, text="Dateiname:", font=font_style, anchor="w").grid(row=3, column=3, sticky="w", padx=(8, 0), pady=(12, 0))
file_entry = tk.Entry(top, font=font_style)
file_entry.grid(row=3, column=4, columnspan=2, sticky="ew", padx=(8, 0), pady=(12, 0))

# --- Info-Box unten: bestimmt die Gesamtbreite des Fensters ---------------
info_frame = tk.Frame(main)
info_frame.pack(fill="both", expand=True, pady=(20, 0))

info_box = tk.Text(info_frame, width=100, height=14, font=mono_font, wrap="none",
                   state="disabled", relief="solid", borderwidth=1, padx=8, pady=6)
scrollbar = tk.Scrollbar(info_frame, orient="vertical", command=info_box.yview)
info_box.config(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
info_box.pack(side="left", fill="both", expand=True)

update_text_box()

root.update_idletasks()
root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())

root.mainloop()