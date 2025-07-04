import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextRequest, NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

const ALL_RESONANCE_TYPES = [
    'VERSTAERKUNG', 'KONTRAST', 'ERGAENZUNG', 'FORTSETZUNG', 'BEISPIEL',
    'HINTERGRUND', 'PERSPEKTIVE_WECHSEL', 'EMOTIONALE_HARMONIE',
    'EMOTIONALE_SPANNUNG', 'STRUKTURELLE_ANALOGIE', 'NEUTRAL_SCHWACH',
    'KONFLIKT', 'ECHTBEZUG', 'ENTWICKLUNG'
];

export async function POST(req: NextRequest) {
  try {
    const { inputA, inputB, inputC } = await req.json();

    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `
      Du bist ein Experte für Textanalyse und das Konzept der "Resonanz" zwischen Textfragmenten.
      Analysiere, wie Fragment C die semantische und emotionale Beziehung zwischen Fragment A und B verändert.

      Fragment A: "${inputA}"
      Fragment B: "${inputB}"
      Fragment C (der Einfluss): "${inputC}"

      Gib deine Analyse als striktes JSON-Objekt zurück, ohne Markdown-Formatierung. Das JSON-Objekt MUSS die folgenden Schlüssel enthalten:
      - "einfluss_beschreibung": Eine kurze, prägnante Beschreibung in einem Satz, wie C die Beziehung verändert (z.B. "C bildet eine Brücke", "C stellt einen Widerspruch her").
      - "ergebnis_art": Die wahrscheinlichste Resonanz-Art zwischen A und B NACH dem Einfluss von C. Wähle eine aus: ${ALL_RESONANCE_TYPES.join(', ')}.
      - "ergebnis_staerke": Eine Fließkommazahl zwischen 0.0 und 1.0 für die Stärke der neuen Resonanz.

      Beispiel-Ausgabe:
      {
        "einfluss_beschreibung": "C verstärkt das gemeinsame Thema 'Versuch' und schafft eine logische Fortsetzung.",
        "ergebnis_art": "FORTSETZUNG",
        "ergebnis_staerke": 0.75
      }
    `;

    const result = await model.generateContent(prompt);
    const responseText = result.response.text();
    const data = JSON.parse(responseText);

    return NextResponse.json(data);
  } catch (error) {
    console.error("Fehler bei der Gemini-API-Anfrage:", error);
    return NextResponse.json({ error: "Analyse fehlgeschlagen" }, { status: 500 });
  }
}