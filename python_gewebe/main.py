########################################
# Datei: ./main.py
# Beschreibung: Beispielskript zur Verwendung der ML-gestützten NeuesTextVerstehen-Klasse.
########################################

from text_gewebe import NeuesTextVerstehen

# HINWEIS: Bevor Sie dieses Skript ausführen, stellen Sie sicher, dass Sie:
# 1. Mit dem Annotations-UI (dem Next.js-Teil) Trainingsdaten in 'training_data.jsonl' gesammelt haben.
# 2. Das Trainingsskript 'model_trainer.py' ausgeführt haben, um die .joblib-Modelle zu erstellen.
#
# Wenn keine Modelle trainiert wurden, läuft das Skript im heuristischen Fallback-Modus.

# Erstelle eine Instanz des Gewebes.
# Beim Initialisieren wird automatisch nach trainierten Modellen gesucht.
gewebe = NeuesTextVerstehen()

# Füge einige Textfragmente hinzu, um ein komplexes Gewebe zu erzeugen
fragmente_zum_hinzufuegen = [
    "Das Gefühl, das Muster im Ganzen zu erfassen, ist schwer.", # Index 0
    "Es ist immer noch ein Versuch, die Wellen zu zählen.", # Index 1
    "Dieser Versuch ist notwendig, um das Gewebe als Ganzes zu verstehen.", # Index 2
    "Manchmal fühlt es sich harmonisch an, manchmal spannungsreich.", # Index 3
    "Die Fähigkeit, den eigenen Zustand zu fühlen, ist ein Ziel.", # Index 4
    "Ein Beispiel dafür ist die Analyse der dominanten Resonanz-Arten.", # Index 5
    "Aber die wahre Komplexität liegt in der Spürlogik.", # Index 6
    "Das Zählen der Wellen hilft, die Muster zu erfassen.", # Index 7 (für Common Ground Beispiel)
    "Die Spürlogik führt zu einem tieferen Verstehen.", # Index 8 (für Brücken-Beispiel)
    "Das Zählen ist aber nicht das Verstehen selbst." # Index 9 (für Widerspruchs-Beispiel)
]

print("\n=== Aufbau des Gewebes ===")
for fragment in fragmente_zum_hinzufuegen:
    gewebe.fuege_ein(fragment)

print("\n" + "="*40)
print("Zustand des Gewebes nach dem Aufbau:")
gewebe.fuehle_zustand_des_gewebes()
print("="*40)


print("\n=== Analyse der Gewebe-Reaktion ===")
impuls = "Wie fühlt sich das Verstehen an?"
print(f"Spüre Reaktion auf Impuls: '{impuls}'")
reaktion_data = gewebe.spuere_reaktion_des_gewebes(impuls)
# spuere_reaktion_des_gewebes gibt jetzt ein Dictionary zurück, der Bericht ist ein Teil davon
print(reaktion_data['report'])
print("="*40)


print("\n=== Suche nach spezifischen Resonanzen ===")
suche_impuls = "Was ist schwer zu erfassen?"
print(f"Suche Fragmente, die auf '{suche_impuls}' reagieren...")
passende_fragmente = gewebe.finde_fragmente_mit_resonanz(suche_impuls, gewuenschte_arten=['VERSTAERKUNG', 'ERGAENZUNG'], mindest_staerke=0.4)
print("\nPassende Fragmente gefunden:")
if passende_fragmente:
    for res in passende_fragmente:
        print(f"- {res}")
else:
    print("- Keine passenden Fragmente mit den Kriterien gefunden.")
print("="*40)


print("\n=== Generative Antwort aus dem Gewebe ===")
antwort_impuls = "Gibt es einen Konflikt im Verstehen?"
print(f"Generiere Antwort auf Impuls: '{antwort_impuls}' (Ziel: KONTRAST)")
antwort = gewebe.antworte_aus_resonanz(antwort_impuls, ziel_art='KONTRAST')
print(f"\nGeneriertes Fragment wurde dem Gewebe hinzugefügt: '{antwort}'")
print("="*40)

print("\n=== Zustand des Gewebes nach generativer Antwort ===")
gewebe.fuehle_zustand_des_gewebes()
print("="*40)

print("\n=== Logisches Löschen und Verschmelzen ===")
print("Lösche Fragment 1...")
gewebe.loesche_fragment(1)

print("\nVerschmelze Fragment 0 und 2...")
# Beachten Sie, dass die Indices der Fragmente gleich bleiben, auch wenn eines gelöscht wurde.
gewebe.verschmelze_fragmente(0, 2)
print("="*40)

print("\n=== Finaler Zustand des Gewebes ===")
gewebe.fuehle_zustand_des_gewebes()
print("\nInterne Resonanz-Struktur (Ausschnitt):")
# Eine kleine, lesbare Ansicht der Struktur
for i in list(gewebe._resonanzen_struktur.keys())[:3]:
    print(f"  Von {i}: {list(gewebe._resonanzen_struktur[i].values())[:3]}")

print("\nSkript-Ausführung beendet.")