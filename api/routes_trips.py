from flask import Blueprint, request, jsonify, current_app
from trip_repo import TripRepository

bp_trips = Blueprint('trips', __name__)

def get_user_from_header():
	user = request.headers.get('X-User')
	if not user:
		return None
	return user

@bp_trips.route('/', methods=['GET'])
def list_trips():
	user = get_user_from_header()
	if not user:
		return jsonify({'error': 'Falta header X-User'}), 400
	repo = TripRepository(current_app.config['DB'], user)
	trips = repo.list_all()
	return jsonify({'trips': trips})

@bp_trips.route('/', methods=['POST'])
def create_trip():
	user = get_user_from_header()
	if not user:
		return jsonify({'error': 'Falta header X-User'}), 400
	data = request.get_json()
	stop_time = data.get('stop_time')
	move_time = data.get('move_time')
	total = data.get('total')
	if stop_time is None or move_time is None or total is None:
		return jsonify({'error': 'Faltan campos stop_time, move_time o total'}), 400
	repo = TripRepository(current_app.config['DB'], user)
	repo.save(stop_time, move_time, total)
	return jsonify({'message': 'Viaje guardado'}), 201
