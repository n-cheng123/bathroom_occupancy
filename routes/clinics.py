from flask import Blueprint, request, jsonify
from db import get_connection

clinic_bp = Blueprint('clinic', __name__)

@clinic_bp.route('/active_clinics', methods=['GET'])
def get_active_clinics():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DISTINCT c._id as id, c.name, c.addr, c.city, c.state, c.zip, c.phone1
        FROM clinics c
        JOIN patients p ON c._id = p.clinicId
        JOIN subscriptions s ON p.patientID = s.patientID
        WHERE s.status = 'Active'
        ORDER BY c.name
    """)
    clinics = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(clinics), 200

@clinic_bp.route('/providers', methods=['GET'])
def get_providers_for_clinic():
    clinic_id = request.args.get('clinic_id')
    if not clinic_id:
        return jsonify({"error": "clinic_id parameter required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
       SELECT DISTINCT p._id as id, CONCAT(p.firstName, ' ', p.lastName) AS name, p.npi, p.credential
        FROM physicians p, patients pa
        WHERE p._id = pa.physicianId AND pa.clinicId = %s
        ORDER BY p.lastName, p.firstName
    """, (clinic_id,))
    providers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(providers), 200

@clinic_bp.route('/patient_report_periods', methods=['GET'])
def get_patient_report_periods():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT DATE_FORMAT(g.BGdate, '%Y-%m') as yearmonth
        FROM glucoses2 g
        JOIN patients p ON g.patientID = p.patientID
        WHERE g.BGdate IS NOT NULL
        ORDER BY yearmonth DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    import calendar
    periods = []
    for (year_month,) in rows:
        year, month = year_month.split('-')
        label = f"{calendar.month_abbr[int(month)]} {year}"
        periods.append(label)

    return jsonify(periods), 200