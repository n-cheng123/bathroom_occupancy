from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL connection config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Summer2020$',
    'database': 'bathroom_extra'
}

def get_connection():
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        return connection
    else:
        raise ConnectionError("Failed to connect to the database.")

@app.route('/building', methods=['POST'])
def insert_building():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO building (building_name, year_built, floors, material) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (
        data['building_name'],
        data['year_built'],
        data['floors'],
        data['material']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201

@app.route("/building/<int:building_id>", methods=["GET"])
def get_building(building_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM building WHERE building_id = %s", (building_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Building not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/building', methods=['GET'])
def get_all_buildings():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM building")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results), 200



@app.route("/building/<int:building_id>", methods=["DELETE"])
def delete_building(building_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("""
            DELETE bu FROM bathroom_usage bu
            JOIN bathroom b ON bu.bathroom_id = b.bathroom_id
            JOIN floor f ON b.floor_id = f.floor_id
            WHERE f.building_id = %s
        """, (building_id,))

        cursor.execute("""
            DELETE b FROM bathroom b
            JOIN floor f ON b.floor_id = f.floor_id
            WHERE f.building_id = %s
        """, (building_id,))
        cursor.execute("DELETE FROM floor WHERE building_id = %s", (building_id,))
        cursor.execute("DELETE FROM building WHERE building_id = %s", (building_id,))

        conn.commit()
        return jsonify({"message": "Building deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/floor', methods=['POST'])
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

@app.route('/residents', methods=['GET'])
def get_residents():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT resident_id, student_id, name FROM residents")
    residents = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(residents), 200

@app.route("/residents/<int:resident_id>", methods=["GET"])
def get_resident(resident_id):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM residents WHERE resident_id = %s", (resident_id,))
    result = cursor.fetchone()
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Resident not found"}), 404

@app.route('/residents', methods=['POST'])
def add_resident():
    data = request.json
    student_id = data.get("student_id")
    name = data.get("name")

    if not student_id or not name:
        return jsonify({"error": "student_id and name required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM residents WHERE student_id=%s", (student_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "student_id must be unique"}), 409

    cursor.execute("INSERT INTO residents (student_id, name) VALUES (%s, %s)", (student_id, name))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201

@app.route('/residents/<int:resident_id>', methods=['PUT'])
def update_resident(resident_id):
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')

    if not student_id or not name:
        return jsonify({"error": "student_id and name required"}), 400

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT resident_id FROM residents WHERE resident_id = %s", (resident_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Resident not found"}), 404

            cursor.execute(
                "SELECT resident_id FROM residents WHERE student_id = %s AND resident_id != %s",
                (student_id, resident_id)
            )
            if cursor.fetchone():
                return jsonify({"error": "student_id must be unique"}), 409

            cursor.execute(
                "UPDATE residents SET student_id = %s, name = %s WHERE resident_id = %s",
                (student_id, name, resident_id)
            )
            conn.commit()

    return jsonify({"success": True}), 200

@app.route("/residents/<int:resident_id>", methods=["DELETE"])
def delete_resident(resident_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("DELETE FROM bathroom_usage WHERE resident_id = %s", (resident_id,))
        cursor.execute("DELETE FROM residents WHERE resident_id = %s", (resident_id,))

        conn.commit()
        return jsonify({"message": "Resident deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def validate_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False, field
    return True, None

@app.route('/bathroom', methods=['POST'])
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

@app.route("/bathroom/<int:bathroom_id>", methods=["GET"])
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

@app.route('/bathroom', methods=['GET'])
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

@app.route('/bathroom/<int:bathroom_id>', methods=['PUT'])
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

@app.route("/bathroom/<int:bathroom_id>", methods=["DELETE"])
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


@app.route('/bathroom_usage', methods=['POST'])
def insert_bathroom_usage():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor(buffered=True)

    cursor.execute("""
        SELECT r.floor_id, f.building_id, f.floor_id
        FROM residents r
        JOIN floor f ON r.floor_id = f.floor_id
        WHERE r.resident_id = %s
    """, (data['resident_id'],))
    res = cursor.fetchone()
    if not res:
        cursor.close()
        conn.close()
        return jsonify({"error": "Resident not found."}), 404
    resident_floor_id, resident_building_id, resident_floor_id = res

    cursor.execute("""
        SELECT building_id, floor_id
        FROM bathroom
        WHERE bathroom_id = %s
    """, (data['bathroom_id'],))
    bath = cursor.fetchone()
    if not bath:
        cursor.close()
        conn.close()
        return jsonify({"error": "Bathroom not found."}), 404
    bathroom_building_id, bathroom_floor_id = bath

    if resident_building_id != bathroom_building_id or resident_floor_id != bathroom_floor_id:
        cursor.close()
        conn.close()
        return jsonify({"error": "Resident is not allowed to use this bathroom."}), 403

    cursor.execute("""
        SELECT usage_id FROM bathroom_usage
        WHERE bathroom_id = %s
        AND ((%s < end_time) AND (%s > start_time))
    """, (data['bathroom_id'], data['start_time'], data['end_time']))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Bathroom is already in use during this time slot."}), 409

    cursor.execute("""
        INSERT INTO bathroom_usage (resident_id, bathroom_id, usage_type, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['resident_id'],
        data['bathroom_id'],
        data['usage_type'],
        data['start_time'],
        data['end_time']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201

if __name__ == '__main__':
    app.run(debug=True)
