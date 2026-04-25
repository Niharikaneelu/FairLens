document.addEventListener("DOMContentLoaded", () => {
  console.log("FairLens frontend loaded.");

  // Initialize Chart.js
  const chartDataEl = document.getElementById("chartData");
  if (chartDataEl) {
    const data = JSON.parse(chartDataEl.textContent);
    const ctx = document.getElementById('biasChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: Object.keys(data),
        datasets: [{
          label: 'Selection Rate (%)',
          data: Object.values(data),
          backgroundColor: '#818CF8',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: '#94A3B8' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#94A3B8' }
          }
        }
      }
    });
  }
});
function sendQuestion() {
  const question = document.getElementById("question").value.trim();
  const askBtn = document.getElementById("askBtn");
  const chatResponse = document.getElementById("chatResponse");

  if (!question) return;

  askBtn.disabled = true;
  askBtn.innerHTML = '<span style="display:inline-block;width:12px;height:12px;border:2px solid rgba(165,180,252,0.3);border-top-color:#A5B4FC;border-radius:50%;animation:spin 0.7s linear infinite;vertical-align:middle;margin-right:6px;"></span> Thinking...';
  chatResponse.className = '';
  chatResponse.innerText = "";

  fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  })
    .then(res => res.json())
    .then(data => {
      chatResponse.innerText = data.reply;
      chatResponse.className = 'active';
      askBtn.disabled = false;
      askBtn.innerHTML = '🤖 Ask AI';
    })
    .catch(() => {
      chatResponse.innerText = "Error contacting server.";
      askBtn.disabled = false;
      askBtn.innerHTML = '🤖 Ask AI';
    });
}

function downloadPDF() {
  const chartDataEl = document.getElementById("chartData");
  let data = {};
  if (chartDataEl) {
    data = JSON.parse(chartDataEl.textContent);
  }

  const metricCards = document.querySelectorAll('.metric-card');
  let biasGap = '';
  let disparateImpact = '';

  metricCards.forEach(card => {
    const label = card.querySelector('.metric-label').textContent.toLowerCase();
    const value = card.querySelector('.metric-value').textContent;
    if (label.includes("bias gap")) biasGap = value;
    if (label.includes("disparate impact")) disparateImpact = value;
  });

  const biasStatus = document.querySelector('.alert-title').innerText;
  const aiExplanation = document.querySelector('.markdown-content').innerText;

  let reportHtml = `
    <html>
    <head><title>FairLens Audit Report</title>
    <style>
      body { font-family: 'Outfit', 'Inter', sans-serif; padding: 2rem; color: #111827; background: #F8FAFC; }
      h1 { color: #312E81; border-bottom: 2px solid #818CF8; padding-bottom: 0.5rem; }
      .report-card { background: white; border-radius: 16px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
      .status { font-size: 1.5rem; font-weight: 700; color: #4338CA; margin-bottom: 1rem; }
      table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
      th { background: #4F46E5; color: white; padding: 12px; text-align: left; }
      td { padding: 12px; border-bottom: 1px solid #E2E8F0; }
      .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 2rem; }
      .metric-box { background: #EEF2FF; padding: 1.5rem; border-radius: 12px; text-align: center; }
      .metric-label { font-size: 1rem; color: #4338CA; font-weight: 600; text-transform: uppercase; }
      .metric-value { font-size: 2.5rem; font-weight: 800; color: #EF4444; margin-top: 0.5rem; }
      .ai-insight { white-space: pre-wrap; line-height: 1.6; color: #374151; }
    </style>
    </head>
    <body>
    <h1>📋 FairLens Audit Report</h1>
    <div style="margin-bottom: 2rem; color: #64748B;">Generated on ${new Date().toLocaleString()}</div>
    
    <div class="report-card">
      <div class="status">${biasStatus}</div>
      
      <div class="metrics-grid">
        <div class="metric-box">
          <div class="metric-label">Bias Gap</div>
          <div class="metric-value">${biasGap}</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">Disparate Impact</div>
          <div class="metric-value">${disparateImpact}</div>
        </div>
      </div>

      <h3 style="margin-top: 3rem; color: #312E81;">Selection Rates by Group</h3>
      <table>
        <tr><th>Group</th><th>Selection Rate</th></tr>
        ${Object.keys(data).map(group => `<tr><td>${group}</td><td>${parseFloat(data[group]).toFixed(1)}%</td></tr>`).join('')}
      </table>
    </div>

    <div class="report-card">
      <h3 style="color: #312E81;">AI Insight & Recommendations</h3>
      <div class="ai-insight">${aiExplanation}</div>
    </div>
    </body>
    </html>
  `;

  const printWindow = window.open('', '_blank');
  printWindow.document.write(reportHtml);
  printWindow.document.close();
  setTimeout(() => { printWindow.print(); }, 400);
}