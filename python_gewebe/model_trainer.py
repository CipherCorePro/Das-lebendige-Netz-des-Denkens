import json
import numpy as np
import spacy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Konstanten für Dateipfade
DATA_FILE = 'training_data.jsonl'
ART_CLASSIFIER_FILE = 'triadic_art_classifier.joblib'
STAERKE_REGRESSOR_FILE = 'triadic_staerke_regressor.joblib'
LABEL_ENCODER_FILE = 'triadic_label_encoder.joblib'

def load_data(filepath=DATA_FILE):
    """Lädt die .jsonl Trainingsdaten."""
    if not os.path.exists(filepath):
        print(f"Fehler: Trainingsdatendatei '{filepath}' nicht gefunden.")
        print("Bitte erstellen Sie zuerst Trainingsdaten mit dem Next.js Annotator.")
        return []
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warnung: Ungültige JSON-Zeile übersprungen in {filepath}")
    return data

def create_features_and_labels(data, nlp):
    """Erstellt Feature-Vektoren und Labels aus den Rohdaten."""
    features = []
    labels_art = []
    labels_staerke = []
    
    print(f"Verarbeite {len(data)} Datenpunkte...")
    for i, sample in enumerate(data):
        print(f"  Verarbeite Punkt {i+1}/{len(data)}...", end='\r')
        doc_a = nlp(sample['fragment_a'])
        doc_b = nlp(sample['fragment_b'])
        doc_c = nlp(sample['fragment_c'])
        
        # Feature-Vektor: Konkatenation der spaCy-Vektoren der drei Fragmente
        feature_vector = np.concatenate([doc_a.vector, doc_b.vector, doc_c.vector])
        features.append(feature_vector)
        
        labels_art.append(sample['label']['ergebnis_art'])
        labels_staerke.append(float(sample['label']['ergebnis_staerke']))
        
    print("\nFeature-Erstellung abgeschlossen.")
    return np.array(features), np.array(labels_art), np.array(labels_staerke)

def train():
    """Der Haupt-Trainingsprozess."""
    print("="*50)
    print("Starte Trainingsprozess für triadische Resonanz-Modelle")
    print("="*50)
    
    # 1. Daten laden
    trainingsdaten = load_data()
    if len(trainingsdaten) < 10:
        print(f"Nicht genügend Trainingsdaten ({len(trainingsdaten)}). Training wird abgebrochen.")
        print("Es werden mindestens 10 annotierte Beispiele benötigt, um die Modelle sinnvoll zu trainieren.")
        return

    # 2. NLP-Modell laden und Features erstellen
    print("\nLade spaCy-Modell 'de_core_news_lg' (kann einen Moment dauern)...")
    try:
        nlp = spacy.load("de_core_news_lg")
    except IOError:
        print("\n[FEHLER] spaCy-Modell 'de_core_news_lg' nicht gefunden.")
        print("Bitte führen Sie aus: python -m spacy download de_core_news_lg")
        return
    
    X, y_art_str, y_staerke = create_features_and_labels(trainingsdaten, nlp)
    
    # Label-Encoding für Resonanz-Arten (z.B. 'VERSTAERKUNG' -> 0)
    le = LabelEncoder()
    y_art = le.fit_transform(y_art_str)
    
    # 3. Aufteilung in Trainings- und Testsets (75% Training, 25% Test)
    # Stratify sorgt für eine gleichmäßige Verteilung der Klassen im Trainings- und Testset
    stratify_labels = y_art if len(np.unique(y_art)) > 1 else None
    X_train, X_test, y_art_train, y_art_test, y_staerke_train, y_staerke_test = \
        train_test_split(X, y_art, y_staerke, test_size=0.25, random_state=42, stratify=stratify_labels)
    
    print(f"\nDaten aufgeteilt: {len(X_train)} Trainingsbeispiele, {len(X_test)} Testbeispiele.")

    # 4. Modell für die Resonanz-Art trainieren (Klassifikation)
    print("\nTrainiere Klassifikationsmodell (RandomForestClassifier)...")
    art_classifier = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    art_classifier.fit(X_train, y_art_train)
    
    # 5. Modell für die Resonanz-Stärke trainieren (Regression)
    print("Trainiere Regressionsmodell (RandomForestRegressor)...")
    staerke_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    staerke_regressor.fit(X_train, y_staerke_train)
    
    # 6. Modelle evaluieren und Ergebnisse ausgeben
    print("\n" + "="*20 + " EVALUATION " + "="*21)
    y_art_pred = art_classifier.predict(X_test)
    print("\nKlassifikations-Report (Resonanz-Art):")
    # Sicherstellen, dass die Zielnamen korrekt sind, auch wenn im Testset nicht alle vorkommen
    target_names = le.inverse_transform(sorted(np.unique(np.concatenate((y_art_test, y_art_pred)))))
    print(classification_report(y_art_test, y_art_pred, target_names=target_names, zero_division=0))
    
    y_staerke_pred = staerke_regressor.predict(X_test)
    print("\nRegressions-Report (Resonanz-Stärke):")
    print(f"  Mean Squared Error: {mean_squared_error(y_staerke_test, y_staerke_pred):.4f}")
    print(f"  R² Score (Bestimmtheitsmaß): {r2_score(y_staerke_test, y_staerke_pred):.4f}")
    
    # 7. Modelle und LabelEncoder für die spätere Verwendung speichern
    print("\n" + "="*18 + " SPEICHERN " + "="*20)
    joblib.dump(art_classifier, ART_CLASSIFIER_FILE)
    joblib.dump(staerke_regressor, STAERKE_REGRESSOR_FILE)
    joblib.dump(le, LABEL_ENCODER_FILE)
    
    print(f"Modelle erfolgreich trainiert und gespeichert:")
    print(f"  -> {ART_CLASSIFIER_FILE}")
    print(f"  -> {STAERKE_REGRESSOR_FILE}")
    print(f"  -> {LABEL_ENCODER_FILE}")
    print("="*50)

if __name__ == "__main__":
    train()