from flask import Blueprint, render_template, request, jsonify

rag_bp = Blueprint('rag', __name__, url_prefix='/rag')

@rag_bp.route('/')
def index():
    return render_template('rag.html')