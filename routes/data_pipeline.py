"""
Data Pipeline routes for the AI Assistant Platform.
Handles pipeline jobs management using Nifi/Airflow.
"""

from flask import Blueprint, render_template, request, jsonify, session
from db import execute_query
import logging
import json
import time
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
data_pipeline_bp = Blueprint('data_pipeline', __name__, url_prefix='/data_pipeline')

@data_pipeline_bp.route('/')
def index():
    """Data Pipeline main page."""
    # Get pipeline jobs from database
    jobs = get_pipeline_jobs()
    
    # Get recent job runs
    recent_runs = get_recent_job_runs(limit=10)
    
    return render_template(
        'data_pipeline.html', 
        jobs=jobs,
        recent_runs=recent_runs
    )

@data_pipeline_bp.route('/jobs', methods=['GET'])
def list_jobs():
    """List pipeline jobs."""
    jobs = get_pipeline_jobs()
    return jsonify({'jobs': jobs})

@data_pipeline_bp.route('/jobs', methods=['POST'])
def create_job():
    """Create a new pipeline job."""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        schedule = data.get('schedule')
        pipeline_type = data.get('pipeline_type')
        config = data.get('config')
        
        # Validate inputs
        if not name or not pipeline_type:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Add job to database
        job_id = execute_query("""
            INSERT INTO pipeline_jobs (name, description, schedule, pipeline_type, config, created_at, last_modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (name, description, schedule, pipeline_type, json.dumps(config) if config else None, 
              datetime.now(), datetime.now()))
        
        return jsonify({
            'success': True,
            'job_id': job_id[0]['id'] if job_id else None
        })
        
    except Exception as e:
        logger.error(f"Error creating pipeline job: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_pipeline_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific pipeline job."""
    try:
        # Get job from database
        job = execute_query("""
            SELECT * FROM pipeline_jobs WHERE id = %s
        """, (job_id,))
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        # Get job runs
        runs = execute_query("""
            SELECT * FROM job_runs 
            WHERE job_id = %s
            ORDER BY start_time DESC
            LIMIT 10
        """, (job_id,))
        
        job = job[0]
        job['runs'] = runs if runs else []
        
        return jsonify({'job': job})
        
    except Exception as e:
        logger.error(f"Error getting pipeline job: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_pipeline_bp.route('/jobs/<int:job_id>/run', methods=['POST'])
def run_job(job_id):
    """Run a pipeline job."""
    try:
        # Get job from database
        job = execute_query("""
            SELECT * FROM pipeline_jobs WHERE id = %s
        """, (job_id,))
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Create a new job run
        run_id = execute_query("""
            INSERT INTO job_runs (job_id, status, start_time)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (job_id, 'running', datetime.now()))
        
        # In a real implementation, this would trigger the actual pipeline
        # For now, we'll simulate a successful run after a delay
        
        # For demo purposes, let's simulate some processing time
        # In a real app, this would be a background task
        time.sleep(1)
        
        # Update the job run status to success
        execute_query("""
            UPDATE job_runs 
            SET status = %s, end_time = %s
            WHERE id = %s;
        """, ('success', datetime.now(), run_id[0]['id'] if run_id else None), fetch=False)
        
        return jsonify({
            'success': True,
            'run_id': run_id[0]['id'] if run_id else None,
            'message': 'Job started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error running pipeline job: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_pipeline_jobs():
    """Get pipeline jobs."""
    try:
        jobs = execute_query("""
            SELECT id, name, description, schedule, pipeline_type, config, created_at, last_modified,
                (SELECT COUNT(*) FROM job_runs WHERE job_id = pipeline_jobs.id) as run_count,
                (SELECT status FROM job_runs WHERE job_id = pipeline_jobs.id ORDER BY start_time DESC LIMIT 1) as last_status
            FROM pipeline_jobs
            ORDER BY last_modified DESC
        """)
        
        return jobs if jobs else []
    except Exception as e:
        logger.error(f"Error getting pipeline jobs: {str(e)}")
        return []

def get_recent_job_runs(limit=20):
    """Get recent job runs."""
    try:
        runs = execute_query("""
            SELECT jr.id, jr.job_id, jr.status, jr.start_time, jr.end_time, jr.error_message,
                   pj.name as job_name, pj.pipeline_type
            FROM job_runs jr
            JOIN pipeline_jobs pj ON jr.job_id = pj.id
            ORDER BY jr.start_time DESC
            LIMIT %s
        """, (limit,))
        
        return runs if runs else []
    except Exception as e:
        logger.error(f"Error getting recent job runs: {str(e)}")
        return []