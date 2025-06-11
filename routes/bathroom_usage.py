from flask import Blueprint, request, jsonify
from db import get_connection

bathroom_usage_bp = Blueprint('bathroom_usage', __name__)

@bathroom_usage_bp.route('/bathroom_usage', methods=['POST'])
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
    bathroom_usage_bp.run(debug=True)
