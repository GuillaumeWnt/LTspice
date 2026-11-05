# Audit Critique, Analyse des Anomalies & Correctifs Appliqués

> **Objet :** Examen technique approfondi des schémas KiCad historiques récupérés (`Commande boucle de courant` et `Puissance boucle de courant`) et identification des incohérences, erreurs de câblage et pièges électriques avant modélisation LTspice.

---

## 1. Synthèse des Erreurs & Pièges Identifiés

| N° | Composant / Zone | Anomalie Constatée dans KiCad | Gravité | Conséquence sur Carte Réelle | Correctif Appliqué en Simulation & Réingénierie |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Optocoupleur U9 (4N25)** | **Broches 2 (cathode LED) et 4 (émetteur phototransistor) en l'air (non connectées).** | **Bloquante (Circuit inopérant)** | L'optocoupleur ne conduit jamais. La LED ne peut pas s'allumer et le phototransistor n'a pas de retour de masse. Aucun signal PWM ne peut atteindre le driver de puissance. | Broche 2 reliée à la masse de commande `GND`. Broche 4 reliée à la masse de puissance `GNDD` / `K_GND`. |
| **2** | **Connecteur J1 / J8 (Pin 7)** | **Nom de net incohérent :** nommé `PWM_Arduino` côté puissance, mais relié à `PWM_Opto` côté commande. | **Majeure (Confusion de signal)** | Confusion entre le signal logique TTL 0-5V de l'Arduino et le signal à collecteur ouvert tiré au 15V après l'optocoupleur. | Harmonisation sous le nom explicite `PWM_Opto` sur toute la ligne d'interconnexion. |
| **3** | **Réseau Darlington U6 (ULN2803A)** | Erreur de brochage reconnue dans le rapport d'EI (remplacement d'un ULN2803 par un ULN2804 de la bibliothèque ISI avec décalage de pins). | **Majeure (Inversion des commandes de relais)** | Mauvais canaux activés par l'expandeur I2C MCP23008. | Recalage strict du brochage des broches d'entrée 1-8 face aux sorties 11-18 du modèle ULN2803. |
| **4** | **Inductance de la Boucle & Étage IGBT** | Absence de diode de roue libre rapide de clamp aux bornes de la boucle de jardin (charge fortement inductive). | **Critique (Destruction composant)** | Lors de l'extinction brutale de l'IGBT ($dI/dt$ élevé dans plusieurs centaines de mètres de fil), la surtension inductive $V = -L \cdot dI/dt$ dépasse la tension d'avalanche $V_{CES} = 1200\text{V}$ de l'APT75GT120JU2 et claque la jonction. | Intégration d'un snubber RC et d'une diode de roue libre / clamp TVS rapide aux bornes de l'inductance de boucle pour dissiper l'énergie magnétique. |
| **5** | **Gestion des Masses Multiples** | Présence de `GND`, `GND1`, `GNDD`, `K_GND` sans stratégie claire d'étoilage. | **Moyenne (Bruit & instabilité)** | Les forts courants pulsés de l'IGBT traversant le plan de masse logique perturbent les mesures analogiques (Hall et Shunt) et le bus I2C. | Séparation stricte de la masse de puissance (`K_GND`) et de la masse de signal (`GNDD`), avec point de raccordement unique (star ground / net-tie 0Ω) au plus près de la borne négative de la batterie. |
| **6** | **Blocs 3.3V Obsolètes (PCA9306 & LM1117)** | Schématisation d'un régulateur 3.3V et d'un adaptateur de niveau I2C PCA9306 alors que tous les périphériques (Arduino, MCP23008, MCP3424, MCP6004) fonctionnent en 5V natif. | **Mineure (Complexité inutile)** | Consommation et composants superflus sur le PCB commande. | Neutralisation et omission de ces blocs redondants pour la simulation du cœur fonctionnel. |

---

## 2. Analyse Détaillée des Anomalies & Justifications Physiques

### 2.1 L'erreur critique de l'optocoupleur 4N25 (U9)

Dans l'arbre S-expression extrait de `Commande boucle de courant.kicad_sch` :
```text
=== UNCONNECTED PINS ===
U9.2 (4N25: ~) at (117.475, 39.37)
U9.4 (4N25: ~) at (132.715, 39.37)
```
- **Diagnostic :** La broche 2 (cathode de la diode émettrice infrarouge) est laissée flottante à 2.54 mm de la piste de masse. De même, la broche 4 (émetteur du phototransistor bipolaire) est flottante sans liaison avec la masse de la carte puissance.
- **Impact physique :** Le circuit est en circuit ouvert permanent. Le courant direct $I_F = 0$. Le transistor reste bloqué, la broche `PWM_Opto` reste en permanence tirée au +15V par $R_{31} = 10\,\text{k}\Omega$. Le driver MC33153 reçoit un niveau statique et ne commute jamais l'IGBT.
- **Correction apportée :** Raccordement de la cathode au plan `GND` commande et de l'émetteur au plan `K_GND` / `GNDD` puissance.

---

### 2.2 Surtension inductive au blocage de l'IGBT Q1

- **Contexte physique :** Le câble posé dans un jardin mesure classiquement entre 100 et 500 mètres. L'inductance linéique d'une boucle monofilaire posée au sol est de l'ordre de $1\,\mu\text{H/m}$ à $1.5\,\mu\text{H/m}$, soit une inductance totale de boucle $L_{\text{boucle}} \approx 200\,\mu\text{H}$ à $1\,\text{mH}$.
- Lorsque l'IGBT coupe un courant de $I = 10\,\text{A}$ avec un temps de descente $t_f = 200\,\text{ns}$ :
  $$\frac{dI}{dt} = \frac{10\,\text{A}}{200 \times 10^{-9}\,\text{s}} = 5 \times 10^7\,\text{A/s} = 50\,\text{A}/\mu\text{s}$$
- La surtension aux bornes de l'inductance sans clamp vaut :
  $$V_L = L \cdot \frac{dI}{dt} = 500 \times 10^{-6} \times 50 \times 10^6 = 25\,000\,\text{V} = 25\,\text{kV} !$$
- **Conséquence :** Sans diode de clamp rapide de puissance ou snubber dimensionné, le condensateur de snubber $C_6, C_7$ (1 µF) ne peut à lui seul absorber cette énergie sans faire monter la tension collecteur bien au-delà de 1200V, entraînant la destruction thermique immédiate de l'APT75GT120JU2.
- **Solution en simulation :** Modélisation d'une diode de clamp rapide haute tension ou d'une TVS bidirectionnelle de protection transitoire aux bornes de la boucle.

---

### 2.3 Chaîne de Mesure : Hall vs Shunt

Le schéma d'origine propose une double redondance (Hall ACS770 et Shunt WSK2512 2 mΩ) sélectionnable via les résistances $0\,\Omega$ $R_{15}$ et $R_{16}$ :
1. **ACS770 :** Isolation galvanique intrinsèque, sortie centrée à $V_{CC}/2 = 2.5\,\text{V}$ (ou $0.5\,\text{V}$ pour modèle unidirectionnel $0-50\text{A}$), gain typique de $80\,\text{mV/A}$. Pour 10 A, la variation est de $+800\,\text{mV}$.
2. **Shunt Kelvin 2 mΩ :** Pour 10 A, la tension différentielle est très faible :
   $$V_{\text{shunt}} = 2\,\text{m}\Omega \times 10\,\text{A} = 20\,\text{mV}$$
   Cette tension minuscule nécessite obligatoirement l'étage de gain $U_{2C}$ (Gain $\ge 10$ à 50) pour être exploitable par le comparateur $U_{2B}$, alors que pour l'ACS770, un gain de 1 est suffisant.
- **Recommandation :** Dans notre projet LTspice, nous simulons les deux voies et validons les gains respectifs de la chaîne AOP MCP6004.

