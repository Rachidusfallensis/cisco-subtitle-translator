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
3.Installez les dépendances : 
pip install -r requirements.txt

4. Configurez les clés API dans un fichier .env à la racine
echo "DEEPL_API_KEY=your_deepl_api_key" >> .env

echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env

