from flask import Blueprint, request, jsonify
from db import get_connection
from collections import defaultdict

patient_bp = Blueprint('summary', __name__)

def build_patient_filters():
    clinic_id = request.args.get('clinic_id')
    provider_id = request.args.get('provider_id')
    filters = []
    params = []
    if clinic_id and clinic_id not in ("", "All", "all", None):
        filters.append("p.clinicId = %s")
        params.append(clinic_id)
    if provider_id and provider_id not in ("", "All", "all", None):
        filters.append("p.physicianId = %s")
        params.append(provider_id)
    return filters, params

@patient_bp.route('/active_patients', methods=['GET'])
def get_active_patients():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter required (YYYY-MM)"}), 400

    filters, params = build_patient_filters()

    where_clauses = ["s.status = 'Active'", "DATE_FORMAT(g.BGdate, '%Y-%m') = %s"] + filters
    params.append(year_month)

    sql_where_part = ""
    if where_clauses:
        sql_where_part = f"WHERE {' AND '.join(where_clauses)}"

    sql = f"""
        SELECT DISTINCT p.patientID, p.firstName, p.lastName
        FROM patients p
        JOIN subscriptions s ON p.patientID = s.patientID
        JOIN glucoses2 g ON p.patientID = g.patientID
        {sql_where_part}
    """

    print(f"DEBUG: Active Patients SQL Query (prepared): {sql}")
    print(f"DEBUG: Active Patients SQL Params: {params}")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        patients = cursor.fetchall()
        print(f"DEBUG: Active Patients Results Count: {len(patients)}")
        print(f"DEBUG: Active Patients Results (first 5): {patients[:5]}")
        return jsonify(patients), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /active_patients: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: Active Patients SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@patient_bp.route('/testing_patients', methods=['GET'])
def get_testing_patients():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter required (YYYY-MM)"}), 400

    filters, params = build_patient_filters()
    where_clauses = ["DATE_FORMAT(g.BGdate, '%Y-%m') = %s"] + filters
    params = [year_month] + params

    sql_where_part = ""
    if where_clauses:
        sql_where_part = f"WHERE {' AND '.join(where_clauses)}"

    sql = f"""
        SELECT DISTINCT p.patientID, p.firstName, p.lastName
        FROM patients p
        JOIN glucoses2 g ON p.patientID = g.patientID
        {sql_where_part}
    """

    print(f"DEBUG: Testing Patients SQL Query (prepared): {sql}")
    print(f"DEBUG: Testing Patients SQL Params: {params}")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        patients = cursor.fetchall()
        print(f"DEBUG: Testing Patients Results Count: {len(patients)}")
        return jsonify(patients), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /testing_patients: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: Testing Patients SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@patient_bp.route('/controlled_patients', methods=['GET'])
def get_controlled_patients():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter required (YYYY-MM)"}), 400

    filters, params = build_patient_filters()
    where_clauses = ["DATE_FORMAT(g.BGdate, '%Y-%m') = %s"] + filters
    params = [year_month] + params

    sql_where_part = ""
    if where_clauses:
        sql_where_part = f"WHERE {' AND '.join(where_clauses)}"

    sql = f"""
        SELECT p.patientID, p.firstName, p.lastName, AVG(g.BGvalue) as avg_bg
        FROM patients p
        JOIN glucoses2 g ON p.patientID = g.patientID
        {sql_where_part}
        GROUP BY p.patientID
        HAVING avg_bg < 180
    """

    print(f"DEBUG: Controlled Patients SQL Query (prepared): {sql}")
    print(f"DEBUG: Controlled Patients SQL Params: {params}")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        patients = cursor.fetchall()
        print(f"DEBUG: Controlled Patients Results Count: {len(patients)}")
        return jsonify(patients), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /controlled_patients: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: Controlled Patients SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@patient_bp.route('/ea1c', methods=['GET'])
def get_ea1c():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter required (YYYY-MM)"}), 400

    filters, params = build_patient_filters()
    where_clauses = ["DATE_FORMAT(g.BGdate, '%Y-%m') = %s"] + filters
    params = [year_month] + params

    sql_where_part = ""
    if where_clauses:
        sql_where_part = f"WHERE {' AND '.join(where_clauses)}"

    sql = f"""
        SELECT p.patientID, p.firstName, p.lastName,
                AVG(g.BGvalue) as avg_bg,
                ROUND((AVG(g.BGvalue) + 46.7) / 28.7, 2) AS ea1c
        FROM patients p
        JOIN glucoses2 g ON p.patientID = g.patientID
        {sql_where_part}
        GROUP BY p.patientID
    """

    print(f"DEBUG: EA1C SQL Query (prepared): {sql}")
    print(f"DEBUG: EA1C SQL Params: {params}")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        patients = cursor.fetchall()
        print(f"DEBUG: EA1C Results Count: {len(patients)}")
        return jsonify(patients), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /ea1c: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: EA1C SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@patient_bp.route('/high_patients', methods=['GET'])
def get_high_patients():
    ref_month = request.args.get('ref_month')
    filters, params = build_patient_filters()

    conn = None
    cursor = None
    last3months = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if ref_month:
            cursor.execute("""
                SELECT DATE_FORMAT(DATE_SUB(%s, INTERVAL n MONTH), '%Y-%m') as yearmonth
                FROM (SELECT 0 as n UNION ALL SELECT 1 UNION ALL SELECT 2) nums
            """, (ref_month,))
            last3months = [row['yearmonth'] for row in cursor.fetchall()]
        else:
            cursor.execute("""
                SELECT DISTINCT DATE_FORMAT(BGdate, '%Y-%m') as yearmonth
                FROM glucoses2
                WHERE BGdate IS NOT NULL
                ORDER BY yearmonth DESC
                LIMIT 3
            """)
            last3months = [row['yearmonth'] for row in cursor.fetchall()]

        print(f"DEBUG: High Patients - Last 3 months determined: {last3months}")

        if len(last3months) < 3:
            print("DEBUG: High Patients - Less than 3 months of data available.")
            return jsonify([]), 200

        base_where_clauses = [f"DATE_FORMAT(g.BGdate, '%Y-%m') IN ({','.join(['%s']*len(last3months))})"] + filters

        sql_where_part = ""
        if base_where_clauses:
            sql_where_part = f"WHERE {' AND '.join(base_where_clauses)}"

        sql = f"""
            SELECT
                p.patientID, p.firstName, p.lastName,
                DATE_FORMAT(g.BGdate, '%Y-%m') as yearmonth,
                AVG(g.BGvalue) as avg_bg
            FROM patients p
            JOIN glucoses2 g ON p.patientID = g.patientID
            {sql_where_part}
            GROUP BY p.patientID, yearmonth
        """

        sql_params_for_avg = last3months + params
        print(f"DEBUG: High Patients - Avg BG SQL Query (prepared): {sql}")
        print(f"DEBUG: High Patients - Avg BG SQL Params: {sql_params_for_avg}")

        cursor.execute(sql, sql_params_for_avg)
        rows = cursor.fetchall()
        print(f"DEBUG: High Patients - Raw Avg BG Results Count: {len(rows)}")

        patient_months = defaultdict(list)
        for row in rows:
            if 180 <= row['avg_bg'] <= 250:
                patient_months[row['patientID']].append({
                    "firstName": row["firstName"],
                    "lastName": row["lastName"],
                    "yearmonth": row["yearmonth"]
                })

        result = []
        for pid, months in patient_months.items():
            if len(months) == 3:
                result.append({
                    "patientID": pid,
                    "firstName": months[0]["firstName"],
                    "lastName": months[0]["lastName"]
                })

        print(f"DEBUG: High Patients - Final Filtered Results Count: {len(result)}")
        return jsonify(result), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /high_patients: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: High Patients SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@patient_bp.route('/very_high_patients', methods=['GET'])
def get_very_high_patients():
    year_month = request.args.get('year_month')
    filters, params = build_patient_filters()

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if not year_month:
            cursor.execute("""
                SELECT DATE_FORMAT(BGdate, '%Y-%m') as yearmonth
                FROM glucoses2 WHERE BGdate IS NOT NULL
                ORDER BY yearmonth DESC LIMIT 1
            """)
            row = cursor.fetchone()
            year_month = row['yearmonth'] if row else None

        print(f"DEBUG: Very High Patients - Determined year_month: {year_month}")

        if not year_month:
            print("DEBUG: Very High Patients - No year_month found.")
            return jsonify([]), 200

        where_clauses = ["DATE_FORMAT(g.BGdate, '%Y-%m') = %s"] + filters
        params = [year_month] + params

        sql_where_part = ""
        if where_clauses:
            sql_where_part = f"WHERE {' AND '.join(where_clauses)}"

        sql = f"""
            SELECT p.patientID, p.firstName, p.lastName, AVG(g.BGvalue) as avg_bg
            FROM patients p
            JOIN glucoses2 g ON p.patientID = g.patientID
            {sql_where_part}
            GROUP BY p.patientID
            HAVING avg_bg > 250
        """

        print(f"DEBUG: Very High Patients SQL Query (prepared): {sql}")
        print(f"DEBUG: Very High Patients SQL Params: {params}")

        cursor.execute(sql, params)
        patients = cursor.fetchall()
        print(f"DEBUG: Very High Patients Results Count: {len(patients)}")
        return jsonify(patients), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /very_high_patients: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: Very High Patients SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@patient_bp.route('/test_compliance', methods=['GET'])
def get_test_compliance():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter required (YYYY-MM)"}), 400

    filters, params = build_patient_filters()
    where_clauses = ["DATE_FORMAT(g.BGdate, '%Y-%m') = %s"] + filters
    params = [year_month] + params

    sql_where_part = ""
    if where_clauses:
        sql_where_part = f"WHERE {' AND '.join(where_clauses)}"

    sql = f"""
        SELECT
            p.patientID,
            p.firstName,
            p.lastName,
            COUNT(g.BGvalue) AS total_readings,
            COUNT(DISTINCT DAY(g.BGdate)) AS days_with_readings,
            mo.testingFreq 
        FROM patients p
        JOIN glucoses2 g ON p.patientID = g.patientID
        LEFT JOIN medicalOrders mo ON p.patientID = mo.patientID 
        {sql_where_part}
        GROUP BY p.patientID, mo.testingFreq 
    """

    print(f"DEBUG: Test Compliance SQL Query (prepared): {sql}")
    print(f"DEBUG: Test Compliance SQL Params: {params}")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        result = cursor.fetchall()

        results_with_compliance = []
        for row in result:
            total_readings = row['total_readings']
            days_with_readings = row['days_with_readings']
            testing_freq_str = row['testingFreq']

            prescribed_frequency = 0
            if testing_freq_str and ' x / day' in testing_freq_str:
                try:
                    prescribed_frequency = int(testing_freq_str.split(' x / day')[0].strip())
                except ValueError:
                    prescribed_frequency = 0 

            compliance = 0.0
            avg_freq = 0.0

            if days_with_readings > 0:
                avg_freq = round(total_readings / days_with_readings, 1)

            if prescribed_frequency > 0 and days_with_readings > 0:
                expected_readings = prescribed_frequency * days_with_readings
                if expected_readings > 0:
                    compliance = round(total_readings / expected_readings, 1)

            results_with_compliance.append({
                "patientID": row['patientID'],
                "firstName": row['firstName'],
                "lastName": row['lastName'],
                "avg_freq": avg_freq,
                "prescribed_frequency_text": testing_freq_str, 
                "prescribed_frequency_parsed": prescribed_frequency, 
                "compliance": compliance
            })

        print(f"DEBUG: Test Compliance Final Results Count: {len(results_with_compliance)}")
        return jsonify(results_with_compliance), 200
    except ConnectionError as ce:
        print(f"ERROR: Database connection error in /test_compliance: {ce}")
        return jsonify({"error": str(ce)}), 500
    except Exception as e:
        print(f"ERROR: Test Compliance SQL Execution failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

