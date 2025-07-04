# Das Gewebe des Verstehens: Ein ML-gestütztes Resonanzmodell

Dieses Projekt ist eine Implementierung eines neuartigen KI-Systems zur Analyse von Textverständnis, basierend auf dem Konzept eines dynamischen "Gewebes" aus Textfragmenten. Es modelliert die Beziehungen (Resonanzen) zwischen Texten und simuliert, wie neue Informationen das gesamte System beeinflussen.

Ein zentrales Merkmal dieses Projekts ist die Fähigkeit, seine Kernlogik – die "Spürlogik" – durch maschinelles Lernen kontinuierlich zu verbessern. Hierfür wird ein Web-basiertes Annotationstool verwendet, um mit Hilfe von Google Gemini Trainingsdaten zu generieren, mit denen dann kompakte, effiziente ML-Modelle trainiert werden.

Das Projekt ist in zwei Hauptteile gegliedert:

1.  **`python_gewebe`**: Die Kernimplementierung des Resonanz-Gewebes in Python.
2.  **`nextjs_annotator`**: Ein Web-Frontend (Next.js), um Trainingsdaten für die triadische Resonanzanalyse zu erstellen.

## Features

-   **Dynamisches Graphenmodell**: Textfragmente werden als Knoten in einem Graphen gespeichert, deren Kanten "Resonanzen" darstellen.
-   **ML-gestützte Spürlogik**: Nutzt trainierte Modelle (Random Forest), um den Einfluss eines dritten Fragments auf die Beziehung zweier anderer zu bewerten (triadische Resonanz).
-   **Heuristischer Fallback**: Wenn keine ML-Modelle trainiert wurden, greift das System auf ein robustes, regelbasiertes System zurück.
-   **Resonanz-Wellen**: Simuliert die Ausbreitung von "Impulsen" durch das Gewebe, um indirekte Einflüsse und Reaktionen zu modellieren.
-   **Generative Fähigkeiten**: Kann aus dem aktuellen Zustand des Gewebes heraus neue, thematisch passende Textfragmente erzeugen.
-   **Web-basiertes Annotationstool**: Ein einfach zu bedienendes UI, das Google Gemini nutzt, um schnell hochwertige Trainingsdaten zu generieren ("Human-in-the-Loop").

## Projektstruktur

```
gewebe-ml-projekt/
├── python_gewebe/              # Kernlogik in Python
│   ├── main.py                 # Haupt-Skript zur Demonstration
│   ├── text_gewebe.py          # Die Kernklasse des Gewebes
│   ├── model_trainer.py        # Skript zum Trainieren der ML-Modelle
│   ├── requirements.txt        # Python-Abhängigkeiten
│   └── training_data.jsonl     # (wird durch Annotator erstellt)
│
├── nextjs_annotator/           # Web-basiertes Annotationstool
│   ├── app/                    # Next.js App Router
│   ├── package.json
│   └── .env.local              # (muss erstellt werden)
│
└── README.md                   # Diese Datei
```

## Setup und Installation

Führen Sie die folgenden Schritte aus, um das Projekt vollständig einzurichten.

### Teil 1: Python-Backend (`python_gewebe`)

1.  **Navigieren Sie in das Python-Verzeichnis:**
    ```bash
    cd python_gewebe
    ```

2.  **Erstellen Sie eine virtuelle Umgebung (empfohlen):**
    ```bash
    python -m venv venv
    ```

3.  **Aktivieren Sie die virtuelle Umgebung:**
    -   Auf macOS/Linux: `source venv/bin/activate`
    -   Auf Windows: `venv\Scripts\activate`

4.  **Installieren Sie die Abhängigkeiten:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Laden Sie das spaCy-Sprachmodell herunter:**
    ```bash
    python -m spacy download de_core_news_lg
    ```

### Teil 2: Next.js-Frontend (`nextjs_annotator`)

1.  **Navigieren Sie in das Next.js-Verzeichnis:**
    ```bash
    cd nextjs_annotator
    ```

2.  **Erstellen Sie eine `.env.local`-Datei:**
    Erstellen Sie eine Datei mit dem Namen `.env.local` und fügen Sie Ihren Google Gemini API-Schlüssel hinzu:
    ```
    GEMINI_API_KEY="IHR_GOOGLE_AI_STUDIO_API_KEY"
    ```
    Ersetzen Sie `IHR_GOOGLE_AI_STUDIO_API_KEY` durch Ihren tatsächlichen Schlüssel.

3.  **Installieren Sie die Node.js-Abhängigkeiten:**
    ```bash
    npm install
    ```

## Workflow: Vom Annotieren zum trainierten Modell

Der gesamte Prozess besteht aus drei Schritten: Annotieren, Trainieren und Anwenden.

### Schritt 1: Daten annotieren

In diesem Schritt generieren Sie die Trainingsdaten für die "Spürlogik".

1.  **Starten Sie den Annotator:**
    Navigieren Sie in das `nextjs_annotator`-Verzeichnis und führen Sie folgenden Befehl aus:
    ```bash
    npm run dev
    ```

2.  **Öffnen Sie das UI im Browser:**
    Besuchen Sie `http://localhost:3000`.

3.  **Erstellen Sie Trainingsdaten:**
    -   Geben Sie drei Textfragmente (A, B und C) in die Textfelder ein.
    -   Klicken Sie auf **"Analyse mit Gemini starten"**. Das System bittet Gemini, den Einfluss von C auf die Beziehung zwischen A und B zu bewerten.
    -   Überprüfen und korrigieren Sie die von Gemini vorgeschlagene Klassifikation und Stärke.
    -   Klicken Sie auf **"Annotation als Trainingsdaten speichern"**.

Jede Speicherung fügt eine neue Zeile zur Datei `python_gewebe/training_data.jsonl` hinzu. **Sammeln Sie mindestens 10-20 Beispiele, idealerweise 50+, um ein robustes Modell zu erhalten.**

### Schritt 2: Modelle trainieren

Nachdem Sie genügend Daten gesammelt haben, trainieren Sie die Machine-Learning-Modelle.

1.  **Navigieren Sie in das Python-Verzeichnis** (`python_gewebe`).
2.  **Stellen Sie sicher, dass Ihre virtuelle Umgebung aktiviert ist.**
3.  **Führen Sie das Trainingsskript aus:**
    ```bash
    python model_trainer.py
    ```
    Das Skript liest `training_data.jsonl`, trainiert zwei Modelle (einen Klassifikator für die Art und einen Regressor für die Stärke der Resonanz) und speichert sie als `.joblib`-Dateien im selben Verzeichnis.

### Schritt 3: Das trainierte Gewebe anwenden

Jetzt können Sie die Kernlogik mit der neu gelernten "Spürlogik" ausführen.

1.  **Führen Sie das Haupt-Skript aus:**
    Bleiben Sie im `python_gewebe`-Verzeichnis und führen Sie aus:
    ```bash
    python main.py
    ```
    Beim Starten wird die `NeuesTextVerstehen`-Klasse automatisch die trainierten `.joblib`-Modelle laden. Wenn sie vorhanden sind, wird die Analyse der triadischen Resonanz durch die ML-Modelle durchgeführt. Andernfalls greift das System nahtlos auf die eingebauten heuristischen Regeln zurück.

Das Skript demonstriert das Hinzufügen von Fragmenten, die Analyse von Impulsen, die Suche nach Resonanzen und generative Fähigkeiten des Gewebes.