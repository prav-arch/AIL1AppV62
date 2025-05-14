from flask import Blueprint, render_template, request, jsonify

anomalies_bp = Blueprint('anomalies', __name__, url_prefix='/anomalies')

@anomalies_bp.route('/')
def index():
    return render_template('anomalies.html')