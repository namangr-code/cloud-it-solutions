import http.server
import socketserver
import json
import os
import urllib.parse

PORT = 3000
BASE_DIR = os.path.dirname(__file__)

# Fallback to root directory if public/ folder is missing (flat deployment)
if os.path.exists(os.path.join(BASE_DIR, 'public')):
    PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
else:
    PUBLIC_DIR = BASE_DIR
    DATA_DIR = BASE_DIR

ASSESSMENTS_FILE = os.path.join(DATA_DIR, 'assessments.json')

# Setup directories
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(ASSESSMENTS_FILE):
    with open(ASSESSMENTS_FILE, 'w') as f:
        json.dump([], f)

class CloudITServer(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve static assets from public folder
        path = super().translate_path(path)
        rel_path = os.path.relpath(path, os.getcwd())
        return os.path.join(PUBLIC_DIR, rel_path)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Clean routing rules
        clean_routes = {
            '/': 'index.html',
            '/comparison': 'comparison.html',
            '/calculator': 'calculator.html',
            '/assessment': 'assessment.html',
            '/roadmap': 'roadmap.html',
            '/case-studies': 'case-studies.html',
            '/literature': 'literature.html'
        }

        if path in clean_routes:
            file_path = os.path.join(PUBLIC_DIR, clean_routes[path])
            self.send_html_file(file_path)
            return

        # API Handlers
        if path == '/api/assessments':
            self.handle_get_assessments()
            return
        elif path.startswith('/api/assessments/'):
            assessment_id = path.split('/')[-1]
            self.handle_get_assessment_by_id(assessment_id)
            return

        # Default static file routing
        super().do_GET()

    def send_html_file(self, file_path):
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")

    def handle_get_assessments(self):
        try:
            with open(ASSESSMENTS_FILE, 'r') as f:
                data = json.load(f)
            self.send_json_response(200, data)
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def handle_get_assessment_by_id(self, assessment_id):
        try:
            with open(ASSESSMENTS_FILE, 'r') as f:
                assessments = json.load(f)
            found = next((item for item in assessments if item['id'] == assessment_id), None)
            if found:
                self.send_json_response(200, found)
            else:
                self.send_json_response(404, {'error': 'Assessment not found'})
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == '/api/assessments':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                body = json.loads(post_data.decode('utf-8'))
                self.handle_create_assessment(body)
            except Exception as e:
                self.send_json_response(400, {'error': f'Invalid JSON payload: {str(e)}'})
            return
        
        self.send_error(404, "Endpoint not found")

    def handle_create_assessment(self, body):
        business_name = body.get('businessName')
        industry = body.get('industry')
        size = body.get('size')
        budget = body.get('budget', 'medium')
        security_importance = body.get('securityImportance', 'standard')
        tech_expertise = body.get('techExpertise', 'medium')
        current_tools = body.get('currentTools', [])
        pain_points = body.get('painPoints', [])

        if not business_name or not industry or not size:
            self.send_json_response(400, {'error': 'Missing required fields'})
            return

        # Generate recommendations
        recommendations = []
        primary_service_types = []

        if 'excel' in current_tools or 'paper' in current_tools or 'collaboration' in pain_points:
            primary_service_types.append('SaaS (Software as a Service)')
            recommendations.append({
                'category': 'Collaboration & Productivity',
                'solutions': ['Google Workspace', 'Microsoft 365'],
                'reason': 'Replaces offline file storage and paper documents with unified email, storage, and real-time document editing.'
            })

        if 'accounting' in pain_points or 'paper' in current_tools:
            primary_service_types.append('SaaS (Software as a Service)')
            recommendations.append({
                'category': 'Accounting & Finance',
                'solutions': ['QuickBooks Online', 'Zoho Books'],
                'reason': 'Automates bookkeeping, invoice distribution, and provides cloud ledger access for tax compliance.'
            })

        if 'crm' in pain_points:
            primary_service_types.append('SaaS (Software as a Service)')
            recommendations.append({
                'category': 'Customer Relationship Management',
                'solutions': ['Zoho CRM', 'Salesforce Essentials'],
                'reason': 'Consolidates customer histories, leads, and tracking pipelines to ensure no sales follow-up is missed.'
            })

        if 'hosting' in pain_points or size == 'medium' or tech_expertise == 'high':
            primary_service_types.append('IaaS (Infrastructure as a Service)')
            primary_service_types.append('PaaS (Platform as a Service)')
            recommendations.append({
                'category': 'Infrastructure & Custom Hosting',
                'solutions': ['Amazon Web Services (AWS)', 'Google Cloud Platform (GCP)', 'DigitalOcean'],
                'reason': 'Offers highly customizable VMs, secure SQL/NoSQL databases, and storage layers for proprietary apps.'
            })
        elif tech_expertise == 'low' and 'hosting' in pain_points:
            primary_service_types.append('PaaS (Platform as a Service)')
            recommendations.append({
                'category': 'Managed Hosting & Deployments',
                'solutions': ['Heroku', 'Render', 'AWS Elastic Beanstalk'],
                'reason': 'Automates app deployments and configurations, reducing complexity for companies without IT operations teams.'
            })

        # Security actions
        if security_importance == 'critical':
            security_roadmap = [
                'Enforce Multi-Factor Authentication (MFA) across all email and data providers.',
                'Enforce Role-Based Access Controls (RBAC) to block unauthorized file sharing.',
                'Set up automatic weekly cloud data backup snapshots with strict encryption.',
                'Organize cyber security training sessions for employees.'
            ]
        else:
            security_roadmap = [
                'Enforce basic MFA protocols on administrator profiles.',
                'Enable automatic daily backups for accounting and customer records.',
                'Assign unique user credentials; prohibit shared office passwords.'
            ]

        # Cost options
        if budget == 'low':
            budget_tips = [
                'Choose entry tiers or free options for SaaS subscriptions.',
                'Avoid deploying unmanaged AWS virtual machines that incur hourly running costs.',
                'Consolidate separate tools into Google Workspace or Microsoft 365 starter kits.'
            ]
        else:
            budget_tips = [
                'Commit to annual subscription agreements to save up to 20% on software fees.',
                'Utilize serverless functions (like AWS Lambda) to charge strictly on application requests.',
                'Employ a dedicated implementation specialist to avoid costly setup mistakes.'
            ]

        # Build roadmap phases
        roadmap_steps = [
            {
                'phase': 'Phase 1: Assessment & Strategy (Weeks 1-2)',
                'actions': [
                    f"Audit all existing {', '.join(current_tools) if current_tools else 'legacy'} resources.",
                    'Assign a migration coordinator to oversee project phases.'
                ]
            },
            {
                'phase': 'Phase 2: Core SaaS Integration (Weeks 3-6)',
                'actions': [
                    f"Integrate {r['solutions'][0]} for {r['category'].lower()}." for r in recommendations if r['category'] != 'Infrastructure & Custom Hosting'
                ] + ['Configure security layers and identity protections (MFA).']
            },
            {
                'phase': 'Phase 3: Workload Migration (Weeks 7-12)',
                'actions': [
                    'Migrate custom/legacy databases to secure cloud backups.' if 'hosting' in pain_points else 'Coordinate bulk document uploads to cloud-backed drives.',
                    'Initiate beta trials with select staff to fine-tune system configurations.'
                ]
            },
            {
                'phase': 'Phase 4: Management & Cost Auditing (Ongoing)',
                'actions': security_roadmap + budget_tips
            }
        ]

        import random
        assessment_id = f"asm_{random.randint(100000, 999999)}"
        import datetime
        timestamp = datetime.datetime.now().isoformat()

        new_assessment = {
            'id': assessment_id,
            'timestamp': timestamp,
            'businessName': business_name,
            'industry': industry,
            'size': size,
            'budget': budget,
            'securityImportance': security_importance,
            'techExpertise': tech_expertise,
            'currentTools': current_tools,
            'painPoints': pain_points,
            'recommendations': {
                'primaryServiceTypes': list(set(primary_service_types)),
                'detailedRecommendations': recommendations,
                'securityRoadmap': security_roadmap,
                'budgetTips': budget_tips,
                'roadmapSteps': roadmap_steps
            }
        }

        try:
            with open(ASSESSMENTS_FILE, 'r') as f:
                assessments = json.load(f)
            assessments.append(new_assessment)
            with open(ASSESSMENTS_FILE, 'w') as f:
                json.dump(assessments, f, indent=2)
            self.send_json_response(201, new_assessment)
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def send_json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Run
if __name__ == '__main__':
    handler = CloudITServer
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Python server running at http://localhost:{PORT}")
        httpd.serve_forever()
