from flask import Blueprint, request, jsonify
from db import get_connection

bathrooms_bp = Blueprint('bathrooms', __name__)

def validate_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False, field
    return True, None

@bathrooms_bp.route('/bathroom', methods=['POST'])
def insert_bathroom():
    data = request.json
    required_fields = ['floor_id', 'total_stalls', 'total_showers', 'gender_typ']
    valid, missing = validate_fields(data, required_fields)
    if not valid:
        return jsonify({"error": f"Missing field: {missing}"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT building_id FROM floor WHERE floor_id = %s", (data['floor_id'],))
    res = cursor.fetchone()
    if not res:
        cursor.close()
        conn.close()
        return jsonify({"error": "Floor not found."}), 404

    building_id = res[0]

    query = """
        INSERT INTO bathroom (building_id, floor_id, total_stalls, total_showers, gender_typ)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        building_id,
        data['floor_id'],
        data['total_stalls'],
        data['total_showers'],
        data['gender_typ']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201

@bathrooms_bp.route("/bathroom/<int:bathroom_id>", methods=["GET"])
def get_bathroom(bathroom_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bathroom WHERE bathroom_id = %s", (bathroom_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Bathroom not found"}), 404

@bathrooms_bp.route('/bathroom', methods=['GET'])
def get_all_bathrooms():
    floor_id = request.args.get('floor_id')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if floor_id:
        cursor.execute("SELECT * FROM bathroom WHERE floor_id = %s", (floor_id,))
    else:
        cursor.execute("SELECT * FROM bathroom")
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results), 200

@bathrooms_bp.route('/bathroom/<int:bathroom_id>', methods=['PUT'])
def update_bathroom(bathroom_id):
    data = request.json
    required_fields = ['floor_id', 'total_stalls', 'total_showers', 'gender_typ']
    valid, missing = validate_fields(data, required_fields)
    if not valid:
        return jsonify({"error": f"Missing field: {missing}"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bathroom WHERE bathroom_id = %s", (bathroom_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Bathroom not found."}), 404

    cursor.execute("SELECT building_id FROM floor WHERE floor_id = %s", (data['floor_id'],))
    res = cursor.fetchone()
    if not res:
        cursor.close()
        conn.close()
        return jsonify({"error": "Floor not found."}), 404

    building_id = res[0]

    query = """
        UPDATE bathroom
        SET building_id = %s, floor_id = %s, total_stalls = %s,
            total_showers = %s, gender_typ = %s
        WHERE bathroom_id = %s
    """
    cursor.execute(query, (
        building_id,
        data['floor_id'],
        data['total_stalls'],
        data['total_showers'],
        data['gender_typ'],
        bathroom_id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 200

@bathrooms_bp.route("/bathroom/<int:bathroom_id>", methods=["DELETE"])
def delete_bathroom(bathroom_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        cursor.execute("DELETE FROM bathroom_usage WHERE bathroom_id = %s", (bathroom_id,))
        cursor.execute("DELETE FROM bathroom WHERE bathroom_id = %s", (bathroom_id,))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"error": "Bathroom not found"}), 404

        conn.commit()
        return jsonify({"message": "Bathroom deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
