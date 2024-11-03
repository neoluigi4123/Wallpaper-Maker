#!/bin/bash

# Vérifie si Python 3.10 est déjà installé
if ! python3.10 --version &>/dev/null; then
    echo "Python 3.10 n'est pas installé. Installation en cours..."
    
    # Met à jour le système et installe Python 3.10
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-distutils
    
    # Vérifie si Python 3.10 a été installé avec succès
    if ! python3.10 --version &>/dev/null; then
        echo "L'installation de Python 3.10 a échoué."
        exit 1
    fi
else
    echo "Python 3.10 est déjà installé."
fi

# Crée et active un environnement virtuel
python3.10 -m venv env
source env/bin/activate

# Installe les bibliothèques nécessaires
pip install --upgrade pip
pip install pillow

# Télécharge le script depuis GitHub
SCRIPT_URL="https://raw.githubusercontent.com/neoluigi4123/Wallpaper-Maker/refs/heads/main/wallpaper%20maker.py"
SCRIPT_NAME="wallpaper_maker.py"
curl -o "$SCRIPT_NAME" "$SCRIPT_URL"

# Lance le script Python téléchargé
python "$SCRIPT_NAME"

# Désactive l'environnement virtuel
deactivate
