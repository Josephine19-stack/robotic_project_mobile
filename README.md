# Projet – Drone Interactif : Gestes et Couleurs

**Auteur :** Zeina Gebran – Josephine Bernard  
*Projet robotique – Télécom Paris – ENSTA / DJI Tello*

---

## Objectif

Développer un système autonome pour le drone 'DJI Tello' capable de :
* afficher sa caméra en temps réel
* réagir à des objets verts détectés par vision
* reconnaître des gestes humains simples
* explorer automatiquement en l'absence de stimulus
* assurer un atterrissage sécurisé

---

## Technologies utilisées

* Python 3.10+
* OpenCV – vision par ordinateur
* djitellopy – API pour DJI Tello
* NumPy
* MediaPipe – détection des gestes
* Flask + HTML – affichage vidéo en direct

---
## Fonctionnalités principales

### Détection d’objet vert
Détection de zones vertes via HSV et contours. Le drone ajuste sa position ou explore l’environnement s’il ne voit rien, puis atterrit si aucune détection prolongée.

### Détection de gestes humains
Reconnaissance de gestes via règles simples (V0) ou un modèle MLP entraîné (V1). Permet de contrôler le drone (décoller, atterrir, bouger, tourner).

### Sécurité
Surveillance du vol et de la batterie. Atterrissage automatique en cas de danger ou de perte de détection.

---

## Dépendances à installer

Créer un environnement virtuel (ex: `tello_env`) puis exécuter :

```bash
pip install opencv-python mediapipe djitellopy numpy flask


