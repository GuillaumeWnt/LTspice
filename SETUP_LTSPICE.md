# Guide de Configuration LTspice — Architecture Multi-Projets

Ce guide détaille la mise en place pas-à-pas de l'environnement LTspice pour fonctionner de manière fluide avec l'arborescence multi-projets de ce dépôt, sans chemins absolus codés en dur dans vos schémas et sans pollution de fichiers temporaires.

> **Note sur les exemples :** Les composants, sous-dossiers et noms de circuits mentionnés ci-dessous sont purement illustratifs pour faciliter la compréhension.

---

## 1. Arborescence du Workspace

L'espace de travail isole l'infrastructure partagée, les fichiers temporaires et les projets applicatifs :

```text
LTspice_Workspace/
│
├── _Shared_Lib/                       # BIBLIOTHÈQUE CENTRALE (Commune à tout le workspace)
│   ├── sym/                           # Symboles composants constructeurs (Type: Cell)
│   │   ├── OpAmps/
│   │   │   └── OPA1656.asy
│   │   └── MOSFETs/
│   │       └── IRFP240.asy
│   ├── models/                        # Modèles texte SPICE (.lib, .sub, .mod)
│   │   ├── OPA1656.lib
│   │   ├── IRFP240.sub
│   │   └── mes_diodes.mod
│   └── common_blocks/                 # Vos sous-schémas réutilisables (Type: Block)
│       ├── alim_symetrique_labo.asc   # Schéma interne du bloc
│       └── alim_symetrique_labo.asy   # Symbole du bloc (même nom exact)
│
├── _Build_Temp/                       # Fichiers volumineux générés (.raw, .log, .fft)
│
├── Projets/                           # TOUS VOS PROJETS INDÉPENDANTS
│   ├── Ampli_Audio/
│   │   ├── README.md
│   │   ├── docs/
│   │   └── sim/
│   │       ├── main_amp.asc           # Schéma principal
│   │       ├── main_amp.plt           # Configuration d'affichage des courbes
│   │       ├── blocks/                # Blocs hiérarchiques propres à CE projet
│   │       │   ├── filtre_entree.asc
│   │       │   └── filtre_entree.asy
│   │       └── stimuli/
│   │           └── test_audio.wav
│   │
│   └── Alim_Flyback/
│       ├── README.md
│       ├── docs/
│       └── sim/
│           ├── flyback_top.asc
│           └── flyback_top.plt
│
├── src/ltspice/                       # Outillage d'automatisation Python (uv)
└── .agents/                           # Directives IA, règles, compétences et workflows
```

### Pourquoi le préfixe `_` sur certains dossiers ?
Le caractère souligné `_` (`_Shared_Lib/`, `_Build_Temp/`) est une astuce d'affichage naturelle pour Windows et macOS. Il force l'explorateur de fichiers à trier les dossiers d'infrastructure tout en haut de la liste, maintenant ainsi vos répertoires applicatifs (`Projets/`) bien regroupés juste en dessous.

---

## 2. Configuration Globale de LTspice (Search Paths)

Cette configuration s'effectue **une seule fois** dans l'interface de LTspice. Supposons que la racine de votre dépôt soit située dans `C:\LTspice_Workspace` (à adapter selon votre chemin réel).

### Étape 1 : Déclarer les chemins de recherche (Search Paths)

1. Ouvrez LTspice → Cliquez sur **Settings** (icône roue dentée / Control Panel) → Onglet **Search Paths** (ou *Sym. & Lib. Search Paths*).
2. Dans la zone **Symbol Search Path** (répertoire où LTspice cherche les symboles `.asy` lorsque vous appuyez sur **F2**), renseignez :
   ```text
   C:\LTspice_Workspace\_Shared_Lib\sym
   C:\LTspice_Workspace\_Shared_Lib\sym\OpAmps
   C:\LTspice_Workspace\_Shared_Lib\sym\MOSFETs
   C:\LTspice_Workspace\_Shared_Lib\common_blocks
   ```
   > **Astuce F2 :** LTspice ne scanne pas récursivement les sous-dossiers lors de l'ouverture du menu F2. Déclarer explicitement chaque sous-dossier de `sym` permet de les choisir directement dans le menu déroulant **Top Directory**.

3. Dans la zone **Library Search Path** (répertoire où LTspice cherche les modèles texte `.lib`/`.sub`/`.mod` **ET** les sous-schémas `.asc` des blocs partagés), renseignez :
   ```text
   C:\LTspice_Workspace\_Shared_Lib\models
   C:\LTspice_Workspace\_Shared_Lib\common_blocks
   ```

> [!IMPORTANT]
> **Règle d'or pour `common_blocks` :** Ce dossier **doit obligatoirement être déclaré à la fois** dans *Symbol Search Path* et dans *Library Search Path*.
> - *Symbol Search Path* permet d'afficher le symbole `.asy` dans la bibliothèque F2.
> - *Library Search Path* permet à LTspice de trouver et charger le schéma interne `.asc` lors de la simulation.

---

### Étape 2 : Rediriger les fichiers temporaires de simulation

Toujours dans **Settings** → Onglet **Waveforms** :
- Cochez l'option **Store .raw, .plt and .log files in a specific directory** (sous LTspice 24, seuls `.raw` et `.log` sont déplacés, préservant ainsi vos `.plt` locaux).
- Indiquez le chemin absolu de votre dossier temporaire :
  ```text
  C:\LTspice_Workspace\_Build_Temp
  ```

**Bénéfice :** Vos dossiers de projets (`sim/`) restent parfaitement propres, sans fichiers binaires de plusieurs centaines de mégaoctets qui polluent l'arborescence ou Git.

---

## 3. Guide Récapitulatif : Créer Chaque Type de Composant

Dans LTspice, tout composant ou sous-circuit s'intègre selon l'un de ces **3 cas de figure** :

| Cas | Type de composant | Fichiers nécessaires | Emplacement | Attributs clés du `.asy` |
| :--- | :--- | :--- | :--- | :--- |
| **Cas 1** | Composant simple (`.MODEL` : Diode, BJT, MOS simple) | Symbole standard LTspice + fichier `.mod` | `_Shared_Lib/models/` | Pas de `.asy` à créer (symbole d'origine LTspice) |
| **Cas 2** | Composant constructeur (`.SUBCKT` : AOP, CI, MOS complexe) | `composant.asy` + `composant.lib` (ou `.sub`) | `.asy` dans `_Shared_Lib/sym/`<br>`.lib` dans `_Shared_Lib/models/` | `Symbol Type: Cell`<br>`Prefix: X`<br>`Value: <Nom_SUBCKT>`<br>`ModelFile: <fichier.lib>` |
| **Cas 3** | Votre propre circuit (Bloc hiérarchique graphique) | `bloc.asc` + `bloc.asy` (même nom exact) | `_Shared_Lib/common_blocks/` (partagé)<br>ou `sim/blocks/` (local au projet) | `Symbol Type: Block`<br>Tous les champs attributs **vides** |

---

### Cas 1 : Modèle `.MODEL` simple (sans créer de symbole)

Lorsque le modèle téléchargé chez le fabricant est une simple directive `.MODEL` (ex. `.MODEL 1N4007 D(IS=7.02e-9 RS=0.034 ...)`), **aucun symbole `.asy` n'est requis** :

1. Enregistrez la ligne `.MODEL` dans `_Shared_Lib/models/mes_diodes.mod`.
2. Sur votre schéma `.asc`, placez une diode standard de LTspice (raccourci **D**).
3. Faites **Ctrl + Clic droit** sur le composant (ou clic droit sur le texte `D`), puis saisissez le nom exact du modèle dans le champ **Value** (ex: `1N4007`).
4. Ajoutez la directive SPICE sur votre schéma (touche **S**) :
   ```spice
   .lib mes_diodes.mod
   ```
   *(Comme `_Shared_Lib/models` est déclaré dans votre Library Search Path, aucun chemin d'accès n'est nécessaire).*

---

### Cas 2 : Composant constructeur complexe (`.SUBCKT`)

Lorsque le modèle constructeur commence par `.SUBCKT` (ex. `.SUBCKT OPA1656 IN+ IN- V+ V- OUT`) :

1. **Sauvegarder le modèle :** Placez le fichier texte `OPA1656.lib` dans `_Shared_Lib/models/`.
2. **Créer le symbole `.asy` :**
   - Menu **File → New Symbol**, dessinez les contours (menu **Draw → Line / Rectangle**).
   - Ajoutez les broches via **Edit → Add Pin/Port** (raccourci **P**).
   - **Règle absolue du Netlist Order :** Le champ **Netlist Order** (1, 2, 3...) de chaque broche doit strictement respecter **l'ordre séquentiel d'apparition sur la ligne `.SUBCKT`** du fichier texte, et non le brochage physique du boîtier (DIP8, SOIC, etc.) !
     - *Exemple :* `.SUBCKT OPA1656 IN+ IN- V+ V- OUT`
     - Broche `IN+` → Netlist Order `1`
     - Broche `IN-` → Netlist Order `2`
     - Broche `V+`  → Netlist Order `3`
     - Broche `V-`  → Netlist Order `4`
     - Broche `OUT` → Netlist Order `5`
3. **Renseigner les attributs du symbole (`Ctrl + A`) :**
   - **Symbol Type** : `Cell`
   - **Prefix** : `X` *(indique à SPICE qu'il s'agit d'un sous-circuit)*
   - **Value** : `OPA1656` *(doit correspondre mot pour mot au nom après `.SUBCKT`)*
   - **ModelFile** : `OPA1656.lib` *(uniquement le nom du fichier, sans chemin absolu)*
4. **Visibilité des labels :**
   - Menu **Edit → Attributes → Attribute Window**, cochez `InstName` (affiche `U1`, `U2`...) et `Value` (affiche `OPA1656`), puis placez-les à côté du symbole.
5. **Enregistrement :**
   - Enregistrez dans le sous-dossier adéquat : `_Shared_Lib/sym/OpAmps/OPA1656.asy`.

---

### Cas 3 : Bloc Hiérarchique Graphique (`.asc` + `.asy`)

Pour transformer un de vos schémas en boîte noire réutilisable dans d'autres schémas :

1. **Dessiner le schéma interne (`mon_bloc.asc`) :**
   - Créez le schéma et enregistrez-le dans `_Shared_Lib/common_blocks/mon_bloc.asc` (si commun) ou dans `Projets/<Projet>/sim/blocks/mon_bloc.asc` (si local).
   - Placez des labels (touche **F4**) sur tous les signaux traversant la frontière du bloc, en choisissant un **Port Type** (`Input`, `Output` ou `Bi-Direct`).
   - Ne placez **aucune directive de simulation** (`.tran`, `.ac`) dans ce sous-schéma.
2. **Générer le symbole du bloc (`mon_bloc.asy`) :**
   - Depuis le schéma ouvert, allez dans le menu **Hierarchy → Open this Sheet's Symbol**. LTspice propose de créer automatiquement le symbole avec les bonnes broches.
   - Ouvrez les attributs (**Ctrl + A**) et vérifiez :
     - **Symbol Type** : Réglé sur **`Block`**.
     - **Attributs :** Tous les autres champs (`Prefix`, `Value`, `ModelFile`...) doivent rester **totalement vides**.
   - Vérifiez que le nom de chaque broche porte exactement le même label que le port F4 correspondant.
   - Enregistrez sous le même nom exact : `mon_bloc.asy` au même endroit que `mon_bloc.asc`.
3. **Paramétrage dynamique d'un bloc hiérarchique (`PARAMS:`) :**
   - Dans le schéma interne, vous pouvez utiliser des variables entre accolades (ex. résistance `{R_charge}` avec `.param R_charge=100` par défaut).
   - Sur votre schéma principal, faites un **clic droit** sur le bloc posé et renseignez la ligne **PARAMS:** (ex. `R_charge=50`) pour surcharger la valeur sans modifier le sous-schéma.

---

## 4. Différence Technique entre `.lib` et `.sub`

Pour le moteur de simulation SPICE, **il n'y a aucune différence technique de format** : ce sont tous deux des fichiers de texte brut ASCII. La distinction repose sur une convention d'organisation :

* **`.sub` (Subcircuit individuel) :** Contient généralement **un seul composant** décrit sous forme de sous-circuit (`.SUBCKT Nom ... .ENDS`).
* **`.lib` (Bibliothèque / Collection) :** Contient généralement **une collection de plusieurs composants** regroupés par un constructeur (plusieurs `.SUBCKT` et/ou `.MODEL`).
* **Performance de la directive `.lib` vs `.inc` :**
  - La directive `.lib nom_fichier.lib` est optimisée : LTspice ne charge en mémoire que les modèles réellement posés sur le schéma.
  - La directive `.inc nom_fichier.sub` recopie textuellement l'intégralité du fichier dans la netlist avant simulation.

