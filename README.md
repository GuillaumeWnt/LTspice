# LTspice Simulation Hub & Python Automation Workspace

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/uv-fast%20python-purple.svg)](https://docs.astral.sh/uv/)
[![LTspice](https://img.shields.io/badge/LTspice-ADI%2024%2B-red.svg)](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Integrated-green.svg)](https://modelcontextprotocol.io/)

A professional, modular multi-project workspace designed for managing electronic circuit simulations with **LTspice**, backed by a high-performance **Python automation toolchain (`uv`)**, official **LTspice MCP integration**, and structured **AI agent directives (`.agents/`)**.

> 💡 **Guide de démarrage rapide LTspice :** Pour configurer vos chemins de recherche globaux (*Search Paths*), rediriger les fichiers temporaires et comprendre les 3 façons de créer des composants, consultez le guide dédié : **[`SETUP_LTSPICE.md`](SETUP_LTSPICE.md)**.

---

## 1. Overview & Directory Architecture

The repository enforces a clean separation between shared assets, temporary build outputs, and active engineering projects:

```text
LTspice_Workspace/
│
├── _Shared_Lib/                       # BIBLIOTHÈQUE CENTRALE (Commune à tous les projets)
│   ├── sym/                           # Symboles constructeurs (Type: Cell) classés par familles
│   ├── models/                        # Modèles texte SPICE (.lib, .sub, .mod)
│   └── common_blocks/                 # Blocs hiérarchiques réutilisables (.asc + .asy)
│
├── _Build_Temp/                       # Sorties de simulation lourdes (.raw, .log, .fft) [gitignored]
│
├── Projets/                           # TOUS VOS PROJETS INDÉPENDANTS
│   ├── <Projet_Exemple>/              # Dossier de projet (ex: Ampli_Audio, Alim_Flyback)
│   │   ├── README.md                  # Cahier des charges et spécifications du circuit
│   │   ├── docs/                      # Notes d'application, schémas-blocs, datasheets
│   │   └── sim/                       # Schémas de simulation (*.asc, *.plt)
│   │       ├── blocks/                # Blocs hiérarchiques locaux au projet (*.asc + *.asy)
│   │       └── stimuli/               # Fichiers d'excitation (ex: signaux PWL, .wav)
│   └── ...
│
├── src/ltspice/                       # Package d'automatisation Python (géré avec uv)
│   ├── __init__.py                    # Exports du package
│   ├── runner.py                      # Exécuteur headless & détection automatique _Build_Temp
│   └── log_parser.py                  # Parser de logs (*.log, extraction .meas, erreurs)
├── pyproject.toml                     # Configuration uv et dépendances Python
├── SETUP_LTSPICE.md                   # Guide complet de configuration de LTspice
├── AGENTS.md                          # Directives fondamentales pour agents IA
├── .agents/                           # Intelligence centralisée (règles, skills, subagents)
│   ├── rules/                         # Architecture, style de code, diagnostics, sécurité
│   ├── skills/                        # ltspice-manager, circuit-design-review, memory, diagrams
│   ├── subagents/                     # simulation-debugger, circuit-qa-reviewer, etc.
│   └── scripts/sync-mcp.ps1           # Script de synchronisation MCP multi-environnements
├── .mcp.json                          # Configuration standard des serveurs MCP
└── README.md                          # Documentation principale
```

> **Note sur le préfixe `_` :** Les dossiers `_Shared_Lib/` et `_Build_Temp/` utilisent un tiret bas afin de se positionner naturellement tout en haut de l'explorateur de fichiers sous Windows et macOS, laissant le dossier `Projets/` immédiatement accessible.

---

## 2. Configuration Globale de LTspice

Pour que LTspice résolve automatiquement vos symboles, modèles et sous-circuits sans jamais nécessiter de chemins absolus dans vos schémas :

1. **Symbol Search Path (F2) :** Déclarez les dossiers de symboles et blocs :
   ```text
   C:\<Chemin_Vers_Workspace>\_Shared_Lib\sym
   C:\<Chemin_Vers_Workspace>\_Shared_Lib\common_blocks
   ```
2. **Library Search Path (.lib / .sub / .asc) :** Déclarez les modèles texte et blocs :
   ```text
   C:\<Chemin_Vers_Workspace>\_Shared_Lib\models
   C:\<Chemin_Vers_Workspace>\_Shared_Lib\common_blocks
   ```
3. **Dossier de génération temporaire :** Dans **Settings → Waveforms**, cochez **Store .raw, .plt and .log files in a specific directory** et pointez vers `_Build_Temp`.

*(Consultez [`SETUP_LTSPICE.md`](SETUP_LTSPICE.md) pour les détails pas-à-pas et les explications sur les 3 types de composants).*

---

## 3. Python Automation Toolchain (`uv`)

Le projet utilise **`uv`** pour garantir un environnement virtuel Python ultra-rapide et reproductible :

```powershell
# Synchroniser l'environnement virtuel
uv sync

# Vérifier la détection de LTspice et du package local
uv run python -c "import ltspice; print('LTspice détecté sur :', ltspice.find_ltspice_executable())"
```

### Exécution Headless et Analyse des Mesures
Vous pouvez lancer une simulation sans ouvrir l'interface graphique :
```powershell
# Exécution directe via la commande enregistrée (détecte automatiquement _Build_Temp ou le dossier local)
uv run ltspice-run "Projets/<Projet>/sim/<schema>.asc"
```

Le script exécute la simulation, vérifie la convergence du solveur et extrait automatiquement toutes les directives `.meas` du fichier `.log` :
```python
from ltspice import run_simulation

result = run_simulation("Projets/Ampli_Audio/sim/main_amp.asc")
if result.success:
    print(f"Simulation réussie en {result.elapsed_seconds:.2f}s")
    for name, value in result.measurements.items():
        print(f"  {name} = {value}")
else:
    print("Erreur de simulation :", result.errors)
```

---

## 4. Règles Fondamentales SPICE

1. **Masse Explicite :** Le nœud `0` (`GND`) doit obligatoirement être présent et connecté.
2. **Attention au multiplicateur SPICE :**
   - `1M` ou `1m` correspond à **milli** ($10^{-3}$).
   - **Méga** ($10^6$) doit obligatoirement être écrit **`1Meg`** ou **`1meg`**.
3. **Modèles `.lib` vs `.sub` :**
   - `.sub` : sous-circuit individuel.
   - `.lib` : bibliothèque de plusieurs modèles. Préférez `.lib nom.lib` (optimisé, charge à la demande) à `.inc nom.sub` (recopie tout en mémoire).
4. **Blocs Hiérarchiques Graphiques :** Paire indissociable `.asc` + `.asy` de même nom dans `_Shared_Lib/common_blocks/` ou localement dans `Projets/<Projet>/sim/blocks/`. Symbole de type `Block` avec attributs vides.

---

## 5. Intégration MCP (Model Context Protocol)

Ce workspace intègre 5 serveurs MCP configurés dans [`.agents/mcp_config.json`](.agents/mcp_config.json) et synchronisés via [`.agents/scripts/sync-mcp.ps1`](.agents/scripts/sync-mcp.ps1) :

| Serveur | Commande / URL | Utilité |
| :--- | :--- | :--- |
| **`ltspice`** | `ltspice-mcp-bridge.exe` | Pont officiel Analog Devices permettant à l'IA de piloter et inspecter les instances LTspice. |
| **`memory`** | `@modelcontextprotocol/server-memory` | Graphe de connaissances persistant (spécifications de circuits, choix de composants). |
| **`brave-search`** | `@modelcontextprotocol/server-brave-search` | Recherche web en temps réel de datasheets, notes d'application et modèles SPICE. |
| **`workspace-filesystem`** | `@modelcontextprotocol/server-filesystem` | Navigation et lecture des fichiers du workspace. |
| **`io.draw/mcp`** | `https://mcp.draw.io/mcp` | Génération de schémas d'architecture et diagrammes de flux de puissance. |

---

## 6. Gouvernance des Directives IA (`.agents/`)

Tous les assistants d'IA (Antigravity, Claude, Copilot, ChatGPT) sont régis par les directives de [`AGENTS.md`](AGENTS.md) :
- **Accord préalable de l'utilisateur :** Toute création, modification ou suppression de règle requiert l'accord explicite préalable de l'utilisateur (Règle 6).
- **Centralisation stricte :** Toutes les règles résident dans `.agents/` et `AGENTS.md`. Les dossiers clients (`.claude/`, `.gemini/`, `.github/`) ne sont que des routeurs légers.
- **Suggestion systématique de commit :** Toute intervention modifiant des fichiers se termine par une proposition de message de commit Git conventionnel (Règle 5).
