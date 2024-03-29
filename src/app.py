"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, CharactersFavourites, PlanetsFavourites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code




#lista characters
@app.route('/characters', methods=['GET'])
def handle_characters():
        characters = Characters.query.all()
        data = [characters.serialize() for character in characters]

        return jsonify(data), 200


#single characters
@app.route('/characters/<int:id>', methods=['GET'])
def handle_singlecharacters(id):
        characters_id = Characters.query.get(id)
        if characters_id: 
            return jsonify(characters.serialize()), 200
        else: 
            return jsonify({"Mensaje": "character not found"}), 404


#list planets
@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planets.query.all()
    data = [planets.serialize() for planet in planets]

    return jsonify(data), 200


#single planets
@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_singleplanets(planet_id):
    planets_id = Planets.query.all(id)

    if plantes_id: 
        return jsonify(planets_id.serialize()), 200
    else: 
        return jsonify({"Mensaje": "planets not found"}), 404


#users
@app.route('/user', methods=['GET'])
def handle_users():
    users = User.query.all()
    data = [user.serialize() for user in users]

    return jsonify(data), 200


#favorits
@app.route('/user/favorites', methods=['GET'])
def favourites_user():
    data = request.json
    print(data)
    favorites_planets = PlanetsFavourites.query.filter_by(user_id = data["user_id"])
    favorites_characters = CharactersFavourites.query.filter_by(user_id = data["user_id"])

    data_planets = [favorite.planets_fav.serialize() for favorite in favorites_planets]
    data_characters = [favorite.characters_fav.serialize() for favorite in favorites_characters]

    return jsonify({"planets":data_planets, "characters":data_characters}), 200



#add planet favorite
@app.route('/user/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.json
    favorite = PlanetsFavourites(user_id = data["user_id"], planets_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify("planeta favorito"), 200



# add character favorite 
@app.route('/user/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    data = request.json
    favorite = CharactersFavourites(user_id = data["user_id"], characters_id=character_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify("personaje favorito"), 200


# Delete planet favorite 
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    data = request.json
    favorite = PlanetsFavourites.query.filter_by(user_id=data["user_id"], planets_id=planet_id).first()
    db.session.delete(favorite)
    db.session.commit()

    return jsonify("borrado"), 200


#Delete character favorite
@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    data = request.json
    favorite = CharactersFavourites.query.filter_by(user_id=data["user_id"], characters_id=character_id).first()
    db.session.delete(favorite)
    db.session.commit()

    return jsonify("borrado"), 200


# this only runs if `$ python src/main.py` is executed
if  __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)