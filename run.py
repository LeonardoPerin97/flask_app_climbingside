from app import create_app, db


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
    app.run(debug=True)
