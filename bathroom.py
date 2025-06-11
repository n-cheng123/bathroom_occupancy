from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

