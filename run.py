from app import create_app, db
import os


app = create_app()

# Crea il database se non esiste
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # Usa la variabile d'ambiente PORT o la porta di default 5000
    port = int(os.environ.get('PORT', 5000))
    # Esegui l'app (senza debug in produzione)
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', False) == '1')
