"""
Home page view for KVK Trading System
"""

from django.http import HttpResponse
from django.views import View


class HomeView(View):
    """Welcome page with quick links to all endpoints"""
    
    def get(self, request):
        """Return welcome page with available endpoints"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KVK_8833_PROFIT - Trading System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .status {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 15px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
            margin-top: 15px;
        }
        
        .version {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .quick-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .link-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .link-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        
        .link-card a {
            display: block;
            color: white;
            text-decoration: none;
            padding: 15px 20px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 1.1em;
            transition: background 0.3s;
        }
        
        .link-card .label {
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .api-link a {
            background: #667eea;
        }
        
        .api-link a:hover {
            background: #5568d3;
        }
        
        .health-link a {
            background: #4CAF50;
        }
        
        .health-link a:hover {
            background: #45a049;
        }
        
        .admin-link a {
            background: #FF9800;
        }
        
        .admin-link a:hover {
            background: #e68900;
        }
        
        .docs-link a {
            background: #2196F3;
        }
        
        .docs-link a:hover {
            background: #0b7dda;
        }
        
        .endpoints-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .endpoints-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .endpoints-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .endpoint {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            transition: background 0.3s;
        }
        
        .endpoint:hover {
            background: #e8eaff;
        }
        
        .endpoint-name {
            color: #667eea;
            font-weight: bold;
            font-size: 1.05em;
            margin-bottom: 5px;
        }
        
        .endpoint-desc {
            color: #666;
            font-size: 0.9em;
        }
        
        .features-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .features-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
        }
        
        .feature {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .feature-icon {
            font-size: 2em;
        }
        
        .feature-text {
            font-size: 0.95em;
        }
        
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }
        
        .new-badge {
            display: inline-block;
            background: #FF5722;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.75em;
            margin-left: 5px;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .quick-links {
                grid-template-columns: 1fr;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 KVK_8833_PROFIT</h1>
            <p>Expert AI Trading Assistant & Financial Analysis System</p>
            <div class="status">✓ Running & Ready</div>
            <div class="version">Version 1.0.0 | Django 4.2.8</div>
        </div>
        
        <!-- Quick Links -->
        <div class="quick-links">
            <div class="link-card api-link">
                <div class="label">API Root</div>
                <a href="/api/">Browse All Endpoints →</a>
            </div>
            <div class="link-card health-link">
                <div class="label">Health Check</div>
                <a href="/health/">System Status →</a>
            </div>
            <div class="link-card admin-link">
                <div class="label">Admin Panel</div>
                <a href="/admin/">Manage Data →</a>
            </div>
            <div class="link-card docs-link">
                <div class="label">Documentation</div>
                <a href="#endpoints">Learn More →</a>
            </div>
        </div>
        
        <!-- Endpoints Section -->
        <div class="endpoints-section" id="endpoints">
            <h2>📡 Available Endpoints (25+)</h2>
            <div class="endpoints-grid">
                <!-- Original Endpoints -->
                <div class="endpoint">
                    <div class="endpoint-name">/api/stocks/</div>
                    <div class="endpoint-desc">Stock management and data</div>
                </div>
                <div class="endpoint">
                    <div class="endpoint-name">/api/recommendations/</div>
                    <div class="endpoint-desc">Trade recommendations</div>
                </div>
                <div class="endpoint">
                    <div class="endpoint-name">/api/portfolio/</div>
                    <div class="endpoint-desc">Portfolio management</div>
                </div>
                <div class="endpoint">
                    <div class="endpoint-name">/api/risk/</div>
                    <div class="endpoint-desc">Risk assessment</div>
                </div>
                
                <!-- New Advanced Features -->
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/signals/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Stock analysis with signals</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/intraday-signals/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Quick intraday signals</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/risk-analysis/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Advanced risk checks</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/paper-trading/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Practice trading safely</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/market-summary/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Market sentiment analysis</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/portfolio-health/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Portfolio metrics</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/smart-alerts/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Alert notifications</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/investment-planner/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Goal-based planning</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/mistake-detector/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Learn from mistakes</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/ai-explain/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">Transparent AI decisions</div>
                </div>
                <div class="endpoint" style="border-left-color: #FF5722;">
                    <div class="endpoint-name">/api/support-resistance/ <span class="new-badge">NEW</span></div>
                    <div class="endpoint-desc">S&R level calculations</div>
                </div>
            </div>
        </div>
        
        <!-- Features Section -->
        <div class="features-section">
            <h2>✨ Key Features</h2>
            <div class="features-grid">
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <div class="feature-text">One-click Stock Analysis (Beginner & Pro)</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-text">Intraday Quick Signals</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🛡️</div>
                    <div class="feature-text">Automatic Risk Checks</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📝</div>
                    <div class="feature-text">Paper Trading Practice</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌍</div>
                    <div class="feature-text">Market Sentiment Analysis</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔔</div>
                    <div class="feature-text">Smart Alert System</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📈</div>
                    <div class="feature-text">Portfolio Health Monitoring</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-text">Investment Goal Planner</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-text">Mistake Detection & Learning</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">💡</div>
                    <div class="feature-text">AI Decision Explanations</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📍</div>
                    <div class="feature-text">Support & Resistance Levels</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔐</div>
                    <div class="feature-text">0.5% Capital Protection</div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>KVK_8833_PROFIT Trading System | Built with Django 4.2.8 & Django REST Framework</p>
            <p style="font-size: 0.9em; margin-top: 10px;">📚 Documentation: README.md | 🔧 Admin: /admin/ | 🚀 API: /api/</p>
        </div>
    </div>
</body>
</html>
        """
        return HttpResponse(html_content, content_type='text/html')

