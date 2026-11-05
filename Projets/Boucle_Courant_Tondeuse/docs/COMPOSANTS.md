# Répertoire Détaillé des Composants (BOM & Utility Catalog)

Ce document dresse l'inventaire exhaustif des composants issus des schémas KiCad de la carte puissance et de la carte commande, en expliquant précisément leur utilité et leur rôle physique dans le système.

---

## 1. Carte Puissance (Power Board)

### 1.1 Étage de Puissance & Commutation IGBT

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **Q1** | APT75GT120JU2 | ISOTOP (SOT-227) | **IGBT haute puissance (1200V, 75A).** Commute le courant dans le fil de boucle périphérique du jardin. Supporte les fortes pointes d'intensité et les surtensions inductives au blocage. |
| **U1** | MC33153DG | SOIC-8 | **Driver de grille d'IGBT dédié.** Fournit les courants transitoires nécessaires à la charge/décharge rapide de la capacité d'entrée de grille ($C_{ies}$). Intègre la détection de désaturation pour protéger l'IGBT en cas de court-circuit sur le fil de boucle. |
| **R6** | R (ex. 10 Ω - 22 Ω) | SMD 1206 | **Résistance de grille à la mise en conduction ($R_{g,on}$).** Limite le $dI/dt$ et le pic de courant tiré du driver lors du turn-on. |
| **R7** | R (ex. 4.7 Ω - 10 Ω) | SMD 1206 | **Résistance de grille à l'extinction ($R_{g,off}$).** Permet un turn-off plus rapide que le turn-on en parallèle avec la diode D5. |
| **D5** | 1N5404 / Schottky rapide | SOD-123 | **Diode d'extinction rapide de grille.** Décharge rapidement la grille à travers R7 sans passer par R6. |
| **C6, C7** | 1 µF (haute tension) | Film WRE / SMD | **Condensateurs de snubber / découplage collecteur-émetteur.** Absorbent les oscillations transitoires haute fréquence générées par l'inductance de boucle lors des commutations. |
| **D6** | NRVA4007T3G | SMA (1000V) | **Diode de détection de désaturation.** Connectée entre la broche 8 du driver et le collecteur de l'IGBT pour surveiller la tension $V_{CE,sat}$ pendant la conduction. Si $V_{CE}$ monte au-delà du seuil (court-circuit), le driver coupe la grille et active la sortie de défaut `FaultIGBT`. |
| **R4** | R (100 kΩ) | SMD 1206 | **Résistance de limitation du circuit de désaturation.** |
| **C3** | 10 µF | Polarized AVX-N | **Capacité de temporisation de masquage de défaut (Blanking Capacitor).** Évite les faux déclenchements de désaturation pendant le temps de commutation initial de l'IGBT. |
| **D3** | 1N5404 / Diode signal | SOD-123 | **Diode d'isolation sur le signal de défaut `FaultIGBT`.** |
| **R3** | R (10 kΩ) | SMD 1206 | **Résistance de pull-up du signal de défaut.** |

### 1.2 Mesure de Courant & Capteurs

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **U3** | ACS770xCB-050U-PFF | Module CB-PFF | **Capteur de courant isolé à effet Hall unidirectionnel (0-50A).** Mesure le courant total traversant la boucle de câble. Fournit une sortie analogique isolée `V_cpt_Hall` avec une sensibilité calibrée (ex: 80 mV/A). |
| **R1** | WSK25122L000FEA (2 mΩ) | Shunt 4 bornes Kelvin 2512 | **Shunt de courant de précision (0.002 Ω).** Mesure alternative directe par chute de tension aux bornes de l'émetteur de l'IGBT. Les bornes Kelvin (E1, E2) évitent les erreurs dues aux résistances de contact. |
| **R14, R15** | R (1 kΩ) | SMD 1206 | **Résistances de filtrage et d'adaptation du signal de shunt `Sens_I`.** |
| **C9** | 100 nF | SMD 1206 | **Condensateur de filtrage haute fréquence sur le signal de shunt.** |
| **U4** | DS18B20 | TO-92 | **Capteur de température numérique 1-Wire.** Surveille l'échauffement thermique du radiateur de puissance ou du PCB. |

### 1.3 Diviseur de Surveillance Tension Haute de Boucle (`V_cond`)

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **R8, R9, R10, R11** | 50 kΩ (x4 en série = 200 kΩ) | SMD 1206 | **Branche haute du pont diviseur haute tension.** La mise en série de 4 résistances 1206 répartit la tension (évite le claquage diélectrique d'un seul boîtier SMD) et dissipe la puissance. |
| **R12** | 11 kΩ | SMD 1206 | **Résistance intermédiaire de calage du pont diviseur.** |
| **R13** | 5 kΩ | SMD 1206 | **Branche basse du diviseur de tension.** Rapport de division : $5k / (200k + 11k + 5k) \approx 1/43.2$. Pour 200V transitoires, la sortie `V_cond` est plafonnée à ~4.6V (compatible ADC/AOP 5V). |
| **C8** | 100 nF | SMD 1206 | **Filtrage passe-bas du signal `V_cond`.** Élimine le bruit parasite haute fréquence. |

### 1.4 Alimentation et Régulation 15V

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **U2** | L7815 | TO-220 | **Régulateur linéaire 24V -> 15V.** Alimente le driver d'IGBT MC33153 (qui nécessite 15V pour une commutation franche de la grille) et la carte commande via le connecteur J8. |
| **D1, D4** | NRVA4007T3G | SMA | **Diodes de protection contre les inversions de polarité et anti-retour.** |
| **D7** | B320 (Schottky 20V/30V 3A) | SMC | **Diode de protection contre les inversions et clamp de surtension d'entrée.** |
| **C1, C2** | 10 µF | AVX-N Tantalum / SMD | **Condensateurs de filtrage d'entrée et de sortie du régulateur L7815.** |
| **D2, R2** | LED verte + R (2.2 kΩ) | SMD 1206 | **Indicateur visuel de présence tension 15V.** |
| **R16, R17** | 0 Ω | SMD 1206 | **Pontets de liaison de masse (Net-ties).** Permettent de relier proprement les plans de masse de puissance (`K_GND`), masse logique (`GNDD`) et masse de protection. |

### 1.5 Connecteurs & Interfaces

| Désignateur | Type | Rôle |
| :--- | :--- | :--- |
| **J1** | Bornier à vis 4 contacts (Wurth 691321300004) | Arrivée d'alimentation continue principale (+24V, GND1). |
| **J2, J3, J5, J6** | Douilles de puissance WP-PLUG 7464000 | Raccordement robuste du câble de boucle inductive de jardin (`+Boucle`, `-Boucle`). |
| **J7, J10** | Douilles de masse supplémentaires | Reprise de masse forte intensité. |
| **J8** | Connecteur HE10 10 broches (Wurth 61201021621) | **Nappe d'interconnexion vers la carte de commande.** Transfère le 15V, 5V, les masses, `PWM_Opto`, `Sens_I`, `V_cpt_Hall`, `V_cond`, `FaultIGBT` et `Temp`. |

---

## 2. Carte Commande (Control Board)

### 2.1 Alimentation 5V & Protection

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **U1** | L7805 | TO-220 | **Régulateur linéaire 15V -> 5V.** Alimente le microcontrôleur Arduino, le quadruple AOP MCP6004, le boîtier de portes ET 74HCT08, les ADC MCP3424 et l'expandeur I2C. |
| **D3** | SM6T22A | SMB | **Diode Transil / TVS bidirectionnelle 22V.** Absorbe les transitoires et pics de tension sur le rail 15V d'entrée. |
| **C14, C3** | 10 µF | Polarized SMD | **Filtrage et découplage d'entrée (15V) et de sortie (5V) du régulateur L7805.** |
| **D1, R1** | LED + R (1 kΩ) | SMD 0805 | **Témoin de présence tension 5V.** |

### 2.2 Chaîne de Traitement Analogique & Sécurité Courant (U2 : MCP6004)

Le boîtier **U2 (MCP6004)** est un quadruple amplificateur opérationnel Rail-to-Rail basse tension (0-5V) et haute précision :

| Étage | Désignateur & Composants Associés | Fonction Électrique & Calculs |
| :--- | :--- | :--- |
| **U2A (Broches 1, 2, 3)** | Ampli Soustracteur Capteur Hall | Reçoit le signal différentiel `V_cpt_Hall`. Réseau de résistances R8 (100k), R11 (100k) sur entrée (+) et R7 (10k), R13 (10k) sur entrée (-). Filtres C6, C7 (100nF). Fournit un signal référencé à la masse `Signal_effet_halll` dirigé vers l'entrée analogique A1 de l'Arduino. |
| **U2D (Broches 12, 13, 14)** | Ampli Soustracteur Shunt de Courant | Reçoit la tension différentielle aux bornes du shunt `Sens_I` par rapport à `K_GND`. Réseau R10, R12 sur (+) et R9, R14 sur (-), filtré par C12, C13. Sortie `Signal_shunt` vers l'entrée analogique A2 de l'Arduino. |
| **R15, R16** | 0 Ω | **Aiguillage de sélection.** Permet de choisir matériellement quelle mesure de courant (Hall via R15 ou Shunt via R16) est injectée dans la chaîne de sécurité rapide. |
| **U2C (Broches 8, 9, 10)** | Ampli Non-Inverseur (Gain Réglable) | Étage d'amplification optionnel activé par R18 (0R) et R21/R17 (10k/10k, Gain = $1 + R_{21}/R_{17} = 2$). Permet d'amplifier le signal de courant si sa dynamique est trop faible. Si bypassé par R20 (0R), le signal traverse directement. |
| **U2B (Broches 5, 6, 7)** | Comparateur de Dépassement de Seuil | Compare la mesure de courant sélectionnée (sur entrée inverseuse broche 6) à une tension de consigne de seuil ajustable (sur entrée non-inverseuse broche 5). |
| **RV1, R25, R26** | Trimpot 50 kΩ + R25 (1 kΩ) + R26 (100 kΩ) | **Réglage manuel du seuil de courant maximum admissible.** Crée une consigne de tension stable sur la broche 5 de U2B. |
| **R33, D2, R32, C15** | R33 (20 Ω), 1N4148W, R32 (10 kΩ), 100 nF | **Circuit de mise en forme et verrouillage du défaut.** La diode D2 et le filtre RC maintiennent l'information de dépassement de seuil pour assurer un arrêt franc du signal logique. |

### 2.3 Logique de Sécurité Rapide & Optocouplage (U3 : 74HCT08 & U9 : 4N25)

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **U3** | 74LS08 / 74HCT08 | SOIC-14 | **Quadruple porte ET logique.** Détermine si l'impulsion de puissance est autorisée :<br>- **Porte U3B :** Combine le signal de validation et le statut du comparateur U2B pour générer le signal de sécurité `I_Max_Int` (relié à l'interruption externe D3 de l'Arduino).<br>- **Porte U3A :** Effectue le produit logique strict entre le signal `PWM_Arduino` (issu de D9) et l'autorisation `I_Max_Int`. En cas de surintensité, la sortie `PWM` est coupée en quelques dizaines de nanosecondes, bien avant que l'Arduino n'ait le temps d'exécuter sa routine logicielle. |
| **R30** | 0 Ω | SMD 0805 | Pontet de validation du signal logique PWM. |
| **U9** | 4N25 | DIP-6 / SMD | **Optocoupleur d'isolation galvanique du signal PWM.** Isole totalement la logique commande (Arduino / 5V) de l'étage de puissance haute énergie (15V / IGBT).<br>- **LED d'entrée (broches 1-2) :** Pilotée par la porte ET via R27 (1 kΩ).<br>- **Phototransistor (broches 4-5) :** Collecteur tiré au 15V par R31 (10 kΩ), générant le signal `PWM_Opto` destiné au driver MC33153. |
| **R27** | 1 kΩ | SMD 0805 | Résistance de limitation de courant dans la LED infrarouge du 4N25 ($I_F \approx 3.8 \text{ mA}$). |
| **R31** | 10 kΩ | SMD 0805 | Résistance de rappel (Pull-up) au 15V sur la ligne `PWM_Opto`. |

### 2.4 Commutation des Batteries & Périphériques I2C

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **U7** | MCP23008-xP | SOIC-18 | **Expandeur d'E/S I2C 8 bits.** Permet à l'Arduino de commander les différents relais de batterie sur le bus I2C (SDA/SCL) sans consommer de précieuses broches numériques directes. |
| **U6** | ULN2803A / ULN2804A | SOIC-18 | **Réseau de 8 transistors Darlington 50V / 500mA avec diodes de roue libre intégrées.** Amplifie les sorties logiques de l'expandeur U7 pour piloter les bobines des relais de batterie raccordés aux borniers J4, J5, J6, J8. |
| **VR1** | PEC11R-4220F-S0024 | Encodeur rotatif | Interface utilisateur de réglage (bouton poussoir et signaux en quadrature avec filtres R4, R5, R6 et C4, C5). |
| **DS2** | LCD 1602 (WC1602A) | Connecteur I2C | Afficheur LCD pour les diagnostics et l'état du système. |

### 2.5 Surveillance Batteries (Sous-schémas Diviseurs & MCP3424)

| Désignateur | Valeur / Référence | Boîtier / Type | Rôle Électrique & Justification Fonctionnelle |
| :--- | :--- | :--- | :--- |
| **U8, U10 (ou U5)** | MCP3424 | SOIC-14 | **Convertisseur Analogique-Numérique (CAN) 18 bits Delta-Sigma 4 canaux I2C.** Mesure avec une grande résolution la tension et la température des 4 packs de batteries DeWalt. |
| **R36, R44** | 27 kΩ | SMD 1206 | Branche haute des ponts diviseurs de tension batterie (18V-54V). |
| **R45, R46** | 1 kΩ | SMD 1206 | Branche basse des ponts diviseurs de tension batterie. |
| **R34** | 243 Ω | SMD 1206 | Résistance de polarisation de la thermistance CTN interne de la batterie. |
| **D6** | RCLAMP0582BQTCT | SOT-523 | Diode TVS de clamp à 5V pour protéger les entrées du MCP3424 contre toute surtension. |
| **C8, C10, C16** | 10 µF, 100 nF | SMD 1206 | Condensateurs de filtrage et d'amortissement de bruit sur les voies de mesure. |

