# Workspace Architecture & Multi-Project Layout

## 1. Multi-Project Directory Structure

This repository is designed as a structured hub for managing multiple LTspice circuit design and simulation projects, backed by Python automation with `uv` and global LTspice search paths:

```text
LTspice_Workspace/
│
├── _Shared_Lib/                       # BIBLIOTHÈQUE CENTRALE (Commune à tous les projets)
│   ├── sym/                           # Symboles composants constructeurs (Type: Cell)
│   │   ├── OpAmps/
│   │   │   └── OPA1656.asy
│   │   └── MOSFETs/
│   │       └── IRFP240.asy
│   ├── models/                        # Modèles texte SPICE (.lib, .sub, .mod)
│   │   ├── OPA1656.lib
│   │   ├── IRFP240.sub
│   │   └── mes_diodes.mod
│   └── common_blocks/                 # Sous-schémas réutilisables (Type: Block)
│       ├── alim_symetrique_labo.asc   # Schéma interne du bloc
│       └── alim_symetrique_labo.asy   # Symbole du bloc (même nom exact)
│
├── _Build_Temp/                       # Fichiers volumineux générés (.raw, .log, .fft) [gitignored]
│
├── Projets/                           # TOUS VOS PROJETS INDÉPENDANTS
│   ├── Ampli_Audio/
│   │   ├── README.md                  # Spécifications et cas de tests
│   │   ├── docs/                      # Notes d'application, calculs préliminaires
│   │   └── sim/                       # Schémas de simulation
│   │       ├── main_amp.asc           # Schéma principal
│   │       ├── main_amp.plt           # Tracés de courbes associés
│   │       ├── blocks/                # Blocs hiérarchiques propres à CE projet (*.asc + *.asy)
│   │       └── stimuli/               # Fichiers sources (PWL, WAV)
│   └── ...
│
├── _Tools/ltspice/                    # Package d'automatisation Python (uv)
│   ├── __init__.py
│   ├── runner.py                      # Exécuteur headless & détection logs _Build_Temp
│   └── log_parser.py                  # Parser de logs (*.log, .meas extraction)
├── pyproject.toml                     # Configuration uv et dépendances
├── SETUP_LTSPICE.md                   # Guide pas-à-pas de configuration de LTspice
└── .agents/                           # Directives IA, règles, compétences et workflows
```

---

## 2. Rôle du préfixe `_`

- `_Shared_Lib/` et `_Build_Temp/` utilisent un tiret bas initial afin d'être naturellement triés **en tête de liste** par les gestionnaires de fichiers (Windows Explorer, macOS Finder).
- Cette disposition met en valeur immédiate le dossier principal `Projets/` tout en séparant nettement les composants partagés et les fichiers de calcul éphémères.

---

## 3. Configuration des Chemins de Recherche (Search Paths)

Plutôt que d'utiliser des chemins absolus dans chaque schéma, LTspice doit être configuré de manière globale (voir [`SETUP_LTSPICE.md`](../../SETUP_LTSPICE.md)) :
1. **Symbol Search Path (F2) :**
   - Pointé vers `_Shared_Lib/sym` (et ses sous-dossiers de familles) ainsi que `_Shared_Lib/common_blocks`.
2. **Library Search Path :**
   - Pointé vers `_Shared_Lib/models` ET `_Shared_Lib/common_blocks`.
   - **Règle essentielle :** `common_blocks` doit être déclaré dans les deux chemins pour que LTspice charge à la fois le symbole graphique `.asy` et le schéma de simulation `.asc`.
3. **Sorties de simulation :**
   - Redirigées vers `_Build_Temp/` (Settings → Waveforms) pour éviter d'encombrer les dossiers de projet.

---

## 4. Les 3 Cas de Création de Composants

1. **Cas 1 — Modèle simple `.MODEL` :** Pas de fichier `.asy`. Utiliser un symbole standard LTspice, renseigner `Value` et inclure `.lib fichier.mod`.
2. **Cas 2 — Composant constructeur `.SUBCKT` :** Modèle texte dans `_Shared_Lib/models/`, symbole dans `_Shared_Lib/sym/` avec `Symbol Type: Cell`, `Prefix: X`, `Value: <Nom_SUBCKT>`, `ModelFile: <fichier.lib>`, et `Netlist Order` des broches calqué sur l'ordre de la directive `.SUBCKT`.
3. **Cas 3 — Bloc hiérarchique graphique :** Paire `nom.asc` + `nom.asy` dans `_Shared_Lib/common_blocks/` ou localement dans `Projets/<Projet>/sim/blocks/`. `Symbol Type: Block`, tous les attributs vides, broches avec labels identiques aux ports F4.

---

## 5. Outillage Python (`_Tools/ltspice/`)

- Géré exclusivement avec `uv`.
- [`runner.py`](../../_Tools/ltspice/runner.py) recherche automatiquement les fichiers `.log` générés soit localement à côté du `.asc`, soit dans `_Build_Temp/` si la redirection est activée.
