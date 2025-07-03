from flask import Blueprint, request, jsonify, current_app
from trip_repo import TripRepository

bp_trips = Blueprint('trips', __name__)

def get_user_from_header():
	# placeholder: lee token o user header
	return request.headers.get('X-User')

@bp_trips.route('/', methods=['GET'])
def list_trips():
	user = get_user_from_header()
	repo = TripRepository(current_app.config['DB'], user)
	rows = repo.list_all()  # implementa un método list_all en tu repo
	return jsonify(rows)

@bp_trips.route('/', methods=['POST'])
def create_trip():
	user = get_user_from_header()
	data = request.get_json()
	stop_time = data['stop_time']
	move_time = data['move_time']
	total     = data['total']
	repo = TripRepository(current_app.config['DB'], user)
	trip_id = repo.save(stop_time, move_time, total)
	return jsonify({'id':trip_id}), 201
