Write-Host "Activation de l'environnement virtuel..."
.\env\Scripts\Activate.ps1

Write-Host "Lancement du serveur Django..."
python manage.py runserver
