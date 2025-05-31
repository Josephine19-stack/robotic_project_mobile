# 🛸 Projet – Drone Interactif : Gestes et Couleurs

**Auteur :** Zeina Gebran – Josephine Bernard  
**Projet robotique – Télécom Paris – ENSTA / DJI Tello**

---

## 🎯 Objectif

Créer un système intelligent et interactif où un drone **DJI Tello** :
- Décolle automatiquement
- Affiche sa **caméra en temps réel**
- **Réagit à la présence d'objets colorés** (vert)
- **Explore son environnement activement** lorsqu’aucun stimulus n’est détecté pendant un certain temps
- **Interprète des gestes humains** (bras levé → tourne, 2 bras levés → atterrissage)

---

## #1 | 🔧 Technologies utilisées

- `Python 3.10+`
- `OpenCV` – vision par ordinateur
- `djitellopy` – API pour DJI Tello
- `NumPy`
- `MediaPipe` – détection de pose humaine (non utilisé dans cette version, prévu pour plus tard)

---

## #2 | 🛠 Dépendances à installer

Créer un environnement virtuel (`tello_env`) puis exécuter :

```bash
pip install opencv-python mediapipe djitellopy numpy
