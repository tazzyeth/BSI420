// Stock Analysis App - Main JavaScript
console.log("Main.js loaded");

// Global variables
let currentTicker = '';
let chartDataStore = {};

// Initialize the application when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Document ready, initializing app");
    
    // Initialize form handling
    initializeForm();
    
    // Initialize tabs
    document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.getAttribute('href');
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            document.querySelector(tabId).classList.add('show', 'active');
        });
    });
    
    // Initialize chart control buttons
    initializeChartControls();
});

// Initialize the form submission handler
function initializeForm() {
    const form = document.getElementById('analysisForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const ticker = document.getElementById('ticker').value.trim().toUpperCase();
            if (!ticker) {
                showAlert('Please enter a ticker symbol', 'danger');
                return;
            }
            
            fetchStockData(ticker);
        });
    }
}

// Fetch stock data from the server
function fetchStockData(ticker) {
    currentTicker = ticker;
    
    // Show loading spinner and hide previous results
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingTicker = document.getElementById('loadingTicker');
    const companyData = document.getElementById('companyData');
    const advancedMetrics = document.getElementById('advancedMetrics');
    const analysisResults = document.getElementById('analysisResults');
    const alertMessage = document.getElementById('alertMessage');
    
    if (loadingSpinner) loadingSpinner.style.display = 'flex';
    if (loadingTicker) loadingTicker.textContent = ticker;
    if (companyData) companyData.style.display = 'none';
    if (advancedMetrics) advancedMetrics.style.display = 'none';
    if (analysisResults) analysisResults.style.display = 'none';
    
    // Clear previous alert messages
    if (alertMessage) {
        alertMessage.style.display = 'none';
        alertMessage.textContent = '';
    }
    
    console.log(`Fetching data for ${ticker}`);
    
    // Get form values
    const disableChartsCheckbox = document.getElementById('disableCharts');
    const disableCharts = disableChartsCheckbox ? disableChartsCheckbox.checked : true;
    
    // Create form data
    const formData = new FormData();
    formData.append('ticker', ticker);
    formData.append('use_mock', 'false'); // Always set to false, never use mock data
    formData.append('disable_charts', disableCharts);
    
    // Make the fetch request
    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log("Response status:", response.status);
        return response.json();
    })
    .then(data => {
        // Hide loading spinner
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
        if (data.error) {
            showAlert(`Error: ${data.error}`, 'danger');
            // If we have company data despite the error, display it
            if (data.company_data && data.company_data.name) {
                displayCompanyData(data.company_data);
            }
            return;
        }
        
        // Process data
        if (data.company_data) {
            console.log("Company data received:", data.company_data);
            
            if (data.charts) {
                console.log("Charts data keys:", Object.keys(data.charts));
                chartDataStore = data.charts;
            } else {
                console.log("No charts data available");
            }
            
            // Display company data
            displayCompanyData(data.company_data);
            
            // Display charts if enabled
            if (!disableCharts && data.charts) {
                try {
                    displayCharts(data.charts);
                    showAlert(`Data loaded successfully for ${ticker}`, 'success', true);
                } catch (error) {
                    console.error("Error displaying charts:", error);
                    showAlert(`Data loaded, but charts could not be rendered for ${ticker}`, 'warning');
                    displayChartPlaceholders();
                }
            } else {
                displayChartPlaceholders(disableCharts ? 'disabled' : 'unavailable');
                showAlert(`Basic data loaded for ${ticker}`, 'success', true);
            }
        } else {
            showAlert("No company data received", 'danger');
        }
    })
    .catch(error => {
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        console.error("Error in fetch operation:", error);
        showAlert(`Failed to retrieve data: ${error.message}`, 'danger');
    });
}

// Display company data in the UI
function displayCompanyData(data) {
    console.log("Updating company info with:", data);
    
    try {
        // Helper function to update element text with null checks
        function updateElement(id, value) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value || 'N/A';
            } else {
                console.debug(`Element with ID '${id}' not found in the DOM`);
            }
        }
        
        // Update company header and basic info
        updateElement('companyName', data.name);
        updateElement('companySymbol', currentTicker);
        updateElement('description', data.description);
        
        // Update company overview data
        updateElement('sector', data.sector);
        updateElement('industry', data.industry);
        updateElement('market-cap', data.market_cap);
        updateElement('pe-ratio', data.pe_ratio);
        updateElement('forward-pe', data.forward_pe);
        updateElement('eps-overview', data.eps);
        updateElement('peg-ratio', data.peg_ratio);
        updateElement('dividend-yield', data.dividend_yield);
        updateElement('beta', data.beta);
        updateElement('52-week-range', data['52_week_range']);
        updateElement('current-ratio', data.current_ratio);
        updateElement('profit-margin', data.profit_margin);
        updateElement('roe', data.return_on_equity);
        updateElement('roa', data.return_on_assets);
        updateElement('intangible-assets', data.intangible_assets);
        
        // Update volume and trading metrics
        updateElement('current-volume', data.current_volume);
        updateElement('average-volume', data.average_volume);
        updateElement('relative-volume', data.relative_volume);
        updateElement('insider-ownership', data.insider_ownership);
        updateElement('institutional-ownership', data.institutional_ownership);
        updateElement('float-market', data.float);
        updateElement('shortFloat', data.short_float);
        updateElement('revenuePerShare', data.revenue_per_share);
        updateElement('profitMargin', data.profit_margin);
        updateElement('freeCashFlow', data.free_cash_flow);
        updateElement('weekHigh', data['52_week_high']);
        updateElement('weekLow', data['52_week_low']);
        
        // Update new metrics for Key Metrics Card
        updateElement('eps-key', data.eps);
        updateElement('pegRatio', data.pegRatio);
        updateElement('forwardPE', data.forwardPE);
        updateElement('dividendYield', data.dividendYield);
        updateElement('marketCap', data.marketCap);
        updateElement('currentRatio-key', data.currentRatio);
        updateElement('float-key', data.float);
        updateElement('shortFloat', data.short_float);
        
        // Update Ownership & Assets Card
        updateElement('institutionalOwnership', data.institutionalOwnership);
        updateElement('insiderOwnership', data.insiderOwnership);
        updateElement('intangibleAssets', data.intangibleAssets);
        
        // Update Advanced Metrics
        updateElement('currentRatio-adv', data.currentRatio);
        updateElement('intangibleAssets-adv', data.intangibleAssets);
        
        // Update current price and price change if available
        updateElement('currentPrice', data.current_price);
        
        if (data.daily_change && data.daily_change_pct) {
            const change = parseFloat(data.daily_change);
            const changePct = data.daily_change_pct;
            const changeElement = document.getElementById('dailyChange');
            
            if (changeElement) {
                if (change > 0) {
                    changeElement.innerHTML = `<span class="text-success">+${change} (${changePct})</span>`;
                } else if (change < 0) {
                    changeElement.innerHTML = `<span class="text-danger">${change} (${changePct})</span>`;
                } else {
                    changeElement.innerHTML = `<span class="text-muted">${change} (${changePct})</span>`;
                }
            }
        }
        
        // Update advanced financial metrics
        updateElement('totalAssets', data.total_assets);
        updateElement('totalLiabilities', data.total_liabilities);
        updateElement('shareholderEquity', data.shareholder_equity);
        updateElement('longTermDebt', data.long_term_debt);
        updateElement('cashFlowToRevenue', data.cash_flow_to_revenue);
        updateElement('enterpriseValue', data.enterprise_value);
        updateElement('debtToEquity', data.debt_to_equity);
        updateElement('grossMargin', data.gross_margin);
        updateElement('operatingMargin', data.operating_margin);
        updateElement('returnOnEquity', data.return_on_equity);
        updateElement('returnOnAssets', data.return_on_assets);
        
        // Show the data sections if they exist
        const companyDataElement = document.getElementById('companyData');
        if (companyDataElement) companyDataElement.style.display = 'flex';
        
        const advancedMetricsElement = document.getElementById('advancedMetrics');
        if (advancedMetricsElement) advancedMetricsElement.style.display = 'flex';
        
        const ownershipAssetsSection = document.getElementById('ownershipAssetsSection');
        if (ownershipAssetsSection) ownershipAssetsSection.style.display = 'block';
        
        const analysisResultsElement = document.getElementById('analysisResults');
        if (analysisResultsElement) analysisResultsElement.style.display = 'block';
        
        // Print debug info for fields that might be missing
        console.log("Display data fields check:");
        console.log("EPS:", data.eps);
        console.log("PEG Ratio:", data.pegRatio);
        console.log("Forward P/E:", data.forwardPE);
        console.log("Dividend Yield:", data.dividendYield);
        console.log("Market Cap:", data.marketCap);
        console.log("Current Ratio:", data.currentRatio);
        console.log("Float:", data.float);
        console.log("Short Float:", data.short_float);
        console.log("Institutional Ownership:", data.institutionalOwnership);
        console.log("Insider Ownership:", data.insiderOwnership);
        console.log("Intangible Assets:", data.intangibleAssets);
    } catch (error) {
        console.error("Error displaying company data:", error);
        showAlert(`Error displaying company data: ${error.message}`, 'warning');
    }
}

// Display charts if available
function displayCharts(charts) {
    // Clear existing charts
    document.querySelectorAll('#summaryChart, #priceChart, #techChart, #volumeChart, #financialChart')
        .forEach(container => {
            if (container) container.innerHTML = '';
        });
    
    // Keep track of successes and failures
    let successful = 0;
    let failed = 0;
    
    // Helper function to safely render a chart
    function safeRenderChart(containerId, chartData) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Chart container #${containerId} not found in DOM`);
                failed++;
                return false;
            }
            
            if (!chartData || !chartData.data || !Array.isArray(chartData.data) || !chartData.layout) {
                container.innerHTML = '<div class="alert alert-warning">Chart data not available or invalid</div>';
                failed++;
                return false;
            }
            
            // Ensure the layout is responsive
            const responsiveLayout = {
                ...chartData.layout,
                autosize: true,
                responsive: true,
                // Add margin for better visibility
                margin: {
                    ...chartData.layout.margin,
                    pad: 5
                }
            };
            
            // Special handling for price chart to make it more detailed
            if (containerId === 'priceChart') {
                // Add responsive configuration specific to price chart
                responsiveLayout.xaxis = {
                    ...responsiveLayout.xaxis,
                    autorange: true,
                    rangeslider: {
                        visible: false  // Disable rangeslider for cleaner look
                    }
                };
                
                // Make sure y-axis auto-scales
                responsiveLayout.yaxis = {
                    ...responsiveLayout.yaxis,
                    autorange: true,
                    fixedrange: false
                };
                
                // Make sure modebar is always visible for zooming
                responsiveLayout.modebar = {
                    orientation: 'v',
                    activecolor: '#007bff'
                };
            }
            
            // Create the chart with responsive config
            const config = {
                responsive: true,
                displayModeBar: true, // Always show the mode bar
                modeBarButtonsToAdd: ['toImage', 'resetScale2d'],
                scrollZoom: true, // Enable scroll to zoom
                displaylogo: false
            };
            
            Plotly.newPlot(containerId, chartData.data, responsiveLayout, config);
            successful++;
            
            return true;
        } catch (error) {
            console.error(`Error rendering ${containerId}:`, error);
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `<div class="alert alert-danger">
                    Error rendering chart: ${error.message}
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="retryChart('${containerId}')">Retry</button>
                </div>`;
            }
            failed++;
            return false;
        }
    }
    
    // Try to render each chart
    if (charts.summary) safeRenderChart('summaryChart', charts.summary);
    if (charts.price) safeRenderChart('priceChart', charts.price);
    if (charts.technical) safeRenderChart('techChart', charts.technical);
    if (charts.volume) safeRenderChart('volumeChart', charts.volume);
    if (charts.financial) safeRenderChart('financialChart', charts.financial);
    
    // Add window resize handler for responsive charts
    setupResponsiveCharts();
    
    return { successful, failed };
}

// Setup responsive behavior for charts
function setupResponsiveCharts() {
    // Resize all charts when window is resized
    window.removeEventListener('resize', resizeAllCharts); // Remove any previous listener
    window.addEventListener('resize', resizeAllCharts);
    
    // Also resize charts when a tab is shown
    document.querySelectorAll('.nav-tabs .nav-link').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const targetId = e.target.getAttribute('href').substring(1);
            const chartId = targetId + 'Chart';
            const chartElement = document.getElementById(chartId);
            
            if (chartElement) {
                setTimeout(() => {
                    try {
                        Plotly.relayout(chartId, {
                            autosize: true
                        });
                    } catch (err) {
                        console.warn(`Could not resize chart ${chartId}:`, err);
                    }
                }, 10);
            }
        });
    });
}

// Resize all charts
function resizeAllCharts() {
    try {
        ['summaryChart', 'priceChart', 'techChart', 'volumeChart', 'financialChart'].forEach(chartId => {
            const chart = document.getElementById(chartId);
            if (chart && chart.data) {
                Plotly.relayout(chartId, {
                    autosize: true
                });
            }
        });
    } catch (error) {
        console.error("Error resizing charts:", error);
    }
}

// Display placeholder messages when charts can't be rendered
function displayChartPlaceholders(reason = 'error') {
    let message = '';
    let alertClass = '';
    
    switch (reason) {
        case 'disabled':
            message = 'Charts were disabled by user';
            alertClass = 'info';
            break;
        case 'unavailable':
            message = 'Chart data not available';
            alertClass = 'warning';
            break;
        default:
            message = 'Charts could not be rendered';
            alertClass = 'danger';
    }
    
    document.querySelectorAll('#summaryChart, #priceChart, #techChart, #volumeChart, #financialChart')
        .forEach(container => {
            if (container) {
                container.innerHTML = `<div class="alert alert-${alertClass}">${message}</div>`;
            }
        });
}

// Show alert message
function showAlert(message, type = 'info', autoHide = false) {
    const alertElement = document.getElementById('alertMessage');
    if (alertElement) {
        alertElement.className = `alert alert-${type} mt-3`;
        alertElement.textContent = message;
        alertElement.style.display = 'block';
        
        if (autoHide) {
            setTimeout(() => {
                if (alertElement) alertElement.style.display = 'none';
            }, 5000);
        }
    } else {
        console.warn("Alert element not found in DOM");
    }
}

// Retry chart rendering - global function for retry buttons
window.retryChart = function(chartId) {
    const chartType = chartId.replace('Chart', '');
    const container = document.getElementById(chartId);
    
    if (!container) {
        console.error(`Chart container #${chartId} not found for retry`);
        return;
    }
    
    if (chartDataStore && chartDataStore[chartType]) {
        try {
            console.log(`Retrying ${chartId} chart`);
            
            // Create the chart with responsive config
            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToAdd: ['toImage', 'resetScale2d'],
                scrollZoom: true,
                displaylogo: false
            };
            
            // Ensure the layout is responsive
            const chartData = chartDataStore[chartType];
            const responsiveLayout = {
                ...chartData.layout,
                autosize: true,
                responsive: true
            };
            
            Plotly.newPlot(chartId, chartData.data, responsiveLayout, config);
            
            const alertEl = container.querySelector('.alert');
            if (alertEl) alertEl.remove();
            
            console.log(`Successfully re-rendered ${chartId} chart`);
        } catch (error) {
            console.error(`Error re-rendering ${chartId} chart:`, error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    Error rendering chart: ${error.message}
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="retryChart('${chartId}')">Retry Again</button>
                </div>
            `;
        }
    } else {
        console.error(`No chart data available for ${chartId}`);
        container.innerHTML = '<div class="alert alert-warning">Chart data not available</div>';
    }
};

// Initialize chart control buttons
function initializeChartControls() {
    // Zoom in buttons
    document.querySelectorAll('.zoom-in-btn').forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.getAttribute('data-chart-id');
            zoomChart(chartId, 0.5); // Zoom in by 50%
        });
    });
    
    // Zoom out buttons
    document.querySelectorAll('.zoom-out-btn').forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.getAttribute('data-chart-id');
            zoomChart(chartId, 2); // Zoom out by 200%
        });
    });
    
    // Fullscreen buttons
    document.querySelectorAll('.fullscreen-btn').forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.getAttribute('data-chart-id');
            toggleFullscreen(chartId);
        });
    });
}

// Zoom in or out on a chart
function zoomChart(chartId, factor) {
    const chartDiv = document.getElementById(chartId);
    if (!chartDiv) return;
    
    try {
        const currentRange = Plotly.getSubplotIds(chartId).map(id => {
            const xrange = Plotly.getXAxes(chartId)[0].range;
            const yrange = Plotly.getYAxes(chartId)[0].range;
            return { xrange, yrange };
        })[0];
        
        if (!currentRange) return;
        
        // Calculate new ranges
        const xMiddle = (currentRange.xrange[0] + currentRange.xrange[1]) / 2;
        const xDiff = (currentRange.xrange[1] - currentRange.xrange[0]) * factor / 2;
        
        const yMiddle = (currentRange.yrange[0] + currentRange.yrange[1]) / 2;
        const yDiff = (currentRange.yrange[1] - currentRange.yrange[0]) * factor / 2;
        
        // Apply new ranges
        Plotly.relayout(chartId, {
            'xaxis.range': [xMiddle - xDiff, xMiddle + xDiff],
            'yaxis.range': [yMiddle - yDiff, yMiddle + yDiff]
        });
    } catch (error) {
        console.error(`Error zooming chart ${chartId}:`, error);
    }
}

// Toggle fullscreen mode for a chart
function toggleFullscreen(chartId) {
    const chartDiv = document.getElementById(chartId);
    if (!chartDiv) return;
    
    try {
        if (!document.fullscreenElement) {
            // Enter fullscreen
            if (chartDiv.requestFullscreen) {
                chartDiv.requestFullscreen();
            } else if (chartDiv.webkitRequestFullscreen) { /* Safari */
                chartDiv.webkitRequestFullscreen();
            } else if (chartDiv.msRequestFullscreen) { /* IE11 */
                chartDiv.msRequestFullscreen();
            }
            
            // Resize chart after entering fullscreen
            setTimeout(() => {
                Plotly.relayout(chartId, {
                    autosize: true
                });
            }, 100);
        } else {
            // Exit fullscreen
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) { /* Safari */
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { /* IE11 */
                document.msExitFullscreen();
            }
            
            // Resize chart after exiting fullscreen
            setTimeout(() => {
                Plotly.relayout(chartId, {
                    autosize: true
                });
            }, 100);
        }
    } catch (error) {
        console.error(`Error toggling fullscreen for chart ${chartId}:`, error);
    }
} 