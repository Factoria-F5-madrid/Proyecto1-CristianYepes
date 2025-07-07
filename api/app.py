from flask import Flask
from flask_cors import CORS
from db import Database
from auth import AuthSystem
from trip_repo import TripRepository

def create_app():
	app = Flask(__name__)
	CORS(app)

	db = Database()
	app.config['DB'] = db

	# registra blueprints
	from api.routes_auth import bp_auth
	from api.routes_trips import bp_trips
	app.register_blueprint(bp_auth, url_prefix='/api/auth')
	app.register_blueprint(bp_trips, url_prefix='/api/trips')

	return app

if __name__ == '__main__':
	create_app().run(debug=True)
