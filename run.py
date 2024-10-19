from app import create_app, db
import os


app = create_app()

# Crea il database se non esiste
with app.app_context():
    db.create_all()

from app.models import Wall
with app.app_context():
    # Controlla se i dati iniziali devono essere inseriti
    if Wall.query.count() == 0:
        wall_a = Wall(name="A")
        wall_b = Wall(name="B")
        wall_c = Wall(name="C")
        wall_d = Wall(name="D")
        db.session.add(wall_a)
        db.session.add(wall_b)
        db.session.add(wall_c)
        db.session.add(wall_d)
        db.session.commit()



if __name__ == '__main__':
    # Usa la variabile d'ambiente PORT o la porta di default 5000
    port = int(os.environ.get('PORT', 5000))
    # Esegui l'app (senza debug in produzione)
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', False) == '1')