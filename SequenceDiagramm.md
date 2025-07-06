![PlantUML Diagramm](https://www.plantuml.com/plantuml/svg/dLRDRjD04BxxAKOze4HAsdkaefP0IghqHqbAZz7MdeGjzgxnhblICqSaVWM22nn0l08d7eONW4TWlFxRpKzRE5aUppSpEzytizvHcYKwZK8lfYVtUSo4XXE52J056ty-l_vgtZQSxxj2ICsqJ4xwXTlxRxz_lApjSD9t4OVuJ9-htUFI_yKhOzeyLq16rtSF8ovuuVZk0-n9EGknCBkkuuIHJSpkCyqAmDlde0lh920pfP0YT647Ci3GO8jp_lhqCQi_okmJdN_OZESkgdlGE-pA18j4txyO2sGcrt5VdeNyp2HHXVERdx1vRinvSkKYHZ7hpkrAb34C-5d24Yh3szukcykbW5EPF9c6yXAsjpt3LVkkpKa7-Y9EzTQ3W6SjuYo0ncuBxhMWsuGxCCIdAQgCHHREhz1ZlkONJACXkdwp0desuPIhOhC3nqUZCMpD33jjdUNYVflbaUkiTTGAwjMIe8WvkPsofgBg8H9tJFWKwJYHKQojG3d2AyJITgioOHHNi3ywEeJ6U1vZ2qOwGJ7JZvjUW8jXh68MU-d4ig7rKIoZtRNLt0pnWkDbJauLksPbn2xm_qXGX6oNscyh5iLXJK4B1kmCmvkPi4UA3X_7A09pz064D1OrtdRqd45S86EK-ZugPNV9mLxJ-wmPD61YofF8IF-V-c-PZRIpAIephvmXUoyGKQbOsWZhXiL6UivwMMhf44dPArRKRJlh5bcTnpYlQ_5YHMRVT60WgHJp3He1JdpQP1E1bseIph95GJEN4GTZQdHTdS5w-SPQhgU7JAUq8n-XJoGufEV0nL9M70SE1iMMXCQGYK16qAFI58t_8jfUjOLSIcIvRwSyH6NftePupgfUFisr-dC2kOLHe4mV5Zr3Z6MYRRWZcLLIfTaBkRz-uvVtKQ5K2aG2XKPVSCrPo6cBPXxDTP8juLvrhwqM1f-2G0mmQAxNG5rARZFGPUxjJ2vpkreZxNVGqigjRajQdRuadtv1Q0_0LAOYQAubRSN9RSr38rSnlp8atEhyD-hVpbd3odlFkl6g8TXwY6d25Vqia8nNmqSyIiCinoa9LhMWnsbfzn8sYr1eUjz34bdsdUB7KYYw3IasdywpIp7riugjo9LwoJiDjThAnUiSfbBFed9twBwW_yc_)


```PlanUML
@startuml
participant User as "👤 User"
participant AnnotatorUI as "🖥️ Annotator UI"
participant NextjsAPI as "🌐 Next.js API"
participant Gemini as "🔗 Google Gemini"
participant TrainingData as "📄 training_data.jsonl"
participant ModelTrainer as "⚙️ model_trainer.py"
participant CMFNCore as "🧠 CMFN Core"
participant JoblibModels as "💾 .joblib Models"
participant SpaCy as "⚙️ spaCy Library"

== Annotation Workflow ==
User -> AnnotatorUI: Input/Edit Triad (A, B, C) & Request Analyze
activate User
activate AnnotatorUI
AnnotatorUI -> NextjsAPI: POST /gemini-triadic-analyze (A, B, C)
activate NextjsAPI
NextjsAPI -> Gemini: Analyze Triad Resonance (Prompt)
activate Gemini
Gemini --> NextjsAPI: Analysis JSON (Type, Strength)
deactivate Gemini
NextjsAPI --> AnnotatorUI: Analysis JSON
deactivate NextjsAPI
deactivate AnnotatorUI

User -> AnnotatorUI: Review/Edit Analysis & Request Save
activate AnnotatorUI
AnnotatorUI -> NextjsAPI: POST /save-training-sample (A, B, C, Label)
activate NextjsAPI
NextjsAPI -> TrainingData: Append JSONL line
activate TrainingData
TrainingData --> NextjsAPI: Success
deactivate TrainingData
NextjsAPI --> AnnotatorUI: Save Confirmation
deactivate NextjsAPI
deactivate AnnotatorUI
deactivate User

== Training Workflow ==
User -> ModelTrainer: Run model_trainer.py
activate User
activate ModelTrainer
ModelTrainer -> TrainingData: Read training_data.jsonl
activate TrainingData
TrainingData --> ModelTrainer: Training Data
deactivate TrainingData
ModelTrainer -> SpaCy: Load Model (de_core_news_lg) & Process Text
activate SpaCy
SpaCy --> ModelTrainer: Feature Vectors
deactivate SpaCy
ModelTrainer -> ModelTrainer: Train ML Models (Random Forest)
ModelTrainer -> JoblibModels: Save Models (.joblib files)
activate JoblibModels
JoblibModels --> ModelTrainer: Save Confirmation
deactivate JoblibModels
ModelTrainer --> User: Training Report
deactivate ModelTrainer
deactivate User

== Application Workflow ==
User -> CMFNCore: Run main.py (Initialize CMFN)
activate User
activate CMFNCore
CMFNCore -> SpaCy: Load Model (if needed)
activate SpaCy
SpaCy --> CMFNCore: SpaCy Model
deactivate SpaCy
CMFNCore -> JoblibModels: Attempt to Load Models
activate JoblibModels
JoblibModels --> CMFNCore: Models (or not found)
deactivate JoblibModels
CMFNCore -> SpaCy: Process Text (Vectorization)
activate SpaCy
SpaCy --> CMFNCore: Feature Vectors
deactivate SpaCy
CMFNCore -> CMFNCore: Analyze Resonance (ML Models/Heuristics)
CMFNCore -> CMFNCore: Simulate Waves, Find Fragments, Generate Response, Modify Structure
CMFNCore --> User: Results/Reports
deactivate CMFNCore
deactivate User
@enduml

```
