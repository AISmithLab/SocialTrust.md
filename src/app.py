"""
SocialTrust Web Application
Flask-based web interface for analyzing GitHub repositories and generating trust reports
"""

from flask import Flask, render_template, request, jsonify
import os
import threading
import queue
import json
from datetime import datetime
import re

# Import existing modules
import sys
sys.path.append(os.path.dirname(__file__))
from scrape import scrape
from get_raw_metrics import get_raw_metrics
from generate_detailed_markdown_file import get_detailed_markdown_file
from generate_social_trust_readme_file import get_social_trust_readme_file

BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)

app = Flask(__name__)

# Global configuration
CONFIG_FILE = 'config.json'
ANALYSIS_QUEUE = queue.Queue()
ANALYSIS_STATUS = {}

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'github_token': ''}

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def parse_github_url(url):
    """Extract owner and repo from GitHub URL"""
    # Patterns: https://github.com/owner/repo or github.com/owner/repo
    pattern = r'(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$'
    match = re.match(pattern, url.strip())
    if match:
        return match.group(1), match.group(2)
    return None, None

def analyze_repository(job_id, owner, repo, token, create_pr=False):
    """Background task to analyze repository"""
    try:
        os.makedirs('../data', exist_ok=True)
        os.makedirs('../output', exist_ok=True)
        os.makedirs('../images', exist_ok=True)
        os.makedirs('../docs', exist_ok=True)

        data_dir = f'../data/{owner}_{repo}'
        repo_json_path = os.path.join(data_dir, 'repo.json')
        has_cached_data = os.path.isdir(data_dir) and os.listdir(data_dir)

        ANALYSIS_STATUS[job_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Starting analysis...',
            'owner': owner,
            'repo': repo
        }

        # Step 1: Scrape data
        if os.path.exists(repo_json_path) or has_cached_data:
            ANALYSIS_STATUS[job_id].update({
                'progress': 10,
                'message': 'Using existing data (skipping scrape)...'
            })
        else:
            ANALYSIS_STATUS[job_id].update({
                'progress': 10,
                'message': 'Scraping repository data from GitHub API...'
            })
            scrape(owner, repo, token)

        # Step 2: Calculate metrics
        ANALYSIS_STATUS[job_id].update({
            'progress': 40,
            'message': 'Calculating trust metrics...'
        })
        get_raw_metrics(owner, repo)

        # Step 3: Generate detailed report
        ANALYSIS_STATUS[job_id].update({
            'progress': 60,
            'message': 'Generating detailed metrics report...'
        })
        get_detailed_markdown_file(owner, repo)

        # Step 4: Generate trust percentile report
        ANALYSIS_STATUS[job_id].update({
            'progress': 80,
            'message': 'Generating trust percentile report...'
        })
        get_social_trust_readme_file(owner, repo)

        # Step 5: Create Pull Request (if requested)
        if create_pr:
            ANALYSIS_STATUS[job_id].update({
                'progress': 90,
                'message': 'Creating Pull Request...'
            })
            try:
                from github_pr import create_pull_request
                pr_url = create_pull_request(owner, repo, token)
                ANALYSIS_STATUS[job_id]['pr_url'] = pr_url
            except Exception as e:
                ANALYSIS_STATUS[job_id]['pr_error'] = str(e)

        # Complete
        ANALYSIS_STATUS[job_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Analysis complete!',
            'readme_path': f'docs/README_{repo}.md',
            'details_path': f'docs/Metrics_detail_template_Component_(Integrity)_{repo}.md',
            'images_path': f'images/{owner}_{repo}/'
        })

    except Exception as e:
        ANALYSIS_STATUS[job_id].update({
            'status': 'error',
            'message': f'Error: {str(e)}'
        })

@app.route('/')
def index():
    """Main page"""
    config = load_config()
    return render_template('index.html', token_configured=bool(config.get('github_token')))

@app.route('/analyze', methods=['POST'])
def analyze():
    """Start repository analysis"""
    data = request.get_json()
    github_url = data.get('github_url', '').strip()
    provided_token = data.get('github_token', '').strip()
    create_pr = data.get('create_pr', False)
    
    # Parse GitHub URL
    owner, repo = parse_github_url(github_url)
    if not owner or not repo:
        return jsonify({'success': False, 'error': 'Invalid GitHub URL'})
    
    # Load token
    config = load_config()
    token = provided_token or config.get('github_token', '')
    if not token:
        return jsonify({'success': False, 'error': 'GitHub token not configured'})
    if provided_token:
        save_config({'github_token': token})
    
    # Create job
    job_id = f"{owner}_{repo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Start analysis in background thread
    thread = threading.Thread(
        target=analyze_repository,
        args=(job_id, owner, repo, token, create_pr)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'job_id': job_id})

@app.route('/status/<job_id>')
def status(job_id):
    """Get analysis status"""
    if job_id not in ANALYSIS_STATUS:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(ANALYSIS_STATUS[job_id])


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('../data', exist_ok=True)
    os.makedirs('../output', exist_ok=True)
    os.makedirs('../images', exist_ok=True)
    os.makedirs('../docs', exist_ok=True)
    
    print("=" * 60)
    print("SocialTrust Web Application")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
