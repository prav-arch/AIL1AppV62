from flask import Blueprint, render_template, request, jsonify

data_pipeline_bp = Blueprint('data_pipeline', __name__, url_prefix='/data-pipeline')

@data_pipeline_bp.route('/')
def index():
    return render_template('data_pipeline.html')