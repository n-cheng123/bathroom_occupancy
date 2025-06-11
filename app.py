from flask import Flask
from flask_cors import CORS

from routes.buildings import buildings_bp
from routes.floors import floors_bp
from routes.bathrooms import bathrooms_bp
from routes.residents import residents_bp
from routes.bathroom_usage import bathroom_usage_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(buildings_bp)
app.register_blueprint(floors_bp)
app.register_blueprint(bathrooms_bp)
app.register_blueprint(residents_bp)
app.register_blueprint(bathroom_usage_bp)

if __name__ == '__main__':
    app.run(debug=True)