from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from flask import Flask, url_for, redirect, request, render_template, abort, session

app = Flask(__name__)
app.secret_key = "serpeggiante"

engine = create_engine("sqlite:///db.sqlite")
Base = declarative_base()


class Posto(Base):
    __tablename__ = "posti"

    mid = Column(Integer, primary_key=True)
    occupato = Column(Boolean, nullable=False)
    riga = Column(Integer, nullable=False)
    colonna = Column(Integer, nullable=False)
    sala_id = Column(Integer, ForeignKey('sala.nome'))
    sala = relationship("Sala", back_populates="posti")

    def status_toggle(self):
        if self.occupato:
            self.occupato = False
        else:
            self.occupato = True

    def status_give(self):
        return self.occupato

    def __init__(self, riga, colonna, sala_id):
        self.riga = riga
        self.colonna = colonna
        self.sala_id = sala_id
        self.occupato = False


class Sala(Base):
    __tablename__ = "sala"

    nome = Column(String, primary_key=True)
    numero_righe = Column(Integer, nullable=False)
    numero_colonne = Column(Integer, nullable=False)
    posti = relationship("Posto", cascade="all,delete", back_populates="sala")
    posti_tot = Column(Integer, nullable=False)
    posti_occ = Column(Integer, nullable=False)

    def __init__(self, nome, numero_righe, numero_colonne):
        self.nome = nome
        self.numero_colonne = numero_colonne
        self.numero_righe = numero_righe
        for i in range(1, self.numero_righe + 1, 1):
            for a in range(1, self.numero_colonne + 1, 1):
                nuovoposto = Posto(i, a, self.nome)
                dbsession.add(nuovoposto)
        self.posti_occ = 0
        self.posti_tot = numero_colonne * numero_righe
        dbsession.commit()


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
dbsession = Session()


@app.route('/')
def page_root():
    return redirect(url_for('page_dashboard'))


@app.route('/dashboard')
def page_dashboard():
    sale = dbsession.query(Sala).all()
    return render_template('dashboard.htm', sale=sale)


@app.route('/nuovasala', methods=['GET', 'POST'])
def page_sala_add():
    if request.method == 'GET':
        return render_template('add.htm')
    else:
        lettera = request.form['lettera']
        file = int(request.form['file'])
        colonne = int(request.form['colonne'])
        nuovasala = Sala(lettera, file, colonne)
        dbsession.add(nuovasala)
        dbsession.commit()
        return redirect(url_for('page_dashboard'))


@app.route('/delsala/<string:lettera>')
def page_sala_delete(lettera):
    sala = dbsession.query(Sala).filter_by(nome=lettera).first()
    if sala:
        dbsession.delete(sala)
        dbsession.commit()
    return redirect(url_for('page_dashboard'))


@app.route('/iscrizione/<int:colonna>/<int:fila>/<string:lettera>')
def page_posto_toggle(colonna, fila, lettera):
    posto = dbsession.query(Posto).filter_by(colonna=colonna, riga=fila, sala_id=lettera).first()
    if posto:
        posto.status_toggle()
        sala = dbsession.query(Sala).filter_by(nome=lettera).first()
        if posto.occupato:
            sala.posti_occ += 1
        else:
            sala.posti_occ -= 1
        dbsession.commit()
        return redirect(url_for('page_dashboard'))
    else:
        return abort(400)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
