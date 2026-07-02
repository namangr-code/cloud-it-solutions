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
