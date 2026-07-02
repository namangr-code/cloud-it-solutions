# Project Source Code Submission
### Project: Enhancing Small Business Efficiency through Cloud-Based IT Solutions

This document aggregates all the backend and frontend source files developed for the project.

---

## File: `server.py`

```python
import http.server
import socketserver
import json
import os
import urllib.parse

PORT = 3000
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
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

```

---

## File: `public/js/app.js`

```javascript
// Common Utility Functions & Interactivity

document.addEventListener('DOMContentLoaded', () => {
  // Highlight Active Nav Item
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('nav a');
  navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (currentPath === linkPath || (currentPath === '/' && linkPath === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Accordion Logic (for literature review page)
  const headers = document.querySelectorAll('.accordion-header');
  headers.forEach(header => {
    header.addEventListener('click', () => {
      const content = header.nextElementSibling;
      const isOpen = content.classList.contains('open');
      
      // Close other panels
      document.querySelectorAll('.accordion-content').forEach(c => {
        c.classList.remove('open');
        c.style.maxHeight = null;
      });

      if (!isOpen) {
        content.classList.add('open');
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  });

  // Service Comparison Page Tab Switcher
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));
      
      btn.classList.add('active');
      const pane = document.getElementById(targetId);
      if (pane) pane.classList.add('active');
    });
  });

  // Initializations
  initCalculator();
  initAssessment();
});

// ROI Calculator Logic
let roiChart = null;
function initCalculator() {
  const onPremiseHardwareInput = document.getElementById('calc-onprem-hardware');
  const onPremiseMaintInput = document.getElementById('calc-onprem-maint');
  const downtimeCostInput = document.getElementById('calc-downtime-cost');
  const cloudSubInput = document.getElementById('calc-cloud-sub');
  
  if (!onPremiseHardwareInput) return; // Check if on calculator page

  const updateCalculations = () => {
    const hw = parseFloat(onPremiseHardwareInput.value);
    const maint = parseFloat(onPremiseMaintInput.value);
    const downtime = parseFloat(downtimeCostInput.value);
    const cloudSub = parseFloat(cloudSubInput.value);

    // Update UI value indicators
    document.getElementById('val-onprem-hardware').innerText = '$' + hw.toLocaleString();
    document.getElementById('val-onprem-maint').innerText = '$' + maint.toLocaleString();
    document.getElementById('val-downtime-cost').innerText = '$' + downtime.toLocaleString();
    document.getElementById('val-cloud-sub').innerText = '$' + cloudSub.toLocaleString();

    // 3 Year Projection
    // On-Premise: Year 1 = Hardware + Maint + Downtime, Year 2 & 3 = Maint + Downtime
    const onPremiseY1 = hw + maint + downtime;
    const onPremiseY2 = maint + downtime;
    const onPremiseY3 = maint + downtime;
    const onPremiseCumulative = [onPremiseY1, onPremiseY1 + onPremiseY2, onPremiseY1 + onPremiseY2 + onPremiseY3];

    // Cloud: Year 1 = Cloud Subscription * 12 + Setup Cost (approx 15% of hw), Year 2 & 3 = Cloud Subscription * 12
    const cloudSetup = hw * 0.15;
    const cloudY1 = (cloudSub * 12) + cloudSetup;
    const cloudY2 = cloudSub * 12;
    const cloudY3 = cloudSub * 12;
    const cloudCumulative = [cloudY1, cloudY1 + cloudY2, cloudY1 + cloudY2 + cloudY3];

    // Savings
    const totalOnPremise = onPremiseY1 + onPremiseY2 + onPremiseY3;
    const totalCloud = cloudY1 + cloudY2 + cloudY3;
    const netSavings = totalOnPremise - totalCloud;
    const roiPercentage = ((netSavings) / totalCloud) * 100;

    document.getElementById('metric-onprem-total').innerText = '$' + totalOnPremise.toLocaleString();
    document.getElementById('metric-cloud-total').innerText = '$' + totalCloud.toLocaleString();
    document.getElementById('metric-savings-net').innerText = (netSavings >= 0 ? '' : '-') + '$' + Math.abs(netSavings).toLocaleString();
    document.getElementById('metric-roi').innerText = (netSavings >= 0 ? '+' : '-') + Math.abs(roiPercentage).toFixed(0) + '%';

    // Chart.js updates
    if (roiChart) {
      roiChart.data.datasets[0].data = onPremiseCumulative;
      roiChart.data.datasets[1].data = cloudCumulative;
      roiChart.update();
    }
  };

  // Add event listeners to sliders
  [onPremiseHardwareInput, onPremiseMaintInput, downtimeCostInput, cloudSubInput].forEach(slider => {
    slider.addEventListener('input', updateCalculations);
  });

  // ChartJS setup
  const ctx = document.getElementById('roiChart');
  if (ctx) {
    roiChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Year 1 (Setup)', 'Year 2', 'Year 3 (Cumulative)'],
        datasets: [
          {
            label: 'On-Premise Infrastructure',
            data: [0, 0, 0],
            borderColor: '#ff4b5c',
            backgroundColor: 'rgba(255, 75, 92, 0.1)',
            borderWidth: 3,
            tension: 0.3,
            fill: true
          },
          {
            label: 'Cloud Integration',
            data: [0, 0, 0],
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            borderWidth: 3,
            tension: 0.3,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: {
              color: '#f3f4f6',
              font: { family: 'Outfit' }
            }
          }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#9ca3af',
              callback: value => '$' + value.toLocaleString()
            }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#9ca3af' }
          }
        }
      }
    });

    // Run initial calculations
    updateCalculations();
  }
}

// Assessment and Dynamic Roadmap Logic
function initAssessment() {
  const form = document.getElementById('cloud-assessment-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Collect data
    const businessName = document.getElementById('biz-name').value;
    const industry = document.getElementById('biz-industry').value;
    const size = document.getElementById('biz-size').value;
    const budget = document.getElementById('biz-budget').value;
    const securityImportance = document.getElementById('biz-security').value;
    const techExpertise = document.getElementById('biz-tech').value;

    const currentTools = [];
    document.querySelectorAll('input[name="current-tools"]:checked').forEach(cb => {
      currentTools.push(cb.value);
    });

    const painPoints = [];
    document.querySelectorAll('input[name="pain-points"]:checked').forEach(cb => {
      painPoints.push(cb.value);
    });

    const payload = {
      businessName,
      industry,
      size,
      budget,
      securityImportance,
      techExpertise,
      currentTools,
      painPoints
    };

    try {
      const response = await fetch('/api/assessments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const result = await response.json();
      
      // Store result ID in session storage to render on roadmap page
      sessionStorage.setItem('latestAssessmentId', result.id);
      
      // Redirect to roadmap page
      window.location.href = 'roadmap.html';

    } catch (err) {
      console.error('Error submitting assessment:', err);
      alert('There was a problem generating your roadmap. Please check your connection and try again.');
    }
  });
}

// Function to fetch and render the roadmap on roadmap.html
async function renderRoadmap() {
  const container = document.getElementById('roadmap-container');
  if (!container) return;

  const assessmentId = sessionStorage.getItem('latestAssessmentId');
  if (!assessmentId) {
    container.innerHTML = `
      <div class="card" style="text-align: center;">
        <h3>No Assessment Found</h3>
        <p style="margin-bottom: 1.5rem;">To view your personalized cloud roadmap, please complete the assessment first.</p>
        <a href="assessment.html" class="btn btn-primary">Start Assessment</a>
      </div>
    `;
    return;
  }

  try {
    const res = await fetch(`/api/assessments/${assessmentId}`);
    if (!res.ok) throw new Error('Roadmap fetch failed');
    const data = await res.json();

    const recs = data.recommendations;
    let serviceTypesHtml = recs.primaryServiceTypes.map(t => `<span class="tab-btn active" style="margin-right: 0.5rem; display:inline-block; font-size: 0.85rem; padding: 0.4rem 0.8rem; pointer-events: none;">${t}</span>`).join('');

    let detailedRecsHtml = recs.detailedRecommendations.map(r => `
      <div class="card" style="margin-bottom: 1rem;">
        <div class="card-icon" style="margin-bottom: 1rem; width: 2.5rem; height: 2.5rem;"><i class="fas fa-cube"></i></div>
        <h3>${r.category}</h3>
        <p style="color: var(--color-secondary); font-weight: 600; margin-bottom: 0.5rem;">Recommended Solutions: ${r.solutions.join(', ')}</p>
        <p>${r.reason}</p>
      </div>
    `).join('');

    let roadmapHtml = recs.roadmapSteps.map(step => `
      <div class="roadmap-step">
        <h4>${step.phase}</h4>
        <ul>
          ${step.actions.map(act => `<li>${act}</li>`).join('')}
        </ul>
      </div>
    `).join('');

    container.innerHTML = `
      <div style="margin-bottom: 2.5rem;">
        <h2 style="margin-bottom: 0.5rem;">Custom Cloud Roadmap for ${data.businessName}</h2>
        <p><strong>Industry:</strong> ${data.industry} | <strong>Scale:</strong> ${data.size.toUpperCase()}</p>
        <div style="margin-top: 1rem;">
          <strong>Target Service Classifications:</strong>
          <div style="margin-top: 0.5rem;">${serviceTypesHtml}</div>
        </div>
      </div>

      <div style="margin-bottom: 3rem;">
        <h3 style="margin-bottom: 1rem;">Recommended Cloud Software Stack</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
          ${detailedRecsHtml}
        </div>
      </div>

      <div style="margin-bottom: 3rem;">
        <h3 style="margin-bottom: 1rem;">Phased Integration Timeline</h3>
        <div class="roadmap-timeline">
          ${roadmapHtml}
        </div>
      </div>

      <div style="display: flex; gap: 1rem;">
        <a href="assessment.html" class="btn btn-secondary">Retake Assessment</a>
        <button onclick="window.print()" class="btn btn-primary">Print / Export Roadmap</button>
      </div>
    `;

  } catch (err) {
    console.error('Error rendering roadmap:', err);
    container.innerHTML = `<p>Error loading roadmap details. Please try again.</p>`;
  }
}
window.renderRoadmap = renderRoadmap;

```

---

## File: `public/css/style.css`

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg-primary: #0b0f19;
  --bg-secondary: #111827;
  --bg-tertiary: #1f2937;
  --glass-bg: rgba(17, 24, 39, 0.7);
  --glass-border: rgba(255, 255, 255, 0.08);
  --text-primary: #f3f4f6;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --color-primary: #6366f1; /* Indigo */
  --color-primary-glow: rgba(99, 102, 241, 0.15);
  --color-secondary: #06b6d4; /* Cyan */
  --color-secondary-glow: rgba(6, 182, 212, 0.15);
  --color-accent: #a855f7; /* Purple */
  --color-success: #10b981; /* Emerald */
  --color-warning: #f59e0b; /* Amber */
  --font-heading: 'Outfit', sans-serif;
  --font-body: 'Plus Jakarta Sans', sans-serif;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-glow: 0 0 25px -5px rgba(99, 102, 241, 0.4);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-body);
  line-height: 1.6;
  overflow-x: hidden;
  background-image: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.1) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.1) 0px, transparent 50%);
  background-attachment: fixed;
}

/* Scrollbar Customization */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* Header & Navigation */
header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--glass-border);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo span {
  font-weight: 300;
  color: var(--text-primary);
  -webkit-text-fill-color: var(--text-primary);
}

nav ul {
  display: flex;
  list-style: none;
  gap: 1.5rem;
}

nav a {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.3s ease, text-shadow 0.3s ease;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
}

nav a:hover, nav a.active {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

nav a.active {
  border-bottom: 2px solid var(--color-primary);
  border-radius: 0.5rem 0.5rem 0 0;
}

/* Main Container */
main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  min-height: calc(100vh - 160px);
}

/* Hero Section */
.hero {
  text-align: center;
  padding: 4rem 1rem 6rem;
  position: relative;
}

.hero::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--color-primary-glow) 0%, transparent 70%);
  z-index: -1;
  pointer-events: none;
}

h1 {
  font-family: var(--font-heading);
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 1.5rem;
  letter-spacing: -0.025em;
  background: linear-gradient(135deg, var(--text-primary) 30%, var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero p {
  font-size: 1.25rem;
  color: var(--text-secondary);
  max-width: 800px;
  margin: 0 auto 2.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem 1.8rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  box-shadow: 0 4px 14px var(--color-primary-glow);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--text-secondary);
}

/* Feature Grid / Cards */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 2.25rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: var(--shadow-xl), 0 0 20px rgba(99, 102, 241, 0.05);
}

.card:hover::before {
  opacity: 1;
}

.card-icon {
  width: 3rem;
  height: 3rem;
  background: var(--bg-tertiary);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  color: var(--color-primary);
  font-size: 1.5rem;
}

h2 {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}

h3 {
  font-family: var(--font-heading);
  font-size: 1.35rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

p {
  color: var(--text-secondary);
  font-size: 0.975rem;
}

/* Cost & ROI Calculator Page */
.calculator-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 3rem;
  align-items: start;
}

@media (max-width: 968px) {
  .calculator-layout {
    grid-template-columns: 1fr;
  }
}

.calc-panel {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 2rem;
}

.control-group {
  margin-bottom: 1.75rem;
}

.control-group label {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.control-group label span {
  color: var(--color-secondary);
  font-family: var(--font-heading);
  font-size: 1.05rem;
}

.slider-input {
  width: 100%;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  transition: transform 0.1s ease;
  box-shadow: 0 0 10px var(--color-primary);
}

.slider-input::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.chart-panel {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
  text-align: center;
}

.metric-value {
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.metric-value.savings {
  color: var(--color-success);
}

.metric-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Service Comparison Page styling */
.comp-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 0.75rem;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active, .tab-btn:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px var(--color-primary-glow);
}

.tab-content {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 2.5rem;
}

.tab-pane {
  display: none;
}

.tab-pane.active {
  display: block;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.5rem;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--glass-border);
}

th {
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--text-primary);
}

tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

/* Form Styles for Assessment */
.form-section {
  max-width: 800px;
  margin: 0 auto;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  padding: 3rem;
}

.form-group {
  margin-bottom: 2rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.input-text, select {
  width: 100%;
  padding: 0.85rem 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 0.75rem;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.input-text:focus, select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-glow);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.option-card {
  position: relative;
}

.option-card input[type="checkbox"], .option-card input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.option-label {
  display: block;
  padding: 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--glass-border);
  border-radius: 0.75rem;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.option-card input:checked + .option-label {
  border-color: var(--color-primary);
  background: var(--color-primary-glow);
  color: var(--text-primary);
}

/* Roadmap Visualizer */
.roadmap-timeline {
  position: relative;
  max-width: 800px;
  margin: 2rem auto;
  padding-left: 2rem;
  border-left: 2px dashed var(--glass-border);
}

.roadmap-step {
  position: relative;
  margin-bottom: 3rem;
  padding: 1.5rem 2rem;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1rem;
}

.roadmap-step::before {
  content: '';
  position: absolute;
  left: -2.6rem;
  top: 1.8rem;
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: var(--color-primary);
  border: 4px solid var(--bg-primary);
  box-shadow: 0 0 10px var(--color-primary);
}

.roadmap-step h4 {
  font-family: var(--font-heading);
  font-size: 1.2rem;
  color: var(--color-secondary);
  margin-bottom: 0.75rem;
}

.roadmap-step ul {
  list-style: none;
}

.roadmap-step li {
  position: relative;
  padding-left: 1.25rem;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.roadmap-step li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--color-success);
}

/* Accordion for literature review */
.accordion {
  margin-top: 2rem;
}

.accordion-item {
  border: 1px solid var(--glass-border);
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  overflow: hidden;
  background: var(--glass-bg);
}

.accordion-header {
  padding: 1.25rem 1.5rem;
  font-weight: 600;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.3s ease;
}

.accordion-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.accordion-content {
  padding: 0;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
}

.accordion-content.open {
  padding: 1.5rem;
  max-height: 1000px;
  border-top: 1px solid var(--glass-border);
}

/* Footer */
footer {
  border-top: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  padding: 2.5rem 0;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}

footer p {
  color: var(--text-muted);
}

```

---

## File: `public/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CloudIT - Enhancing Small Business Efficiency</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <section class="hero">
      <h1>Enhancing Small Business Efficiency through Cloud Solutions</h1>
      <p>Transform your small enterprise with scalable, cost-effective, and secure cloud integration. Evaluate IaaS, PaaS, and SaaS, calculate your ROI, and build a tailored integration roadmap today.</p>
      <div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
        <a href="assessment.html" class="btn btn-primary"><i class="fa-solid fa-clipboard-question"></i> Take Cloud Assessment</a>
        <a href="calculator.html" class="btn btn-secondary"><i class="fa-solid fa-calculator"></i> Calculate Cost Savings</a>
      </div>
    </section>

    <h2 style="text-align: center; margin-bottom: 1rem;">Project Objectives</h2>
    <p style="text-align: center; max-width: 700px; margin: 0 auto 3rem; color: var(--text-secondary);">
      Understanding and evaluating the operational benefits, economic impacts, and adoption challenges of cloud technologies for small business agility.
    </p>

    <div class="card-grid">
      <div class="card">
        <div class="card-icon"><i class="fa-solid fa-sliders"></i></div>
        <h3>Evaluate Cloud Types</h3>
        <p>Analyze differences between Infrastructure (IaaS), Platform (PaaS), and Software (SaaS) structures to fit core operations.</p>
      </div>
      <div class="card">
        <div class="card-icon"><i class="fa-solid fa-chart-line"></i></div>
        <h3>Analyze Cost & Safety</h3>
        <p>Calculate overall cost-effectiveness, risk parameters, flexibility advantages, and disaster recovery reliability.</p>
      </div>
      <div class="card">
        <div class="card-icon"><i class="fa-solid fa-road"></i></div>
        <h3>Custom Integration Roadmap</h3>
        <p>Design a structured implementation framework custom-fitted to your budget, scale, and digital maturity.</p>
      </div>
    </div>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
      <p style="font-size: 0.75rem;">Developed for business digitalization research & implementation roadmap planning.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
</body>
</html>

```

---

## File: `public/comparison.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Service Comparison - CloudIT</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <div style="margin-bottom: 3rem; text-align: center;">
      <h2>Evaluating Cloud Service Models</h2>
      <p style="max-width: 700px; margin: 0 auto;">Different business needs call for different levels of control, management, and flexibility. Learn which model matches your company's operational profile.</p>
    </div>

    <div class="comp-tabs">
      <button class="tab-btn active" data-tab="saas">SaaS (Software as a Service)</button>
      <button class="tab-btn" data-tab="paas">PaaS (Platform as a Service)</button>
      <button class="tab-btn" data-tab="iaas">IaaS (Infrastructure as a Service)</button>
    </div>

    <div class="tab-content">
      <!-- SaaS -->
      <div id="saas" class="tab-pane active">
        <h3>Software as a Service (SaaS)</h3>
        <p style="margin-bottom: 1.5rem;">Fully managed software applications accessible over the web. Perfect for general business functions where custom programming is not required.</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
          <div>
            <h4 style="color: var(--color-secondary); margin-bottom: 0.5rem;">Key Benefits for Small Business</h4>
            <ul style="padding-left: 1.2rem; margin-bottom: 1rem;">
              <li>Zero installation or infrastructure setup.</li>
              <li>Subscription-based billing (Opex instead of Capex).</li>
              <li>Vendor handles updates, security patches, and backups automatically.</li>
            </ul>
          </div>
          <div>
            <h4 style="color: var(--color-secondary); margin-bottom: 0.5rem;">Common Examples</h4>
            <p>Google Workspace, Microsoft 365, QuickBooks Online, Zoho Suite, Slack, Salesforce.</p>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Business Function</th>
              <th>SaaS Tool</th>
              <th>Efficiency Improvement</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Communication & Team Collab</td>
              <td>Google Workspace / Teams</td>
              <td>Real-time document co-authoring, reduced internal emails, unified video conferencing.</td>
            </tr>
            <tr>
              <td>Accounting & Finance</td>
              <td>QuickBooks Online / Zoho Books</td>
              <td>Automated invoice tracking, receipt scanning, and instantly updated bank reconciliation.</td>
            </tr>
            <tr>
              <td>CRM & Customer Support</td>
              <td>Zoho CRM / Salesforce Essentials</td>
              <td>Centralized customer histories, automated follow-ups, and customer pipeline forecasting.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- PaaS -->
      <div id="paas" class="tab-pane">
        <h3>Platform as a Service (PaaS)</h3>
        <p style="margin-bottom: 1.5rem;">Provides a cloud environment to build, deploy, and manage custom applications without worrying about OS management, networking, or servers.</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
          <div>
            <h4 style="color: var(--color-secondary); margin-bottom: 0.5rem;">Key Benefits for Small Business</h4>
            <ul style="padding-left: 1.2rem; margin-bottom: 1rem;">
              <li>Allows developers to focus strictly on coding application logic.</li>
              <li>Built-in scaling mechanisms to handle spikes in customer usage.</li>
              <li>Reduces development complexity and time-to-market.</li>
            </ul>
          </div>
          <div>
            <h4 style="color: var(--color-secondary); margin-bottom: 0.5rem;">Common Examples</h4>
            <p>Heroku, Render, AWS Elastic Beanstalk, Google App Engine.</p>
          </div>
        </div>
      </div>

      <!-- IaaS -->
      <div id="iaas" class="tab-pane">
        <h3>Infrastructure as a Service (IaaS)</h3>
        <p style="margin-bottom: 1.5rem;">Provides virtualized computing resources (servers, storage, firewalls, and networks) over the internet. You have complete control over OS configurations and databases.</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
          <div>
            <h4 style="color: var(--color-secondary); margin-bottom: 0.5rem;">Key Benefits for Small Business</h4>
            <ul style="padding-left: 1.2rem; margin-bottom: 1rem;">
              <li>Highest level of control and configuration flexibility.</li>
              <li>Ability to run legacy desktop software in secure cloud environments (e.g., Windows VMs).</li>
              <li>Only pay for exact raw compute/hour resources used.</li>
            </ul>
          </div>
          <div>
            <h4 style="color: var(--color-secondary); margin-bottom: 0.5rem;">Common Examples</h4>
            <p>Amazon Web Services (AWS EC2/S3), Microsoft Azure, Google Cloud Engine, DigitalOcean.</p>
          </div>
        </div>
      </div>
    </div>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
</body>
</html>

```

---

## File: `public/calculator.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ROI Calculator - CloudIT</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <div style="margin-bottom: 3rem; text-align: center;">
      <h2>On-Premises vs. Cloud ROI Calculator</h2>
      <p style="max-width: 700px; margin: 0 auto;">Estimate potential cost savings over 3 years. Drag the sliders below to reflect your current physical server costs versus planned cloud subscription models.</p>
    </div>

    <div class="calculator-layout">
      <!-- Input Controls -->
      <div class="calc-panel">
        <h3>Operational Variables</h3>
        <p style="margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--text-muted);">Adjust variables to calculate cumulative infrastructure budgets.</p>

        <div class="control-group">
          <label for="calc-onprem-hardware">On-Premises Server Purchase (One-time) <span id="val-onprem-hardware">$5,000</span></label>
          <input type="range" id="calc-onprem-hardware" class="slider-input" min="0" max="30000" step="500" value="5000">
        </div>

        <div class="control-group">
          <label for="calc-onprem-maint">Annual IT Support & Maintenance <span id="val-onprem-maint">$2,000</span></label>
          <input type="range" id="calc-onprem-maint" class="slider-input" min="0" max="15000" step="250" value="2000">
        </div>

        <div class="control-group">
          <label for="calc-downtime-cost">Estimated Annual Outage Loss <span id="val-downtime-cost">$1,500</span></label>
          <input type="range" id="calc-downtime-cost" class="slider-input" min="0" max="10000" step="100" value="1500">
        </div>

        <div class="control-group">
          <label for="calc-cloud-sub">Target Cloud Subscriptions (Monthly) <span id="val-cloud-sub">$150</span></label>
          <input type="range" id="calc-cloud-sub" class="slider-input" min="10" max="1500" step="10" value="150">
        </div>
      </div>

      <!-- Live Calculations & Chart -->
      <div class="chart-panel">
        <h3>3-Year Financial Comparison</h3>
        <div style="flex-grow: 1; margin: 1.5rem 0; min-height: 250px;">
          <canvas id="roiChart"></canvas>
        </div>
        
        <div class="metric-grid">
          <div class="metric-card">
            <div class="metric-value" id="metric-onprem-total">$15,500</div>
            <div class="metric-label">Total On-Premises</div>
          </div>
          <div class="metric-card">
            <div class="metric-value" id="metric-cloud-total">$6,150</div>
            <div class="metric-label">Total Cloud Cost</div>
          </div>
          <div class="metric-card" style="grid-column: span 2; background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.2);">
            <div class="metric-value savings" id="metric-savings-net">+$9,350</div>
            <div class="metric-label" style="color: var(--color-success);">Net Cost Savings</div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
</body>
</html>

```

---

## File: `public/assessment.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cloud Assessment - CloudIT</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <div style="margin-bottom: 3rem; text-align: center;">
      <h2>Interactive Cloud Readiness Assessment</h2>
      <p style="max-width: 700px; margin: 0 auto;">Determine your organization's cloud suitability. Submit your current operations, pain points, and technical background to build a tailored cloud integration roadmap.</p>
    </div>

    <section class="form-section">
      <form id="cloud-assessment-form">
        <!-- Business Profile -->
        <h3 style="border-bottom: 1px solid var(--glass-border); padding-bottom: 0.5rem; margin-bottom: 1.5rem; color: var(--color-secondary);">1. Business Profile</h3>
        
        <div class="form-group">
          <label for="biz-name">Business Name</label>
          <input type="text" id="biz-name" class="input-text" placeholder="e.g. Acme Retailers" required>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
          <div class="form-group">
            <label for="biz-industry">Industry Sector</label>
            <select id="biz-industry" required>
              <option value="">Select industry...</option>
              <option value="retail">Retail & E-commerce</option>
              <option value="professional">Professional Services (Consulting, Law, etc)</option>
              <option value="manufacturing">Manufacturing & Logistics</option>
              <option value="healthcare">Healthcare & Medical</option>
              <option value="education">Education & Non-Profit</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="biz-size">Number of Employees</label>
            <select id="biz-size" required>
              <option value="micro">Micro (1-9 employees)</option>
              <option value="small" selected>Small (10-49 employees)</option>
              <option value="medium">Medium (50-249 employees)</option>
            </select>
          </div>
        </div>

        <!-- Tech Maturity -->
        <h3 style="border-bottom: 1px solid var(--glass-border); padding-bottom: 0.5rem; margin-bottom: 1.5rem; color: var(--color-secondary);">2. Technical Maturity & Budget</h3>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
          <div class="form-group">
            <label for="biz-budget">Monthly Cloud Budget Range</label>
            <select id="biz-budget" required>
              <option value="low">Low (Under $200/month)</option>
              <option value="medium" selected>Moderate ($200 - $1,000/month)</option>
              <option value="high">High ($1,000+/month)</option>
            </select>
          </div>

          <div class="form-group">
            <label for="biz-tech">Internal Technical Expertise</label>
            <select id="biz-tech" required>
              <option value="low">Low (Non-technical staff only)</option>
              <option value="medium" selected>Moderate (Some IT/Admin experience)</option>
              <option value="high">High (Dedicated IT Staff / Developers)</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="biz-security">Data Security & Compliance Requirement Level</label>
          <select id="biz-security" required>
            <option value="standard">Standard (General data protection)</option>
            <option value="critical">Critical (Financial data, health files, strict privacy policies)</option>
          </select>
        </div>

        <!-- Infrastructure State -->
        <h3 style="border-bottom: 1px solid var(--glass-border); padding-bottom: 0.5rem; margin-bottom: 1.5rem; color: var(--color-secondary);">3. Current Systems & Operational Pain Points</h3>

        <div class="form-group">
          <label>Common Legacy Systems Used (Select all that apply)</label>
          <div class="options-grid">
            <div class="option-card">
              <input type="checkbox" id="tool-excel" name="current-tools" value="excel">
              <label for="tool-excel" class="option-label">Offline Excel / Word</label>
            </div>
            <div class="option-card">
              <input type="checkbox" id="tool-server" name="current-tools" value="server">
              <label for="tool-server" class="option-label">On-Premises Local Server</label>
            </div>
            <div class="option-card">
              <input type="checkbox" id="tool-paper" name="current-tools" value="paper">
              <label for="tool-paper" class="option-label">Paper records / files</label>
            </div>
            <div class="option-card">
              <input type="checkbox" id="tool-basic-hosting" name="current-tools" value="basic-hosting">
              <label for="tool-basic-hosting" class="option-label">Shared Shared Web Hosting</label>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Target Business Pain Points (Select all that apply)</label>
          <div class="options-grid">
            <div class="option-card">
              <input type="checkbox" id="pain-collaboration" name="pain-points" value="collaboration">
              <label for="pain-collaboration" class="option-label">Poor Collaboration / Remote Work</label>
            </div>
            <div class="option-card">
              <input type="checkbox" id="pain-accounting" name="pain-points" value="accounting">
              <label for="pain-accounting" class="option-label">Manual Accounting & Invoicing</label>
            </div>
            <div class="option-card">
              <input type="checkbox" id="pain-crm" name="pain-points" value="crm">
              <label for="pain-crm" class="option-label">Customer tracking issues</label>
            </div>
            <div class="option-card">
              <input type="checkbox" id="pain-hosting" name="pain-points" value="hosting">
              <label for="pain-hosting" class="option-label">Unreliable local app hosting</label>
            </div>
          </div>
        </div>

        <div style="text-align: center; margin-top: 3rem;">
          <button type="submit" class="btn btn-primary" style="width: 100%; max-width: 300px;"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate Custom Roadmap</button>
        </div>
      </form>
    </section>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
</body>
</html>

```

---

## File: `public/roadmap.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Integration Roadmap - CloudIT</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <div id="roadmap-container" style="max-width: 900px; margin: 0 auto;">
      <!-- JavaScript will load dynamic content here -->
      <div style="text-align: center; padding: 4rem 0;">
        <i class="fa-solid fa-spinner fa-spin" style="font-size: 3rem; color: var(--color-primary); margin-bottom: 1.5rem;"></i>
        <p>Generating your custom cloud integration roadmap...</p>
      </div>
    </div>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      if (typeof window.renderRoadmap === 'function') {
        window.renderRoadmap();
      }
    });
  </script>
</body>
</html>

```

---

## File: `public/case-studies.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Case Studies - CloudIT</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <div style="margin-bottom: 3rem; text-align: center;">
      <h2>Small Business Cloud Adoption Case Studies</h2>
      <p style="max-width: 700px; margin: 0 auto;">See how other small businesses restructured their operations, saved capital, and boosted team output using tailored cloud-based tools.</p>
    </div>

    <div class="card-grid">
      <!-- Case Study 1 -->
      <div class="card">
        <div class="card-icon" style="color: var(--color-secondary);"><i class="fa-solid fa-store"></i></div>
        <h3>The Daily Olive Deli</h3>
        <p style="margin-bottom: 1rem;"><strong>Profile:</strong> Specialty gourmet deli with three physical shop locations.</p>
        
        <h4 style="color: var(--color-primary); font-size: 0.95rem; margin-bottom: 0.25rem;">Before Cloud:</h4>
        <p style="font-size: 0.85rem; margin-bottom: 0.75rem;">Used hand-written daybooks and manual spreadsheet updates for stock counts once a week, leading to frequent inventory shortages on high-margin ingredients.</p>
        
        <h4 style="color: var(--color-success); font-size: 0.95rem; margin-bottom: 0.25rem;">After Cloud (SaaS integration):</h4>
        <p style="font-size: 0.85rem; margin-bottom: 1rem;">Transitioned to Shopify POS synced with a unified QuickBooks Online catalog. Real-time automatic inventory tracking across all storefronts.</p>
        
        <div class="metric-card" style="background: rgba(16, 185, 129, 0.05); padding: 0.75rem;">
          <div class="metric-value" style="font-size: 1.25rem; color: var(--color-success);">+24% Sales Revenue</div>
          <p style="font-size: 0.75rem; color: var(--text-muted);">from eliminated out-of-stock events & live stock monitoring</p>
        </div>
      </div>

      <!-- Case Study 2 -->
      <div class="card">
        <div class="card-icon" style="color: var(--color-accent);"><i class="fa-solid fa-user-tie"></i></div>
        <h3>M&R Legal Advisory</h3>
        <p style="margin-bottom: 1rem;"><strong>Profile:</strong> Local real estate law and conveyancing partnership with 12 associates.</p>
        
        <h4 style="color: var(--color-primary); font-size: 0.95rem; margin-bottom: 0.25rem;">Before Cloud:</h4>
        <p style="font-size: 0.85rem; margin-bottom: 0.75rem;">Local NAS drive server kept in-office. Slow VPN connectivity for remote staff led to duplicate drafts and document version confusion.</p>
        
        <h4 style="color: var(--color-success); font-size: 0.95rem; margin-bottom: 0.25rem;">After Cloud (SaaS Productivity):</h4>
        <p style="font-size: 0.85rem; margin-bottom: 1rem;">Adopted Microsoft 365 SharePoint Online with unified co-authoring tools and standardized remote client portals.</p>
        
        <div class="metric-card" style="background: rgba(16, 185, 129, 0.05); padding: 0.75rem;">
          <div class="metric-value" style="font-size: 1.25rem; color: var(--color-success);">-14 hours/week</div>
          <p style="font-size: 0.75rem; color: var(--text-muted);">saved per staff member on contract draft reviews</p>
        </div>
      </div>

      <!-- Case Study 3 -->
      <div class="card">
        <div class="card-icon" style="color: var(--color-primary);"><i class="fa-solid fa-industry"></i></div>
        <h3>Apex Steel Works</h3>
        <p style="margin-bottom: 1rem;"><strong>Profile:</strong> Independent steel frame fabrication workshop, 30 workers.</p>
        
        <h4 style="color: var(--color-primary); font-size: 0.95rem; margin-bottom: 0.25rem;">Before Cloud:</h4>
        <p style="font-size: 0.85rem; margin-bottom: 0.75rem;">CAD blueprint files stored on individual hard drives. High risk of data loss from local disk failure and manual file transfers.</p>
        
        <h4 style="color: var(--color-success); font-size: 0.95rem; margin-bottom: 0.25rem;">After Cloud (IaaS & PaaS):</h4>
        <p style="font-size: 0.85rem; margin-bottom: 1rem;">AWS S3 integrated storage with client access portal, paired with automated daily server image backup policies.</p>
        
        <div class="metric-card" style="background: rgba(16, 185, 129, 0.05); padding: 0.75rem;">
          <div class="metric-value" style="font-size: 1.25rem; color: var(--color-success);">99.99% Availability</div>
          <p style="font-size: 0.75rem; color: var(--text-muted);">blueprint recovery speed increased from hours to seconds</p>
        </div>
      </div>
    </div>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
</body>
</html>

```

---

## File: `public/literature.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Literature & Challenges - CloudIT</title>
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="index.html" class="logo">
        <i class="fa-solid fa-cloud"></i> Cloud<span>IT</span>
      </a>
      <nav>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="comparison.html">Services</a></li>
          <li><a href="calculator.html">Cost ROI</a></li>
          <li><a href="assessment.html">Assessment</a></li>
          <li><a href="case-studies.html">Case Studies</a></li>
          <li><a href="literature.html">Literature</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main style="max-width: 900px;">
    <div style="margin-bottom: 3rem; text-align: center;">
      <h2>Cloud Computing Literature & Adoption Barriers</h2>
      <p>Research findings, data privacy, and mitigation strategies for small businesses undergoing digital transformation.</p>
    </div>

    <div class="accordion">
      <!-- Section 1 -->
      <div class="accordion-item">
        <div class="accordion-header">
          <span>1. Literature Review: Cloud Computing & Business Agility</span>
          <i class="fa-solid fa-chevron-down"></i>
        </div>
        <div class="accordion-content">
          <p style="margin-bottom: 1rem;">Research by <em>Mell and Grance (2011)</em> from the National Institute of Standards and Technology (NIST) describes cloud computing through key characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity, and measured service. In the context of small and medium enterprises (SMEs), these characteristics drive <strong>operational efficiency</strong> and <strong>flexibility</strong> (Alshamaila et al., 2013). By moving infrastructure expenditures from upfront capital investments (CapEx) to modular operational costs (OpEx), small businesses can implement high-grade software tools without large budgets.</p>
          <p style="margin-bottom: 1rem;"><strong>Agility and Collaborative Workspace:</strong> Real-time co-authoring tools like Google Workspace or Microsoft 365 shift workflows from isolated file versions to single-source documents. Studies show collaborative cloud adoption significantly reduces email traffic, saving time during project delivery (Oliveira et al., 2014).</p>
          <p><strong>Digitalization of Admin Workloads:</strong> Moving manual accounting ledger entries or client tracking lists into cloud-hosted platforms helps eliminate reporting delays, providing management with real-time analytics to make immediate business decisions.</p>
        </div>
      </div>

      <!-- Section 2 -->
      <div class="accordion-item">
        <div class="accordion-header">
          <span>2. Core Barriers to Small Business Adoption</span>
          <i class="fa-solid fa-chevron-down"></i>
        </div>
        <div class="accordion-content">
          <p style="margin-bottom: 1rem;">According to studies on SME technology diffusion (e.g., <em>MacGregor and Vrazalic, 2005</em>), smaller companies face unique friction points compared to large enterprises:</p>
          <ul style="padding-left: 1.5rem; margin-bottom: 1rem;">
            <li style="margin-bottom: 0.5rem;"><strong>Financial Vulnerability:</strong> While upfront setup is cheap, subscription costs can accumulate rapidly if licenses are unmanaged, a phenomenon often described as "cloud cost creep."</li>
            <li style="margin-bottom: 0.5rem;"><strong>Information Privacy Concerns:</strong> Many business owners hesitate to transfer proprietary records to public cloud data centers due to perceived risks of data leaks or compliance violations (Subashini & Kavitha, 2011).</li>
            <li style="margin-bottom: 0.5rem;"><strong>Skills Gap:</strong> Lacking dedicated internal IT personnel, configuring complex access controls, encryption keys, and directory syncs represents a steep learning curve.</li>
            <li style="margin-bottom: 0.5rem;"><strong>Infrastructure Dependability:</strong> Total reliance on cloud hosts exposes operations to disruption during local ISP internet outages.</li>
          </ul>
        </div>
      </div>

      <!-- Section 3 -->
      <div class="accordion-item">
        <div class="accordion-header">
          <span>3. Security, Privacy, and Practical Solutions</span>
          <i class="fa-solid fa-chevron-down"></i>
        </div>
        <div class="accordion-content">
          <p style="margin-bottom: 1rem;">Practical mitigation frameworks help bridge these barriers to enable safe cloud integration:</p>
          
          <h4 style="color: var(--color-secondary); margin-bottom: 0.25rem;">Security Implementations:</h4>
          <p style="margin-bottom: 1rem;">Enforcing Multi-Factor Authentication (MFA) across all identity services blocks up to 99% of automated account attacks. Access should be restricted using Role-Based Access Control (RBAC) to ensure employees only view tools required for their specific role.</p>

          <h4 style="color: var(--color-secondary); margin-bottom: 0.25rem;">Hybrid Sync / Offline Backup:</h4>
          <p style="margin-bottom: 1rem;">Using offline sync controls (e.g., Google Drive Desktop or OneDrive Cache) lets staff continue working during temporary connection drops, auto-merging edits once internet returns.</p>

          <h4 style="color: var(--color-secondary); margin-bottom: 0.25rem;">Cost and Subscription Audits:</h4>
          <p>Schedule a quarterly review of user seats and service tiers to disable unused subscriptions, keeping operating costs within forecast thresholds.</p>
        </div>
      </div>
    </div>
  </main>

  <footer>
    <div class="nav-container" style="flex-direction: column; gap: 1rem;">
      <p>© 2026 CloudIT Project. Enhancing Small Business Efficiency through Cloud-Based IT Solutions.</p>
    </div>
  </footer>

  <script src="js/app.js"></script>
</body>
</html>

```

---

