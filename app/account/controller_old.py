import sys
import hashlib
import json
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from .UserObject import UserObject
from py2neo import Graph
import datetime
from . import account_controller
from flask import Response
from app.models import *
import random
import string
from py2neo import Relationship, Node

sys.path.append("..")
from app.JWTManager import jwt
import uuid

def getHash512(text):
    return hashlib.sha512(str(text).encode("UTF-8")).hexdigest()

def make_error(status_code, sub_code, message, action):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
        'action': action
    })
    response.status_code = status_code
    return response

@account_controller.route('/activity/getAll', methods=['GET'])
@jwt_required
def getAllQUIZ(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    result = Quiz.fetch_all_by_user(db, current_user, request.args.get("activity_id"), size*page, size)
    return jsonify(result)

@account_controller.route('/activity/quiz/register', methods=['POST'])
@jwt_required
def addQuiz(db: Graph):
    current_user = get_jwt_identity()
    dataDict = json.loads(request.data)
    uuid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))

    quiz = Quiz()
    quiz.uuid = uuid
    quiz.name = dataDict['name']
    quiz.description = dataDict['description']
    quiz.time_limit = dataDict['time_limit']
    quiz.time_type  = dataDict['time_type']
    quiz.open_date = dataDict['open_date']
    quiz.end_date  = dataDict['end_date']
    quiz.new_page = dataDict['new_page']
    quiz.shuffle = dataDict['shuffle']
    quiz.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quiz.updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db.push(quiz)

    Activity.addQuiz(db, current_user, dataDict['id_activity'] ,uuid)
    
    return jsonify({"sucess": "quiz created."})

@account_controller.route('/users/activity/subnetwork/get/id', methods=['GET'])
@jwt_required
def get_by_id_subActivity(db: Graph):
    current_user = get_jwt_identity()
    result = SubActivity.fetch_by_id(db, current_user, request.args.get('id_activity'), request.args.get('id_subnetwork'))
    if result:
        result = SubActivity.fetch_by_id(db, current_user, request.args.get("id_activity"), request.args.get("id_subnetwork"))
    else:
        sub = SubActivity()
        sub.uuid = request.args.get('id_subnetwork')
        sub.all_data = "[]"
        db.push(sub)
        SubActivity.create_relationship( db, current_user, request.args.get('id_activity'), request.args.get('id_subnetwork') )
        result = {'uuid': sub.uuid, 'all_data': "[]"}
        print( "criado = " + sub.uuid)
        return jsonify(result)

@account_controller.route('/users/activity/save', methods=['POST'])
@jwt_required
def save_activity(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    # (para fazer) restringir para editar apenas as atividades criadas pelo próprio usuário
    result = Activity.update_by_user(db, current_user, dataDict['id'], dataDict['data'])
    return jsonify({"sucess": "activity saved."})

@account_controller.route('/users/activity/get/id', methods=['GET'])
@jwt_required
def get_by_id_activity(db: Graph):
    current_user = get_jwt_identity()
    result = Activity.fetch_by_id(db, current_user, request.args.get("id"))
    return jsonify(result)


@account_controller.route('/users/activity/getAll', methods=['GET'])
@jwt_required
def getall_activity(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    result = Activity.fetch_all_by_user(db, current_user, size*page, size)
    return jsonify(result)
    

@account_controller.route('/users/activity/update', methods=['POST'])
@jwt_required
def update_activity(db: Graph):
    current_user = get_jwt_identity()
    dataDict = json.loads(request.data)

def generateUUID():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))
    
@account_controller.route('/users/activity/create', methods=['POST'])
@jwt_required
def create_activity(db: Graph):
    current_user = get_jwt_identity()
    dataDict = json.loads(request.data)
    usuario = User.fetch_by_email(db, current_user )
    if not usuario:
        return jsonify({"error": "`email` são obrigatórios."}), 400

    atividade = Activity()
    atividade.id= generateUUID()
    atividade.name = "Sem título "+str(Activity.getQuantity(db, current_user))
    atividade.all_data = ""
    atividade.attachment.add(usuario)

    db.push(atividade)

    return jsonify({"sucess": "activity created.", "name":atividade.id})


@account_controller.route('/users/register', methods=['POST'])
def register(db: Graph):
    dataDict = json.loads(request.data)
    if not dataDict['email'] or not dataDict['first_name'] or not dataDict['last_name'] or not dataDict['password']:
        return jsonify({"error": "`email`, `first_name`, `last_name` e `password` são obrigatórios."}), 400

    usuario = User.fetch_by_email(graph=db, email=dataDict['email'])#Usuario.query.filter_by(email=username,senha=getHash512(password)).first()
    if usuario:
        return jsonify({"error": "Email já cadastrado."}), 400

    usuario = User()
    usuario.email = dataDict['email']
    usuario.first_name = dataDict['first_name']
    usuario.last_name = dataDict['last_name']
    usuario.passwod = getHash512(dataDict['password'])
    db.push(usuario)
    user = UserObject(username=usuario.email, role='User', permissions=['foo', 'bar'])

    expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(identity=user, expires_delta=expires)
    ret = {'token': access_token}

    return jsonify(ret), 200

@account_controller.route('/users/authenticate', methods=['POST','GET'])
def login(db: Graph):
    dataDict = json.loads(request.data)
    
    usuario = User.fetch_by_email_and_password(db, email=dataDict['email'],password=getHash512(dataDict['password']))#Usuario.query.filter_by(email=username,senha=getHash512(password)).first()
    if not usuario:
        return jsonify({"error": "Email ou senha inválido."}), 400

    user = UserObject(username=usuario.email, role='Admin', permissions=['foo', 'bar'])

    expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(identity=user, expires_delta=expires)
    ret = {'token': access_token, 'username': usuario.email}
    return jsonify(ret), 200

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username