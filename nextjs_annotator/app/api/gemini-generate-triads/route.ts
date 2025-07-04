import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextRequest, NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export async function POST(req: NextRequest) {
  try {
    const { topic } = await req.json();

    if (!topic) {
        return NextResponse.json({ error: "Thema ist erforderlich" }, { status: 400 });
    }

    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `
      Du bist ein kreativer Autor und Experte für nuancierte Textbeziehungen.
      Deine Aufgabe ist es, drei kurze, thematisch zusammenhängende Textfragmente (A, B und C) zu generieren, die eine interessante triadische Resonanz bilden.
      Das Thema ist: "${topic}".

      - Fragment A und B sollten eine grundlegende Beziehung haben (z.B. eine Aussage und eine Ergänzung, oder ein leichter Kontrast).
      - Fragment C sollte diese Beziehung auf eine interessante Weise verändern, z.B. durch eine neue Perspektive, einen Widerspruch, eine Verstärkung oder eine Brückenbildung.
      - Die Sätze sollten kurz und prägnant sein.

      Gib deine Antwort als striktes JSON-Objekt zurück, ohne Markdown-Formatierung. Das JSON-Objekt MUSS die folgenden drei Schlüssel enthalten:
      - "fragmentA": Der Text für Fragment A.
      - "fragmentB": Der Text für Fragment B.
      - "fragmentC": Der Text für Fragment C.

      Beispiel für das Thema "Verlust und Erinnerung":
      {
        "fragmentA": "Die Stille in seinem alten Zimmer ist ohrenbetäubend.",
        "fragmentB": "Jedes zurückgelassene Objekt scheint eine Geschichte zu flüstern.",
        "fragmentC": "Doch erst das vergilbte Foto auf dem Nachttisch macht den Verlust greifbar."
      }
    `;

    const result = await model.generateContent(prompt);
    const responseText = result.response.text();
    const data = JSON.parse(responseText);

    return NextResponse.json(data);
  } catch (error)
  {
    console.error("Fehler bei der Gemini-API-Anfrage (Generierung):", error);
    return NextResponse.json({ error: "Generierung fehlgeschlagen" }, { status: 500 });
  }
}