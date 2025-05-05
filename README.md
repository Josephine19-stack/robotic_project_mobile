# 🛸 Projet – Drone Interactif : Gestes et Couleurs

**Auteur :** Zeina Gebran  - Josephine Bernard

**Projet robotique – Télécom Paris – ENSTA / DJI Tello**

---

## 🎯 Objectif

Créer un système intelligent et interactif où un drone **DJI Tello** :
- Décolle automatiquement
- Affiche sa **caméra en temps réel**
- **Réagit à la présence d'objets colorés** (ex : rouge → recule, vert → avance)
- **Interprète des gestes humains** (bras levé → tourne, 2 bras levés → atterrissage)
- **Explore son environnement activement** lorsqu’aucun stimulus n’est détecté pendant un certain temps

---

## #1 | 🔧 Technologies utilisées

- `Python 3.10+`
- `OpenCV` – vision par ordinateur
- `MediaPipe` – détection de pose humaine
- `djitellopy` – API pour DJI Tello
- `NumPy`

---

## #2 | 🛠 Dépendances à installer

Créer un environnement virtuel (`tello_env`) puis exécuter :

```bash
pip install opencv-python mediapipe djitellopy numpy
