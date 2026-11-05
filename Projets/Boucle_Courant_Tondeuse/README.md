# Projet : Boucle de Courant Tondeuse (Émetteur Câble Périphérique)

> **Statut :** En cours de refonte et modularisation (reprise de l'ancien projet KiCad Groupe 2 EI).  
> **Type de projet :** Électronique de puissance et contrôle-commande pour boucle inductive de guidage.  
> **Environnement :** LTspice (simulation hiérarchique modulaire) & Python `uv`.

---

## 1. Vue d'Ensemble du Projet

Ce projet a pour objectif d'émettre des impulsions de courant calibrées dans un câble périmétrique ("fil de jardin") servant de balise électromagnétique pour le guidage d'une tondeuse robot autonome.

Le système est alimenté par une source continue (batterie 24V ou packs batteries 18V/54V) et se compose de deux sous-ensembles fonctionnels principaux :

1. **Carte Puissance (Power Board) :**
   - Étage de puissance basé sur un **IGBT haute puissance (APT75GT120JU2)**.
   - Circuit de commande de grille spécialisé **MC33153DG** avec protection contre la désaturation (court-circuit / surintensité).
   - Double mesure de courant dans la boucle :
     - Capteur à effet Hall isolé **ACS770xCB-050U-PFF** (0 à 50 A).
     - Résistance de shunt 4 fils de précision **WSK2512 (2 mΩ)**.
   - Régulation locale de tension **15V (L7815)** pour le driver IGBT.
   - Capteur numérique de température de carte **DS18B20**.
   - Pont diviseur haute tension résistif sur le collecteur de l'IGBT (`V_cond`).

2. **Carte Commande (Control Board) :**
   - Régulation locale de tension **5V (L7805)**.
   - Isolation galvanique du signal de commande via **optocoupleur (4N25)**.
   - Étage analogique de mise en forme et de sécurité avec quadruple AOP **MCP6004** :
     - Amplificateur soustracteur pour capteur Hall (`U2A`).
     - Amplificateur soustracteur pour shunt de courant (`U2D`).
     - Étage de gain optionnel réglable (`U2C`).
     - Comparateur à seuil rapide (`U2B`) avec potentiomètre de consigne `RV1`.
   - Étage de logique de sécurité par portes ET **74HCT08** (`U3`) pour couper instantanément le PWM en cas de surintensité (`I_Max_Int`).
   - Commutation de bancs de batteries via réseau de transistors Darlington **ULN2803A** (`U6`) piloté par expandeur I2C **MCP23008** (`U7`).
   - Surveillance de tension et température de batteries (packs DeWalt 18V/54V) via CAN 18 bits I2C **MCP3424** (`U8`, `U10` / `U5`) et ponts diviseurs avec thermistances CTN.
   - Microcontrôleur maître **Arduino Uno R3**.

---

## 2. Architecture Hiérarchique Modulaire

Pour garantir une clarté absolue, le projet est décomposé en blocs hiérarchiques stricts :

```text
Boucle_Courant_Tondeuse/
│
├── README.md                          # Présentation générale du projet
├── docs/                              # Documentation détaillée
│   ├── COMPOSANTS.md                  # Répertoire exhaustif et rôles des composants
│   ├── BLOCS_HIERARCHIE.md            # Spécification des blocs, sous-blocs et interfaces
│   └── ANALYSE_ET_CORRECTIFS.md       # Audit des erreurs KiCad historiques & correctifs
│
└── sim/                               # Schémas de simulation LTspice
    ├── top_boucle_courant.asc         # Schéma maître unifié (Top Level)
    ├── blocks/                        # Blocs hiérarchiques (Paires .asc + .asy)
    │   ├── bloc_puissance.asc         # Bloc général Puissance
    │   ├── bloc_puissance.asy
    │   ├── bloc_commande.asc          # Bloc général Commande
    │   ├── bloc_commande.asy
    │   ├── sub_driver_igbt.asc        # Sous-bloc : Driver MC33153 + IGBT
    │   ├── sub_driver_igbt.asy
    │   ├── sub_mesure_courant.asc     # Sous-bloc : Shunt + Capteur Hall
    │   ├── sub_mesure_courant.asy
    │   ├── sub_conditionnement.asc    # Sous-bloc : AOP MCP6004 (Soustraction + Comparateur)
    │   ├── sub_conditionnement.asy
    │   ├── sub_logique_securite.asc   # Sous-bloc : Portes ET 74HCT08 + Opto 4N25
    │   ├── sub_logique_securite.asy
    │   ├── sub_alim_15v.asc           # Sous-bloc : Régulateur L7815
    │   ├── sub_alim_15v.asy
    │   ├── sub_alim_5v.asc            # Sous-bloc : Régulateur L7805
    │   └── sub_alim_5v.asy
    └── tests/                         # Bancs d'essais unitaires
        ├── test_driver_igbt.asc       # Test de commutation IGBT & désaturation
        ├── test_conditionnement.asc   # Test de la chaîne de mesure et déclenchement comparateur
        └── test_alims.asc             # Test de charge transitoire des régulateurs 15V et 5V
```

---

## 3. Principaux Correctifs Appliqués au Schéma KiCad Historique

L'audit approfondi des fichiers sources KiCad (`.kicad_sch`, `.kicad_pcb`, rapport d'EI) a mis en évidence plusieurs anomalies critiques qui ont été corrigées pour la modélisation SPICE :

1. **Optocoupleur 4N25 à broches en l'air :** Dans le schéma de commande KiCad, la cathode de la LED (broche 2) et l'émetteur du phototransistor (broche 4) n'étaient reliés à aucun potentiel (broches non connectées). L'optocoupleur ne pouvait donc pas fonctionner. Elles ont été raccordées respectivement à la masse commande `GND` et à la masse puissance `K_GND`.
2. **Incohérence d'étiquetage du connecteur d'interconnexion (J1 / J8) :** La broche 7 était nommée `PWM_Arduino` côté carte puissance alors qu'il s'agit du signal optocouplé `PWM_Opto` issu du collecteur du 4N25.
3. **Masse de découplage et retour de shunt :** Définition explicite des potentiels de référence entre la masse de commande `GND`, la masse de puissance `K_GND` et la masse filtrée `GNDD` pour éviter les boucles d'impédance commune lors des commutations de l'IGBT (pics à plusieurs dizaines d'ampères).
4. **Protection de surtension inductive de la boucle :** Ajout et vérification du clamping de roue libre sur l'IGBT pour absorber l'énergie inductive du câble périphérique à l'extinction.

