import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

// Der Pfad zeigt auf das Python-Verzeichnis, um die Daten direkt dort zu speichern
const dataFilePath = path.join(process.cwd(), '..', 'python_gewebe', 'training_data.jsonl');

export async function POST(req: NextRequest) {
  try {
    const sample = await req.json();

    if (!sample.fragment_a || !sample.fragment_b || !sample.fragment_c || !sample.label) {
      return NextResponse.json({ error: "Ungültige Daten" }, { status: 400 });
    }

    const dataLine = JSON.stringify(sample) + '\n';

    await fs.appendFile(dataFilePath, dataLine, 'utf-8');

    return NextResponse.json({ message: "Erfolgreich gespeichert" }, { status: 200 });

  } catch (error) {
    console.error("Fehler beim Speichern der Trainingsdaten:", error);
    return NextResponse.json({ error: "Speichern fehlgeschlagen" }, { status: 500 });
  }
}