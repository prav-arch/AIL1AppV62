from flask import Blueprint, render_template, request, jsonify

kafka_browser_bp = Blueprint('kafka_browser', __name__, url_prefix='/kafka-browser')

@kafka_browser_bp.route('/')
def index():
    return render_template('kafka_browser.html')