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
from models import db, Member
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy import exc
from datetime import timedelta

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_KEY')  # Change this!
jwt = JWTManager(app)


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

@app.route('/member', methods=['POST'])
def Register():

    new_email = request.json.get("email", None)
    new_password = request.json.get("password", None)

    if not new_email and new_password:
        return jsonify ({'error': 'invalid email or password'}), 401
    
    new_user = Member(email = new_email, password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8), is_active = True)

    try:
        Created_user = new_user.create()
        access_token = create_access_token(identity=Created_user.serialize(), expires_delta = timedelta(minutes=100))

        return jsonify({'token': access_token}), 201

    except exc.IntegrityError:
        return jsonify({'error':'can not create new user'}), 400

@app.route('/member', methods=['GET'])
def get_members():

    members = Member.get_all()
    all_member = [member.serialize() for member in members]

    return jsonify(all_member), 200

@app.route('/login', methods=['POST'])
def login():

    login_email = request.json.get("email", None)
    login_password = request.json.get("password", None)

    member = Member.get_by_email(login_email)

    if login_email and check_password_hash(member.password, login_password):

        access_token = create_access_token(identity = member.serialize(), expires_delta= timedelta(minutes=100) )

        return jsonify({'token':access_token}), 200

    
    return jsonify({'msg': 'wrong email or password'})
    

   

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
