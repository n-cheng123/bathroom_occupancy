from flask import Blueprint, request, jsonify
from db import get_connection

floors_bp = Blueprint('floors', __name__)

@floors_bp.route('/floor', methods=['POST'])
def insert_floor():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO floor (building_id, floor_number) VALUES (%s, %s)"
    cursor.execute(query, (
        data['building_id'],
        data['floor_number']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201