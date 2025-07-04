"use client";

import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator"; // Neu importieren

export default function Home() {
  // Zustände für die Eingabefelder
  const [inputA, setInputA] = useState('Das Gefühl, das Muster im Ganzen zu erfassen, ist schwer.');
  const [inputB, setInputB] = useState('Dieser Versuch ist notwendig, um das Gewebe zu verstehen.');
  const [inputC, setInputC] = useState('Das Zählen ist aber nicht das Verstehen selbst.');
  
  // Zustände für den Analyse-Workflow
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [editableResult, setEditableResult] = useState<any>(null);

  // Zustände für den Generator-Workflow
  const [topic, setTopic] = useState('Verstehen und Komplexität');
  const [loadingGeneration, setLoadingGeneration] = useState(false);

  useEffect(() => {
    setEditableResult(analysisResult);
    setIsSaved(false);
  }, [analysisResult]);

  // Funktion zum Generieren von Triaden
  const handleGenerate = async () => {
    setLoadingGeneration(true);
    setAnalysisResult(null); // Alte Analyse zurücksetzen
    setEditableResult(null);

    const response = await fetch('/api/gemini-generate-triads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });

    if (response.ok) {
        const json = await response.json();
        setInputA(json.fragmentA);
        setInputB(json.fragmentB);
        setInputC(json.fragmentC);
    } else {
        alert("Generierung fehlgeschlagen. Prüfen Sie die Konsole.");
    }
    setLoadingGeneration(false);
  };

  // Funktion zum Analysieren (unverändert)
  const handleAnalyze = async () => {
    setLoadingAnalysis(true);
    setAnalysisResult(null);
    setEditableResult(null);

    const response = await fetch('/api/gemini-triadic-analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ inputA, inputB, inputC })
    });

    if (response.ok) {
        const json = await response.json();
        setAnalysisResult(json);
    } else {
        alert("Analyse fehlgeschlagen. Prüfen Sie die Konsole.");
    }
    setLoadingAnalysis(false);
  };

  // Funktion zum Speichern (unverändert)
  const handleSave = async () => {
    if (!editableResult) return;
    const trainingSample = {
      fragment_a: inputA,
      fragment_b: inputB,
      fragment_c: inputC,
      label: editableResult
    };

    const response = await fetch('/api/save-training-sample', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trainingSample)
    });

    if (response.ok) {
      setIsSaved(true);
      alert('Trainingsbeispiel erfolgreich im Python-Verzeichnis gespeichert!');
    } else {
      alert('Fehler beim Speichern.');
    }
  };

  const handleFieldChange = (field: string, value: string | number) => {
    if (!editableResult) return;
    setEditableResult({ ...editableResult, [field]: value });
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50">
      <div className="p-6 space-y-6 max-w-2xl w-full bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Triadische Resonanz-Annotation</h1>
        
        {/* --- Generator Sektion --- */}
        <Card className="bg-gray-50">
          <CardHeader>
            <CardTitle>1. Datensätze generieren (Optional)</CardTitle>
            <p className="text-sm text-gray-600">Lassen Sie Gemini kreative Beispiele erstellen.</p>
          </CardHeader>
          <CardContent className="space-y-2">
            <Label htmlFor="topic">Thema für die Generierung</Label>
            <Input id="topic" placeholder="z.B. Kreativität, Verlust, Technologie..." value={topic} onChange={e => setTopic(e.target.value)} />
            <Button onClick={handleGenerate} disabled={loadingGeneration} className="w-full">
              {loadingGeneration ? 'Generiere...' : 'Neue Fragmente generieren'}
            </Button>
          </CardContent>
        </Card>

        {/* --- Annotations Sektion --- */}
        <Card>
          <CardHeader>
            <CardTitle>2. Fragmente annotieren</CardTitle>
            <p className="text-sm text-gray-600">Geben Sie Fragmente manuell ein oder verwenden Sie die generierten.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
                <Label htmlFor="fragA">Fragment A</Label>
                <Textarea id="fragA" value={inputA} onChange={e => setInputA(e.target.value)} rows={3} />
            </div>
            <div className="space-y-2">
                <Label htmlFor="fragB">Fragment B</Label>
                <Textarea id="fragB" value={inputB} onChange={e => setInputB(e.target.value)} rows={3} />
            </div>
            <div className="space-y-2">
                <Label htmlFor="fragC">Fragment C (Einfluss)</Label>
                <Textarea id="fragC" value={inputC} onChange={e => setInputC(e.target.value)} rows={3} />
            </div>
            <Button onClick={handleAnalyze} disabled={loadingAnalysis} className="w-full">
                {loadingAnalysis ? 'Analysiere...' : 'Analyse mit Gemini starten'}
            </Button>
          </CardContent>
        </Card>

        {/* --- Ergebnis- und Speichersektion --- */}
        {editableResult && (
            <Card>
              <CardHeader><CardTitle>3. Ergebnis prüfen und speichern</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="einfluss">Einfluss-Beschreibung</Label>
                    <Input id="einfluss" value={editableResult.einfluss_beschreibung} onChange={e => handleFieldChange('einfluss_beschreibung', e.target.value)} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                        <Label htmlFor="resArt">Ergebnis Art</Label>
                        <Input id="resArt" value={editableResult.ergebnis_art} onChange={e => handleFieldChange('ergebnis_art', e.target.value)} />
                    </div>
                    <div>
                        <Label htmlFor="resStaerke">Ergebnis Stärke</Label>
                        <Input id="resStaerke" type="number" step="0.01" value={editableResult.ergebnis_staerke} onChange={e => handleFieldChange('ergebnis_staerke', parseFloat(e.target.value))} />
                    </div>
                  </div>
                  <Button onClick={handleSave} disabled={isSaved} variant="outline" className="w-full">
                    {isSaved ? 'Gespeichert!' : 'Annotation als Trainingsdaten speichern'}
                  </Button>
              </CardContent>
            </Card>
        )}
      </div>
    </main>
  );
}