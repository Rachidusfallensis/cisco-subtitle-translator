# Cisco Subtitle Translator

Ce projet traduit des fichiers de sous-titres SRT anglais en français à l'aide de l'API DeepL ( je l'ai testé avec la version libre pour le moment) et, en option, raffine les traductions avec Claude 3.5 (Anthropic) pour garantir une précision technique adaptée aux vidéos de cours Cisco.

## Prérequis

- **Python 3.9+** : Assurez-vous d'avoir Python installé.
- **Clés API** :
  - [DeepL API Key](https://www.deepl.com/pro-api) pour la traduction.
  - [Anthropic API Key](https://www.anthropic.com) pour le raffinement (optionnel).
- **FFmpeg** : Nécessaire si vous utilisez les fonctionnalités d'extraction audio.

### Installation des Dépendances

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Rachidusfallensis/cisco-subtitle-translator.git
   cd cisco-subtitle-translator
   ```
2. Créez et activez un environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur macOS/Linux
   # ou venv\Scripts\activate sur Windows
   ```
3. Installez les dépendances : 
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez les clés API dans un fichier .env à la racine
   ```bash
   echo "DEEPL_API_KEY=your_deepl_api_key" >> .env
   echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env
   ```

## Utilisation

### Interface Web (Nouveau!)

Nous avons désormais une interface web conviviale qui permet de :
- Glisser-déposer facilement des fichiers SRT
- Suivre la progression de la traduction en temps réel
- Comparer côte à côte les sous-titres originaux et traduits
- Télécharger les sous-titres traduits

Pour lancer l'interface web :
```bash
python run_web_interface.py
```
Puis accédez à http://localhost:5000 dans votre navigateur.

### Ligne de Commande

#### Traduire un fichier SRT existant :
```bash
python -m scripts.main_srt nom_du_fichier.srt
```

#### Extraire et traduire depuis une vidéo :
```bash
python -m scripts.main chemin/vers/la/video.mp4
```

## Fonctionnalités

- **Traduction SRT** : Traduction efficace de sous-titres SRT de l'anglais vers le français.
- **Raffinement avec Claude 3.5** : Amélioration des traductions pour garantir une précision technique.
- **Extraction Audio** : Extrait l'audio des vidéos pour la transcription.
- **Interface Web** : Interface utilisateur moderne avec suivi de progression et comparaison des sous-titres.

## Structure du Projet

- `scripts/` : Scripts Python principaux
- `input_srt/` : Déposez vos fichiers SRT à traduire ici
- `input_videos/` : Déposez vos vidéos ici pour l'extraction audio
- `output/` : Dossier contenant les sous-titres traduits
- `web/` : Interface web pour la traduction de sous-titres

i