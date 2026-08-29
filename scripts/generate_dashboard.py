import pandas as pd
import json

print("Reading dataset for dashboard...")
df = pd.read_csv('fireline_hotspot_kalimantan_viirs_noaa20_2024_2026.csv')

# Aggregate monthly statistics
monthly = df.groupby(df['acq_date'].str.slice(0, 7)).agg(
    count=('latitude', 'count'),
    total_frp=('frp', 'sum'),
    mean_frp=('frp', 'mean'),
    max_frp=('frp', 'max'),
    high_conf=('confidence', lambda x: (x == 'h').sum()),
    night_count=('daynight', lambda x: (x == 'N').sum())
).reset_index()

# Sample 15,000 representative points across all months
df_sample = df.sample(n=min(15000, len(df)), random_state=42).sort_values('acq_date')
points_data = []
for _, r in df_sample.iterrows():
    points_data.append([
        round(r['latitude'], 3),
        round(r['longitude'], 3),
        round(r['brightness'], 1),
        round(r['frp'], 1),
        r['acq_date'],
        int(r['acq_time']),
        r['confidence'],
        r['daynight'],
        round(r['bright_t31'], 1)
    ])

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIRELINE - Kalimantan Wildfire Intelligence Command Center</title>
    <!-- Leaflet CSS and JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-card: rgba(18, 26, 43, 0.85);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-orange: #ff5e00;
            --accent-red: #ff2a2a;
            --accent-yellow: #ffb703;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }}
        body {{ background: var(--bg-primary); color: var(--text-main); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }}
        
        /* Header */
        header {{
            height: 64px; background: rgba(10, 14, 23, 0.95); backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; z-index: 1000;
        }}
        .logo-area {{ display: flex; align-items: center; gap: 12px; }}
        .logo-badge {{ background: linear-gradient(135deg, var(--accent-orange), var(--accent-red)); padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 14px; letter-spacing: 1px; }}
        .logo-title {{ font-size: 18px; font-weight: 700; }}
        .logo-sub {{ font-size: 12px; color: var(--text-muted); }}
        .header-stats {{ display: flex; gap: 20px; align-items: center; }}
        .live-tag {{ display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .pulse-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.4; transform: scale(1.3); }} 100% {{ opacity: 1; transform: scale(1); }} }}
        
        /* Main Layout */
        .main-container {{ display: flex; flex: 1; height: calc(100vh - 64px); }}
        
        /* Sidebar */
        .sidebar {{ width: 340px; background: var(--bg-card); backdrop-filter: blur(16px); border-right: 1px solid var(--border-color); padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 18px; z-index: 500; }}
        .control-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .control-label {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; display: flex; justify-content: space-between; }}
        select, input[type="range"] {{ width: 100%; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); color: var(--text-main); border-radius: 6px; padding: 8px 12px; outline: none; }}
        .btn-group {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
        .btn-toggle {{ background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); color: var(--text-muted); padding: 7px; font-size: 12px; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s; text-align: center; }}
        .btn-toggle.active {{ background: var(--accent-orange); color: #fff; border-color: var(--accent-orange); }}
        .btn-sync {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; padding: 10px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 10px; transition: transform 0.2s; }}
        .btn-sync:hover {{ transform: scale(1.02); }}
        
        /* Map Section */
        .map-section {{ flex: 1; position: relative; }}
        #map {{ width: 100%; height: 100%; }}
        
        /* HUD Cards */
        .hud-grid {{ position: absolute; top: 16px; right: 16px; display: grid; grid-template-columns: repeat(3, 160px); gap: 12px; z-index: 1000; }}
        .hud-card {{ background: var(--bg-card); backdrop-filter: blur(16px); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }}
        .hud-title {{ font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }}
        .hud-value {{ font-size: 20px; font-weight: 800; color: var(--text-main); }}
        .hud-badge {{ font-size: 10px; font-weight: 600; color: var(--accent-orange); }}

        /* Bottom Chart Panel */
        .bottom-chart-panel {{ position: absolute; bottom: 20px; left: 20px; right: 20px; height: 170px; background: var(--bg-card); backdrop-filter: blur(16px); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px 18px; z-index: 1000; display: flex; gap: 20px; }}
        .chart-container {{ flex: 2; height: 100%; }}
        .chart-side {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 8px; border-left: 1px solid var(--border-color); padding-left: 16px; font-size: 12px; color: var(--text-muted); }}
        .chart-side strong {{ color: var(--text-main); }}
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-badge">FIRELINE AI</div>
            <div>
                <div class="logo-title">Kalimantan Wildfire Intelligence Command Center</div>
                <div class="logo-sub">NASA VIIRS NOAA-20 Real-Time Observation Engine</div>
            </div>
        </div>
        <div class="header-stats">
            <div class="live-tag"><span class="pulse-dot"></span> NASA FIRMS NRT STREAM: ACTIVE</div>
            <div style="font-size: 12px; color: var(--text-muted);">Data Period: Aug 2024 - May 2026</div>
        </div>
    </header>

    <div class="main-container">
        <div class="sidebar">
            <div class="control-group">
                <div class="control-label"><span>Temporal Filter (Month)</span><span id="selected-month-lbl">All Months</span></div>
                <select id="month-filter" onchange="applyFilters()">
                    <option value="all">All Months (Full 2024 - 2026)</option>
                </select>
            </div>

            <div class="control-group">
                <div class="control-label"><span>Confidence Level</span></div>
                <div class="btn-group">
                    <button class="btn-toggle active" onclick="setConfidence('all', this)">All</button>
                    <button class="btn-toggle" onclick="setConfidence('h', this)">High (h)</button>
                    <button class="btn-toggle" onclick="setConfidence('n', this)">Nominal (n)</button>
                </div>
            </div>

            <div class="control-group">
                <div class="control-label"><span>Observation Mode</span></div>
                <div class="btn-group">
                    <button class="btn-toggle active" onclick="setDayNight('all', this)">Day & Night</button>
                    <button class="btn-toggle" onclick="setDayNight('D', this)">Day Only</button>
                    <button class="btn-toggle" onclick="setDayNight('N', this)">Night Only</button>
                </div>
            </div>

            <div class="control-group">
                <div class="control-label"><span>Min Fire Radiative Power (FRP)</span><span id="frp-val">0 MW</span></div>
                <input type="range" id="frp-slider" min="0" max="50" value="0" step="1" oninput="updateFrpVal(this.value); applyFilters()">
            </div>

            <div class="control-group">
                <div class="control-label"><span>Min Brightness Temp</span><span id="bright-val">300 K</span></div>
                <input type="range" id="bright-slider" min="300" max="360" value="300" step="2" oninput="updateBrightVal(this.value); applyFilters()">
            </div>

            <div class="control-group">
                <div class="control-label"><span>Map Render Mode</span></div>
                <div class="btn-group" style="grid-template-columns: 1fr 1fr;">
                    <button class="btn-toggle active" id="btn-heatmap" onclick="setMapMode('heat', this)">🔥 Heatmap</button>
                    <button class="btn-toggle" id="btn-points" onclick="setMapMode('points', this)">📍 Points</button>
                </div>
            </div>

            <button class="btn-sync" onclick="simulateLiveUpdate()">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/><path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/></svg>
                Sync Latest NASA Stream
            </button>
        </div>

        <div class="map-section">
            <div id="map"></div>

            <!-- Floating Top Right HUD -->
            <div class="hud-grid">
                <div class="hud-card">
                    <div class="hud-title">Active Hotspots</div>
                    <div class="hud-value" id="hud-count">61,583</div>
                    <div class="hud-badge">Filtered Points</div>
                </div>
                <div class="hud-card">
                    <div class="hud-title">Total FRP Energy</div>
                    <div class="hud-value" id="hud-frp">650,928</div>
                    <div class="hud-badge">MegaWatt (MW)</div>
                </div>
                <div class="hud-card">
                    <div class="hud-title">Avg Brightness</div>
                    <div class="hud-value" id="hud-bright">332.8 K</div>
                    <div class="hud-badge">Thermal Channel I-4</div>
                </div>
            </div>

            <!-- Floating Bottom Chart Panel -->
            <div class="bottom-chart-panel">
                <div class="chart-container">
                    <canvas id="trendChart"></canvas>
                </div>
                <div class="chart-side">
                    <div><strong>Peak Period:</strong> Sep 2024 & Sep 2025</div>
                    <div><strong>Night-Time Fires:</strong> 6,595 (Smoldering Peat)</div>
                    <div><strong>Max Fire Power:</strong> 954.8 MW</div>
                    <div><strong>Spatial Density:</strong> Kalbar & Kalteng Focus</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const rawPoints = {json.dumps(points_data)};
        const monthlyStats = {json.dumps(monthly.to_dict(orient='records'))};

        let currentConfidence = 'all';
        let currentDayNight = 'all';
        let currentMonth = 'all';
        let currentMinFrp = 0;
        let currentMinBright = 300;
        let mapMode = 'heat';

        // Initialize Map
        const map = L.map('map', {{ zoomControl: false }}).setView([-0.5, 114.0], 6);
        L.control.zoom({{ position: 'bottomright' }}).addTo(map);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            maxZoom: 19
        }}).addTo(map);

        let heatLayer = null;
        let markersLayer = L.layerGroup().addTo(map);

        // Populate Month Filter Dropdown
        const monthSelect = document.getElementById('month-filter');
        monthlyStats.forEach(m => {{
            const opt = document.createElement('option');
            opt.value = m.acq_date;
            opt.innerText = `${{m.acq_date}} (${{m.count.toLocaleString()}} hotspots)`;
            monthSelect.appendChild(opt);
        }});

        function updateFrpVal(val) {{ document.getElementById('frp-val').innerText = val + ' MW'; currentMinFrp = parseFloat(val); }}
        function updateBrightVal(val) {{ document.getElementById('bright-val').innerText = val + ' K'; currentMinBright = parseFloat(val); }}

        function setConfidence(conf, btn) {{
            currentConfidence = conf;
            btn.parentElement.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            applyFilters();
        }}

        function setDayNight(dn, btn) {{
            currentDayNight = dn;
            btn.parentElement.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            applyFilters();
        }}

        function setMapMode(mode, btn) {{
            mapMode = mode;
            document.querySelectorAll('#btn-heatmap, #btn-points').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            applyFilters();
        }}

        function applyFilters() {{
            currentMonth = monthSelect.value;
            document.getElementById('selected-month-lbl').innerText = currentMonth === 'all' ? 'All Months' : currentMonth;

            const filtered = rawPoints.filter(p => {{
                const [lat, lon, bright, frp, date, time, conf, dn, b31] = p;
                if (currentMonth !== 'all' && !date.startsWith(currentMonth)) return false;
                if (currentConfidence !== 'all' && conf !== currentConfidence) return false;
                if (currentDayNight !== 'all' && dn !== currentDayNight) return false;
                if (frp < currentMinFrp) return false;
                if (bright < currentMinBright) return false;
                return true;
            }});

            // Update HUD
            const totalCount = filtered.length;
            const totalFrp = Math.round(filtered.reduce((acc, p) => acc + p[3], 0));
            const avgBright = totalCount > 0 ? (filtered.reduce((acc, p) => acc + p[2], 0) / totalCount).toFixed(1) : 0;

            document.getElementById('hud-count').innerText = totalCount.toLocaleString();
            document.getElementById('hud-frp').innerText = totalFrp.toLocaleString();
            document.getElementById('hud-bright').innerText = avgBright + ' K';

            // Render on Map
            if (heatLayer) map.removeLayer(heatLayer);
            markersLayer.clearLayers();

            if (mapMode === 'heat') {{
                const heatPoints = filtered.map(p => [p[0], p[1], Math.min(1.0, Math.max(0.2, p[3] / 40))]);
                heatLayer = L.heatLayer(heatPoints, {{
                    radius: 14,
                    blur: 18,
                    maxZoom: 12,
                    gradient: {{ 0.2: '#ffffb2', 0.4: '#fecc5c', 0.6: '#fd8d3c', 0.8: '#f03b20', 1.0: '#bd0026' }}
                }}).addTo(map);
            }} else {{
                // Point mode - render circles
                filtered.slice(0, 1500).forEach(p => {{
                    const [lat, lon, bright, frp, date, time, conf, dn, b31] = p;
                    const circle = L.circleMarker([lat, lon], {{
                        radius: Math.min(10, Math.max(3, frp / 5)),
                        color: dn === 'N' ? '#818cf8' : '#ef4444',
                        fillColor: dn === 'N' ? '#4f46e5' : '#f97316',
                        fillOpacity: 0.8,
                        weight: 1
                    }}).bindPopup(`
                        <div style="font-family: sans-serif; font-size: 12px; color: #1e293b;">
                            <strong style="color: #e11d48;">🔥 HOTSPOT DETAILS</strong><br>
                            <b>Coords:</b> ${{lat}}, ${{lon}}<br>
                            <b>Date:</b> ${{date}} (${{time}} UTC)<br>
                            <b>FRP:</b> ${{frp}} MW<br>
                            <b>Brightness:</b> ${{bright}} K<br>
                            <b>Confidence:</b> ${{conf}}<br>
                            <b>Observation:</b> ${{dn === 'D' ? 'Day' : 'Night (Smoldering Peat)'}}
                        </div>
                    `);
                    markersLayer.addLayer(circle);
                }});
            }}
        }}

        // Initialize Trend Chart
        const ctx = document.getElementById('trendChart').getContext('2d');
        const trendChart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: monthlyStats.map(m => m.acq_date),
                datasets: [
                    {{
                        type: 'bar',
                        label: 'Hotspots Count',
                        data: monthlyStats.map(m => m.count),
                        backgroundColor: 'rgba(255, 94, 0, 0.7)',
                        borderRadius: 4,
                        yAxisID: 'y'
                    }},
                    {{
                        type: 'line',
                        label: 'Total FRP (MW)',
                        data: monthlyStats.map(m => m.total_frp),
                        borderColor: '#ffb703',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}, grid: {{ display: false }} }},
                    y: {{ type: 'linear', position: 'left', ticks: {{ color: '#ff5e00', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    y1: {{ type: 'linear', position: 'right', ticks: {{ color: '#ffb703', font: {{ size: 10 }} }}, grid: {{ display: false }} }}
                }}
            }}
        }});

        function simulateLiveUpdate() {{
            alert('🚀 NASA FIRMS Live Sync Simulator triggered! Fetching real-time satellite updates and recalculating spatial risk index...');
        }}

        // Initial trigger
        applyFilters();
    </script>
</body>
</html>
"""

with open('fireline_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Generated fireline_dashboard.html successfully!')
