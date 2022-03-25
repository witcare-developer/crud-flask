from crypt import methods
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

class Dono(db.Model):
    __tablename__ = 'dono'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    adress = db.Column(db.String(100))
    pets = db.relationship('Pet', backref='dono')

    def to_json(self):
        #pets = [ [pet.name, pet.id] for pet in self.pets]
        pets = []
        for pet in self.pets:
            pets.append( {"id":pet.id, "name": pet.name, "age":pet.age} )
            
        return {"id": self.id, "name": self.name, "adress": self.adress, "pets": pets }

class Pet(db.Model):
    __tablename__ = 'pet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    dono_id = db.Column(db.Integer, db.ForeignKey('dono.id'))

    def to_json(self):
        return {"id": self.id, "name": self.name, "age": self.age, }

# Selecionar tudo
@app.route('/donos', methods=["GET"])
def seleciona_donos():
    dono_objetos = Dono.query.all()
    dono_json = [dono.to_json() for dono in dono_objetos]
    print(dono_objetos[1].pets[0].name)

    return gera_response(200, 'usuarios', dono_json)

# Selecionar individual
@app.route("/dono/<int:id>", methods=['GET'])
def selciona_dono(id):
    dono_objeto = Dono.query.filter_by(id=id).first()
    dono_json = dono_objeto.to_json()
    return gera_response(200, 'donos', dono_json)

# Criar Dono
@app.route("/dono", methods=["POST"])
def cria_dono():
    body = request.get_json()

    try:
        dono = Dono(name=body['name'], adress=body['adress'])
        db.session.add(dono)
        db.session.commit()
        return gera_response(201, "dono", dono.to_json(), "Criado com sucesso.")
    except Exception as e:
        print(e)
        return gera_response(400, "dono", {}, "Erro ao cadastrar.")

# Criar Pet
@app.route("/pet/<int:id>", methods=["POST"])
def cria_pet(id):
    body = request.get_json()

    try:
        dono = Dono.query.get(id)
        print(dono.name)
        pet = Pet(name=body['name'], age=body['age'], dono=dono)
        db.session.add(pet)
        db.session.commit()
        return gera_response(201, "pet", pet.to_json(), "Criado com sucesso.")
    except Exception as e:
        print(e)
        return gera_response(400, "pet", {}, "Erro ao cadastrar.")

# Atualizar Dono
@app.route("/dono/<int:id>", methods=["PUT"])
def atualiza_dono(id):
    dono_obj = Dono.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if 'name' in body:
            dono_obj.name = body['name']
        if 'adress' in body:
            dono_obj.adress = body['adress']
        db.session.add(dono_obj)
        db.session.commit()
        return gera_response(200, "dono",dono_obj.to_json() , "Atualizado com sucesso.")
    except Exception as e:
        print(e)
        return gera_response(400, "dono", {}, "Erro ao atualizar.")

# Deletar Dono
@app.route("/dono/<int:id>", methods=['DELETE'])
def deleta_dono(id):
    dono_obj = Dono.query.filter_by(id=id).first()
    try:
        pet_id_obj = [id.id for id in dono_obj.pets]
        for i in pet_id_obj:
            pet_del = Pet.query.filter_by(id=i)
            print(pet_del[0].id)
            for i in pet_del:
                db.session.delete(i)
                db.session.commit()
        db.session.delete(dono_obj)
        db.session.commit()
        return gera_response(200, "dono",dono_obj.to_json() , "Deletado com sucesso.")
    except Exception as e:
        print(e)
        return gera_response(400, "dono", {}, "Erro ao deletar.")

def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body['mensagem'] = mensagem
    
    return Response(json.dumps(body), status = status, mimetype="application/json")

app.run(debug=True)