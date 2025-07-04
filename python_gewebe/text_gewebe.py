########################################
# Datei: ./text_gewebe.py
# Version: ML-Integriert
# Beschreibung: Die Kernklasse des Verstehens-Gewebes, jetzt mit ML-gestützter triadischer Resonanz.
########################################

import re
import random
from collections import Counter
import json
import os
import spacy
import numpy as np
import joblib

# Liste aller bekannten Resonanz-Arten
ALL_RESONANCE_TYPES = [
    'VERSTAERKUNG', 'KONTRAST', 'ERGAENZUNG', 'FORTSETZUNG', 'BEISPIEL',
    'HINTERGRUND', 'PERSPEKTIVE_WECHSEL', 'EMOTIONALE_HARMONIE',
    'EMOTIONALE_SPANNUNG', 'STRUKTURELLE_ANALOGIE', 'NEUTRAL_SCHWACH',
    'KONFLIKT', 'ECHTBEZUG', 'ENTWICKLUNG'
]

class ResonanzVerbindung:
    """Repräsentiert eine gerichtete Resonanzverbindung zwischen zwei Fragmenten."""
    def __init__(self, quelle_index: int, ziel_index: int, art: str, staerke: float, kontext: str):
        self.quelle = quelle_index
        self.ziel = ziel_index
        self.art = art
        self.staerke = staerke
        self.kontext = kontext

    def __repr__(self):
        return f"ResonanzVerbindung(q={self.quelle}, z={self.ziel}, art='{self.art}', staerke={self.staerke:.2f})"

    def to_dict(self):
        return {'quelle': self.quelle, 'ziel': self.ziel, 'art': self.art, 'staerke': self.staerke, 'kontext': self.kontext}

class ResonanzWelle:
    """Repräsentiert eine Welle, die sich durch das Gewebe ausbreitet."""
    def __init__(self, ursprung: int, art: str, staerke: float, pfad: list[int]):
        self.ursprung = ursprung
        self.art = art
        self.staerke = staerke
        self.pfad = pfad

    def __repr__(self):
        return f"ResonanzWelle(ursprung={self.ursprung}, art='{self.art}', staerke={self.staerke:.2f}, pfad={self.pfad})"
        
    def to_dict(self):
        return {'ursprung': self.ursprung, 'art': self.art, 'staerke': self.staerke, 'pfad': self.pfad}

class NeuesTextVerstehen:
  def __init__(self):
    self._fragmente = []
    self._fragment_docs = {}
    self._resonanzen_struktur = {}
    self._gewebe_stimmung = {'harmonisch': 0.0, 'spannungsreich': 0.0, 'offen': 0.0, 'reflexiv': 0.0}
    self._wave_arrival_effects = {}

    # --- NLP und Model Setup ---
    self._load_spacy_model()
    self._load_ml_models()

    # Heuristische Muster bleiben als Fallback und für die 2-Fragment-Analyse erhalten
    self._spuer_muster = {
      'VERSTAERKUNG': {'nlp_criteria': {'similarity': {'min': 0.65, 'weight': 0.5}, 'sentiment_match': {'weight': 0.3}, 'shared_concepts': {'min_count': 1, 'weight': 0.2}}, 'stimmung_effekt': {'harmonisch': 0.1, 'offen': 0.05}},
      'KONTRAST': {'nlp_criteria': {'similarity': {'max': 0.35, 'weight': 0.5}, 'sentiment_contrast': {'weight': 0.5}}, 'stimmung_effekt': {'spannungsreich': 0.15, 'reflexiv': 0.05}},
      'ERGAENZUNG': {'nlp_criteria': {'similarity': {'min': 0.35, 'max': 0.65, 'weight': 0.4}, 'shared_concepts': {'min_count': 2, 'weight': 0.6}}, 'stimmung_effekt': {'harmonisch': 0.1, 'offen': 0.1}},
      'BEISPIEL': {'nlp_criteria': {'similarity': {'min': 0.55, 'weight': 0.6}, 'shared_concepts': {'min_count': 2, 'weight': 0.4}}, 'stimmung_effekt': {'offen': 0.05}},
      'FORTSETZUNG': {'nlp_criteria': {'similarity': {'min': 0.45, 'weight': 0.5}, 'shared_concepts': {'min_count': 2, 'weight': 0.5}}, 'stimmung_effekt': {'harmonisch': 0.05, 'offen': 0.05}},
      'EMOTIONALE_HARMONIE': {'nlp_criteria': {'sentiment_match': {'weight': 0.8}, 'similarity': {'min': 0.45, 'weight': 0.2}}, 'stimmung_effekt': {'harmonisch': 0.2, 'offen': 0.1}},
      'EMOTIONALE_SPANNUNG': {'nlp_criteria': {'sentiment_contrast': {'weight': 0.8}, 'similarity': {'min': 0.35, 'weight': 0.2}}, 'stimmung_effekt': {'spannungsreich': 0.2, 'reflexiv': 0.1}},
      'STRUKTURELLE_ANALOGIE': {'nlp_criteria': {'similarity': {'min': 0.45, 'weight': 0.7}, 'shared_concepts': {'min_count': 3, 'weight': 0.3}}, 'stimmung_effekt': {'reflexiv': 0.15}},
      'NEUTRAL_SCHWACH': {'nlp_criteria': {}, 'stimmung_effekt': {'offen': 0.02}},
      'KONFLIKT': {'nlp_criteria': {}, 'stimmung_effekt': {'spannungsreich': 0.2, 'reflexiv': 0.1}},
      'ECHTBEZUG': {'nlp_criteria': {}, 'stimmung_effekt': {'harmonisch': 0.1, 'reflexiv': 0.1}},
      'ENTWICKLUNG': {'nlp_criteria': {}, 'stimmung_effekt': {'offen': 0.1, 'harmonisch': 0.05}}
    }

  def _load_spacy_model(self):
    try:
        self.nlp = spacy.load("de_core_news_lg")
        print("spaCy model 'de_core_news_lg' loaded successfully.")
    except IOError:
        print("\n[ERROR] spaCy model 'de_core_news_lg' not found. Please run: python -m spacy download de_core_news_lg")
        print("Falling back to a blank model. Semantic features will be limited.")
        self.nlp = spacy.blank("de")

  def _load_ml_models(self):
    """Lädt die trainierten ML-Modelle für die triadische Resonanz."""
    self._art_classifier = None
    self._staerke_regressor = None
    self._label_encoder = None
    self._ml_models_loaded = False
    
    art_model_path = 'triadic_art_classifier.joblib'
    staerke_model_path = 'triadic_staerke_regressor.joblib'
    encoder_path = 'triadic_label_encoder.joblib'
    
    if all(os.path.exists(p) for p in [art_model_path, staerke_model_path, encoder_path]):
        try:
            self._art_classifier = joblib.load(art_model_path)
            self._staerke_regressor = joblib.load(staerke_model_path)
            self._label_encoder = joblib.load(encoder_path)
            self._ml_models_loaded = True
            print("[INFO] Trainierte ML-Modelle für triadische Resonanz erfolgreich geladen.")
        except Exception as e:
            print(f"[WARNUNG] Fehler beim Laden der ML-Modelle: {e}. Verwende heuristische Regeln als Fallback.")
    else:
        print("[INFO] Keine trainierten ML-Modelle gefunden. Verwende heuristische Regeln für triadische Resonanz.")

  # --- NLP Helper Methods ---
  def _analyze_sentiment(self, doc) -> str:
      """Simple sentiment analysis based on a small lexicon and spaCy tokens."""
      positive_words = {"gut", "schön", "freude", "glücklich", "harmonisch", "offen", "friedlich", "sonnig", "verstehen", "klar"}
      negative_words = {"schwer", "spannung", "konflikt", "nicht", "aber", "jedoch", "traurig", "regen", "dunkel", "sorgenvoll", "widerstand", "unerwartet", "problem", "schwierig"}
      score = 0
      for token in doc:
          lemma = token.lemma_.lower()
          if lemma in positive_words:
              score += 1
          elif lemma in negative_words:
              score -= 1
      if score > 0:
          return 'positive'
      elif score < 0:
          return 'negative'
      else:
          return 'neutral'

  def _get_shared_concepts(self, doc1, doc2) -> list[str]:
      """Extracts shared noun, verb, and adjective lemmas between two spaCy docs."""
      concepts1 = {token.lemma_.lower() for token in doc1 if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and not token.is_stop and not token.is_punct}
      concepts2 = {token.lemma_.lower() for token in doc2 if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and not token.is_stop and not token.is_punct}
      return list(concepts1.intersection(concepts2))

  # --- Kernlogik: Spüren ---

  def _spuere_art_und_staerke_der_resonanz(self, teil_a_text, teil_b_text, gesamtes_gewebe_struktur, quelle_index=None, ziel_index=None):
    """Spürt die direkte Resonanz zwischen ZWEI Textteilen."""
    try:
        doc_a = self._fragment_docs.get(quelle_index) if quelle_index is not None and quelle_index in self._fragment_docs else self.nlp(teil_a_text)
        doc_b = self._fragment_docs.get(ziel_index) if ziel_index is not None and ziel_index in self._fragment_docs else self.nlp(teil_b_text)

        if not doc_a.has_vector or not doc_b.has_vector or doc_a.vocab.vectors.size == 0 or doc_b.vocab.vectors.size == 0:
             similarity = 0.0
        else:
             similarity = doc_a.similarity(doc_b)

        sentiment_a = self._analyze_sentiment(doc_a)
        sentiment_b = self._analyze_sentiment(doc_b)
        shared_concepts = self._get_shared_concepts(doc_a, doc_b)
    except Exception as e:
        print(f"Error during NLP processing for resonance: {e}")
        return ResonanzVerbindung(quelle_index or -1, ziel_index or -1, 'NEUTRAL_SCHWACH', 0.05, "NLP Fehler")

    potenzielle_scores = {}
    for art, info in self._spuer_muster.items():
        if art in ['NEUTRAL_SCHWACH', 'KONFLIKT', 'ECHTBEZUG', 'ENTWICKLUNG']: continue
        criteria = info.get('nlp_criteria', {})
        criteria_met_weight_sum = 0.0
        kontext_teile = []

        if 'similarity' in criteria:
            sim_crit = criteria['similarity']
            if similarity >= sim_crit.get('min', -1.0) and similarity <= sim_crit.get('max', 1.0):
                 criteria_met_weight_sum += sim_crit.get('weight', 0)
                 kontext_teile.append(f"Sim({similarity:.2f})")
        if 'sentiment_match' in criteria and sentiment_a != 'neutral' and sentiment_a == sentiment_b:
            criteria_met_weight_sum += criteria['sentiment_match'].get('weight', 0)
            kontext_teile.append(f"SentMatch({sentiment_a})")
        if 'sentiment_contrast' in criteria and sentiment_a != 'neutral' and sentiment_b != 'neutral' and sentiment_a != sentiment_b:
            criteria_met_weight_sum += criteria['sentiment_contrast'].get('weight', 0)
            kontext_teile.append(f"SentContr({sentiment_a} vs {sentiment_b})")
        if 'shared_concepts' in criteria and len(shared_concepts) >= criteria['shared_concepts'].get('min_count', 0):
            criteria_met_weight_sum += criteria['shared_concepts'].get('weight', 0)
            kontext_teile.append(f"Concepts({len(shared_concepts)})")

        if criteria_met_weight_sum > 0:
             potenzielle_scores[art] = {'score': min(1.0, criteria_met_weight_sum), 'kontext_teile': kontext_teile}

    if not potenzielle_scores:
        return None

    beste_art_above_threshold = max(potenzielle_scores, key=lambda k: potenzielle_scores[k]['score'])
    if potenzielle_scores[beste_art_above_threshold]['score'] < 0.25: # Signifikanzschwelle
        return None

    beste_resonanz_art = beste_art_above_threshold
    beste_resonanz_staerke = potenzielle_scores[beste_art_above_threshold]['score']
    beste_resonanz_kontext = ", ".join(potenzielle_scores[beste_art_above_threshold]['kontext_teile'])
    
    return ResonanzVerbindung(quelle_index or -1, ziel_index or -1, beste_resonanz_art, beste_resonanz_staerke, beste_resonanz_kontext)
  
  def _spuere_einfluss_auf_resonanz(self, teil_a_text, teil_b_text, neuer_teil_text, aktuelle_resonanz_ab, gesamtes_gewebe_struktur):
    """Spürt den Einfluss eines dritten Fragments auf die Beziehung zwischen zwei anderen. Priorisiert ML-Modelle."""
    try:
        index_a = self._fragmente.index(teil_a_text)
        index_b = self._fragmente.index(teil_b_text)
        index_neuer = self._fragmente.index(neuer_teil_text)
    except (ValueError, IndexError):
        return aktuelle_resonanz_ab

    # --- Weg 1: ML-gestützte Vorhersage ---
    if self._ml_models_loaded:
        try:
            doc_a = self._fragment_docs.get(index_a)
            doc_b = self._fragment_docs.get(index_b)
            doc_c = self._fragment_docs.get(index_neuer)
            
            if doc_a and doc_b and doc_c and doc_a.has_vector and doc_b.has_vector and doc_c.has_vector:
                feature_vector = np.concatenate([doc_a.vector, doc_b.vector, doc_c.vector]).reshape(1, -1)
                
                art_index = self._art_classifier.predict(feature_vector)[0]
                staerke = self._staerke_regressor.predict(feature_vector)[0]
                
                art = self._label_encoder.inverse_transform([art_index])[0]
                staerke = max(0.0, min(1.0, staerke))
                
                kontext = "ML-Vorhersage (Triade)"
                return ResonanzVerbindung(index_a, index_b, art, staerke, kontext)
        except Exception as e:
            print(f"[WARNUNG] ML-Vorhersage für {index_a}->{index_b} fehlgeschlagen: {e}. Nutze heuristischen Fallback.")
    
    # --- Weg 2: Heuristischer Fallback ---
    # print(f"    Nutze heuristische Regeln für Einfluss auf {index_a}->{index_b}.")
    res_neua = self._spuere_art_und_staerke_der_resonanz(neuer_teil_text, teil_a_text, self._resonanzen_struktur, quelle_index=index_neuer, ziel_index=index_a)
    res_neub = self._spuere_art_und_staerke_der_resonanz(neuer_teil_text, teil_b_text, self._resonanzen_struktur, quelle_index=index_neuer, ziel_index=index_b)
    
    neue_resonanz_ab = aktuelle_resonanz_ab
    
    # Regel: "Gemeinsamer Nenner"
    if (res_neua and res_neua.art in ['VERSTAERKUNG', 'ERGAENZUNG'] and res_neua.staerke > 0.6) and \
       (res_neub and res_neub.art in ['VERSTAERKUNG', 'ERGAENZUNG'] and res_neub.staerke > 0.6):
        neue_staerke = min(1.0, (aktuelle_resonanz_ab.staerke if aktuelle_resonanz_ab else 0) + 0.2)
        neuer_kontext = (aktuelle_resonanz_ab.kontext + ", " if aktuelle_resonanz_ab else "") + f"durch '{neuer_teil_text[:15]}...' gefestigt"
        neue_resonanz_ab = ResonanzVerbindung(index_a, index_b, 'ERGAENZUNG', neue_staerke, neuer_kontext)
        return neue_resonanz_ab

    # Regel: "Störenfried"
    if (res_neua and res_neua.art == 'KONTRAST' and res_neua.staerke > 0.7) and \
       (aktuelle_resonanz_ab and aktuelle_resonanz_ab.art == 'VERSTAERKUNG'):
        neue_staerke = max(0.0, aktuelle_resonanz_ab.staerke - res_neua.staerke * 0.5)
        if neue_staerke < 0.1: return None # Löschen
        neuer_kontext = aktuelle_resonanz_ab.kontext + f", durch Kontrast von '{neuer_teil_text[:15]}...' destabilisiert"
        neue_resonanz_ab = ResonanzVerbindung(index_a, index_b, aktuelle_resonanz_ab.art, neue_staerke, neuer_kontext)
        return neue_resonanz_ab

    return aktuelle_resonanz_ab

  # --- Gewebe-Management ---
  
  def fuege_ein(self, text: str):
    """Fügt ein neues Textfragment zum Gewebe hinzu und aktualisiert die Resonanzstruktur."""
    print(f"\nFüge Fragment '{text[:50]}...' hinzu...")
    neuer_index = len(self._fragmente)
    self._fragmente.append(text)
    try:
        self._fragment_docs[neuer_index] = self.nlp(text)
        print(f"  SpaCy Doc gecacht für Fragment {neuer_index}.")
    except Exception as e:
        print(f"Error caching spaCy doc: {e}")
        self._fragment_docs[neuer_index] = self.nlp("")

    self._resonanzen_struktur[neuer_index] = {}
    
    # 1. Direkte (dyadische) Resonanzen zum neuen Fragment spüren
    for i in range(neuer_index):
        if self._fragmente[i] is None: continue
        res_neu_i = self._spuere_art_und_staerke_der_resonanz(text, self._fragmente[i], self._resonanzen_struktur, neuer_index, i)
        if res_neu_i: self._resonanzen_struktur[neuer_index][i] = res_neu_i
        res_i_neu = self._spuere_art_und_staerke_der_resonanz(self._fragmente[i], text, self._resonanzen_struktur, i, neuer_index)
        if res_i_neu:
            if i not in self._resonanzen_struktur: self._resonanzen_struktur[i] = {}
            self._resonanzen_struktur[i][neuer_index] = res_i_neu

    # 2. Indirekten (triadischen) Einfluss auf alle bestehenden Paare spüren
    aktive_indices = [i for i in range(neuer_index) if self._fragmente[i] is not None]
    if len(aktive_indices) > 1:
        print(f"  Spüre Einfluss von Fragment {neuer_index} auf bestehende Resonanzen...")
    for i in aktive_indices:
        for j in aktive_indices:
            if i == j: continue
            aktuelle_resonanz = self._resonanzen_struktur.get(i, {}).get(j)
            neue_resonanz = self._spuere_einfluss_auf_resonanz(self._fragmente[i], self._fragmente[j], text, aktuelle_resonanz, self._resonanzen_struktur)
            
            if neue_resonanz and neue_resonanz.staerke >= 0.1:
                if i not in self._resonanzen_struktur: self._resonanzen_struktur[i] = {}
                self._resonanzen_struktur[i][j] = neue_resonanz
            elif aktuelle_resonanz is not None:
                del self._resonanzen_struktur[i][j]

    print("  Gewebe aktualisiert.")

  def loesche_fragment(self, index: int):
    """Markiert ein Fragment als gelöscht (Tombstone) und entfernt zugehörige Resonanzen."""
    if not (0 <= index < len(self._fragmente) and self._fragmente[index] is not None):
        print(f"Fehler: Fragment {index} kann nicht gelöscht werden (existiert nicht oder bereits gelöscht).")
        return

    print(f"\nLösche Fragment {index} logisch...")
    self._fragmente[index] = None
    if index in self._fragment_docs: del self._fragment_docs[index]
    if index in self._resonanzen_struktur: del self._resonanzen_struktur[index]
    
    for quelle_index in list(self._resonanzen_struktur.keys()):
        if index in self._resonanzen_struktur[quelle_index]:
            del self._resonanzen_struktur[quelle_index][index]
    
    if index in self._wave_arrival_effects: del self._wave_arrival_effects[index]
    print(f"  Fragment {index} als gelöscht markiert.")

  def verschmelze_fragmente(self, index1: int, index2: int):
      """Verschmilzt zwei Fragmente zu einem neuen und löscht die alten."""
      if not (0 <= index1 < len(self._fragmente) and self._fragmente[index1] is not None and \
              0 <= index2 < len(self._fragmente) and self._fragmente[index2] is not None and index1 != index2):
          print("Fehler: Ungültige oder inaktive Indices für Verschmelzung.")
          return
      
      print(f"\nVerschmelze Fragmente {index1} und {index2}...")
      neues_fragment_text = f"{self._fragmente[index1].strip()}. {self._fragmente[index2].strip()}"
      self.loesche_fragment(index1)
      self.loesche_fragment(index2)
      self.fuege_ein(neues_fragment_text)

  # --- Analyse und Reaktion ---

  def spuere_reaktion_des_gewebes(self, impuls: str) -> dict:
      """Simuliert die Reaktion des Gewebes auf einen externen Impuls, inkl. Wellen."""
      initial_waves = []
      for i, fragment_text in enumerate(self._fragmente):
          if fragment_text is None: continue
          res = self._spuere_art_und_staerke_der_resonanz(impuls, fragment_text, self._resonanzen_struktur, -1, i)
          if res and res.staerke > 0.1:
              initial_waves.append(ResonanzWelle(-1, res.art, res.staerke, [-1, i]))

      self._wave_arrival_effects = {}
      waves_to_propagate = initial_waves[:]
      
      for step in range(3): # Max 3 Hops
          if not waves_to_propagate: break
          next_waves = []
          for wave in waves_to_propagate:
              current_node_idx = wave.pfad[-1]
              if current_node_idx not in self._wave_arrival_effects: self._wave_arrival_effects[current_node_idx] = []
              self._wave_arrival_effects[current_node_idx].append(wave)

              outgoing = self._resonanzen_struktur.get(current_node_idx, {})
              for target_idx, conn in outgoing.items():
                  if self._fragmente[target_idx] is None: continue
                  if len(wave.pfad) > 1 and target_idx == wave.pfad[-2]: continue # No immediate bounce-back

                  new_staerke = wave.staerke * conn.staerke * 0.7 # Damping
                  if new_staerke > 0.05:
                      new_wave = ResonanzWelle(wave.ursprung, conn.art, new_staerke, wave.pfad + [target_idx])
                      next_waves.append(new_wave)
          waves_to_propagate = next_waves

      zustand_daten = self._analysiere_gewebe_zustand(self._resonanzen_struktur, self._wave_arrival_effects, return_data=True)
      return {
          'impuls': impuls,
          'report': self._analysiere_gewebe_zustand(self._resonanzen_struktur, self._wave_arrival_effects)
      }

  def finde_fragmente_mit_resonanz(self, impuls: str, gewuenschte_arten: list[str], mindest_staerke: float = 0.2) -> list[str]:
      """Findet Fragmente, die auf einen Impuls mit bestimmten Resonanz-Arten reagieren."""
      self.spuere_reaktion_des_gewebes(impuls)
      gefundene_indices = set()
      for fragment_index, waves in self._wave_arrival_effects.items():
          for wave in waves:
              if wave.art in gewuenschte_arten and wave.staerke >= mindest_staerke:
                  gefundene_indices.add(fragment_index)
      
      return [self._fragmente[i] for i in sorted(list(gefundene_indices))]

  def antworte_aus_resonanz(self, impuls: str, ziel_art: str = "VERSTAERKUNG") -> str:
      """Generiert ein neues Fragment, das aus den Resonanzen eines Impulses entsteht."""
      reaktion = self.spuere_reaktion_des_gewebes(impuls)
      relevante_indices = set()
      for fragment_index, waves in self._wave_arrival_effects.items():
          for wave in waves:
              if wave.art == ziel_art and wave.staerke >= 0.3:
                  relevante_indices.add(fragment_index)
      
      if not relevante_indices:
          return "Aus dieser Resonanz entsteht noch keine klare Formulierung."
      
      combined_text = " ".join([self._fragmente[idx] for idx in relevante_indices])
      combined_doc = self.nlp(combined_text)
      concepts = {t.lemma_ for t in combined_doc if t.pos_ in ['NOUN', 'VERB'] and not t.is_stop}
      kern = ", ".join(list(concepts)[:3])
      
      template = f"Die Resonanz um '{kern}' deutet auf eine {ziel_art.lower()} hin."
      synthetisches_fragment = template
      self.fuege_ein(synthetisches_fragment)
      return synthetisches_fragment

  def _analysiere_gewebe_zustand(self, resonanzen_struktur, wave_arrival_effects, return_data=False):
      """Analysiert und berichtet den aktuellen Zustand des Gewebes."""
      active_frags = [f for f in self._fragmente if f is not None]
      all_active_res = [res for res_list in resonanzen_struktur.values() for res in res_list.values() if self._fragmente[res.quelle] and self._fragmente[res.ziel]]
      
      res_counts = Counter(res.art for res in all_active_res)
      dominant_res = res_counts.most_common(1)[0][0] if res_counts else "Keine"

      # Stimmung berechnen
      self._gewebe_stimmung = {'harmonisch': 0.0, 'spannungsreich': 0.0, 'offen': 0.0, 'reflexiv': 0.0}
      for res in all_active_res:
          effekt = self._spuer_muster.get(res.art, {}).get('stimmung_effekt', {})
          for key, val in effekt.items(): self._gewebe_stimmung[key] += val * res.staerke
      
      if return_data:
          return {'num_active_fragments': len(active_frags), 'dominant_resonance': dominant_res}

      report = [
          "\n--- Gewebe Zustandsbericht ---",
          f"Fragmente: {len(active_frags)} aktiv / {len(self._fragmente)} total",
          f"Resonanzen (aktiv): {len(all_active_res)}",
          f"Dominante Resonanz: {dominant_res}",
          f"Stimmung: " + ", ".join([f"{k}:{v:.2f}" for k, v in self._gewebe_stimmung.items()]),
          "---"
      ]
      return "\n".join(report)

  def fuehle_zustand_des_gewebes(self):
      """Gibt einen Bericht über den aktuellen Zustand des Gewebes aus."""
      print(self._analysiere_gewebe_zustand(self._resonanzen_struktur, self._wave_arrival_effects))