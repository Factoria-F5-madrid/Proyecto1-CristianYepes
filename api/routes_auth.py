from flask import Blueprint, request, jsonify, current_app
from auth import AuthSystem

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/register', methods=['POST'])
def register():
	data = request.get_json()
	username = data.get('username')
	password = data.get('password')
	auth = AuthSystem(current_app.config['DB'])
	user = auth.register(username, password)
	if not user:
		return jsonify({'error':'Usuario existe'}), 400
	return jsonify({'message':'Registrado','user':user}), 201

@bp_auth.route('/login', methods=['POST'])
def login():
	data = request.get_json()
	username = data.get('username')
	password = data.get('password')
	auth = AuthSystem(current_app.config['DB'])
	user = auth.login(username, password)
	if not user:
		return jsonify({'error':'Credenciales inválidas'}), 401
	# opcional: emitir JWT aquí
	return jsonify({'message':'Autenticado','user':user})
