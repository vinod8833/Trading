
const CACHE_KEY = "popular_stocks_cache";
const CACHE_TIMESTAMP_KEY = "popular_stocks_timestamp";
const FALLBACK_STOCKS_KEY = "fallback_popular_stocks";
const CACHE_DURATION = 5 * 60 * 1000; 


const FALLBACK_POPULAR_STOCKS = [
  { symbol: "INFY", name: "Infosys", sector: "IT", volume: 8500000, change: 1.2 },
  { symbol: "TCS", name: "Tata Consultancy", sector: "IT", volume: 9200000, change: 0.8 },
  { symbol: "WIPRO", name: "Wipro", sector: "IT", volume: 7100000, change: -0.5 },
  { symbol: "HCLTECH", name: "HCL Technologies", sector: "IT", volume: 6300000, change: 1.5 },
  { symbol: "RELIANCE", name: "Reliance Industries", sector: "Energy", volume: 12000000, change: 2.1 },
  { symbol: "HDFCBANK", name: "HDFC Bank", sector: "Banking", volume: 15600000, change: 1.8 },
  { symbol: "ICICIBANK", name: "ICICI Bank", sector: "Banking", volume: 11200000, change: 0.9 },
  { symbol: "SBIN", name: "State Bank of India", sector: "Banking", volume: 13400000, change: 1.3 },
  { symbol: "AXISBANK", name: "Axis Bank", sector: "Banking", volume: 8900000, change: -0.2 },
  { symbol: "LT", name: "Larsen & Toubro", sector: "Engineering", volume: 9800000, change: 2.5 },
  { symbol: "BAJAJFINSV", name: "Bajaj Finserv", sector: "Finance", volume: 5200000, change: 1.1 },
  { symbol: "ASIANPAINT", name: "Asian Paints", sector: "Chemicals", volume: 7400000, change: 0.6 },
  { symbol: "MARUTI", name: "Maruti Suzuki", sector: "Automotive", volume: 10100000, change: -1.2 },
  { symbol: "SUNPHARMA", name: "Sun Pharma", sector: "Pharma", volume: 6800000, change: 1.7 },
  { symbol: "DRREDDY", name: "Dr. Reddy's", sector: "Pharma", volume: 5900000, change: 0.4 },
];


const isCacheValid = () => {
  const timestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
  if (!timestamp) return false;
  
  const elapsed = Date.now() - parseInt(timestamp);
  return elapsed < CACHE_DURATION;
};


const getCachedStocks = () => {
  const cached = localStorage.getItem(CACHE_KEY);
  return cached ? JSON.parse(cached) : null;
};

const getFallbackStocks = () => {
  const fallback = localStorage.getItem(FALLBACK_STOCKS_KEY);
  return fallback ? JSON.parse(fallback) : FALLBACK_POPULAR_STOCKS;
};


const cacheStocks = (stocks) => {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(stocks));
    localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString());
    localStorage.setItem(FALLBACK_STOCKS_KEY, JSON.stringify(stocks));
  } catch (error) {
    console.error("Error caching popular stocks:", error);
  }
};


const calculatePopularityScore = (stock) => {
  const volumeScore = Math.min(stock.volume || 0, 20000000) / 20000000; 
  const changeScore = Math.abs(stock.change || 0) / 10; 
  
  return volumeScore * 0.7 + Math.min(changeScore, 1) * 0.3;
};


export const fetchLivePopularStocks = async (apiUrl = "/api/stocks/") => {
  try {
    if (isCacheValid()) {
      const cached = getCachedStocks();
      if (cached && cached.length > 0) {
        console.log("Using cached popular stocks");
        return cached;
      }
    }

    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    let stocks = Array.isArray(data) ? data : data.results || [];

    if (stocks.length === 0) {
      console.warn("No stocks from API, using fallback data");
      return getFallbackStocks();
    }

    const scoredStocks = stocks.map((stock) => ({
      symbol: stock.symbol,
      name: stock.name,
      sector: stock.sector,
      volume: stock.volume || 0,
      change: stock.price_change_percent || 0,
      price: stock.current_price || 0,
      previousClose: stock.previous_close || 0,
      marketCap: stock.market_cap || 0,
      _score: calculatePopularityScore(stock),
    }));

    const topPopular = scoredStocks
      .sort((a, b) => b._score - a._score)
      .slice(0, 15)
      .map(({ _score, ...stock }) => stock); 

    cacheStocks(topPopular);

    return topPopular;
  } catch (error) {
    console.error("Error fetching live popular stocks:", error);
    
    return getFallbackStocks();
  }
};

export const getPopularStocks = async (apiUrl = "/api/stocks/") => {
  if (isCacheValid()) {
    const cached = getCachedStocks();
    if (cached && cached.length > 0) {
      return cached;
    }
  }

  return fetchLivePopularStocks(apiUrl);
};


export const refreshPopularStocks = async (apiUrl = "/api/stocks/") => {
  localStorage.removeItem(CACHE_TIMESTAMP_KEY);
  return fetchLivePopularStocks(apiUrl);
};


export const getPopularStocksBySetor = async (sector, apiUrl = "/api/stocks/") => {
  const stocks = await getPopularStocks(apiUrl);
  return stocks.filter((s) => s.sector === sector);
};


export const getTopStocksByVolume = async (limit = 8, apiUrl = "/api/stocks/") => {
  const stocks = await getPopularStocks(apiUrl);
  return stocks
    .sort((a, b) => (b.volume || 0) - (a.volume || 0))
    .slice(0, limit);
};


export const getTopStocksByMovement = async (limit = 8, apiUrl = "/api/stocks/") => {
  const stocks = await getPopularStocks(apiUrl);
  return stocks
    .sort((a, b) => Math.abs(b.change || 0) - Math.abs(a.change || 0))
    .slice(0, limit);
};


export const getTopGainers = async (limit = 8, apiUrl = "/api/stocks/") => {
  const stocks = await getPopularStocks(apiUrl);
  return stocks
    .filter((s) => (s.change || 0) > 0)
    .sort((a, b) => (b.change || 0) - (a.change || 0))
    .slice(0, limit);
};


export const getTopLosers = async (limit = 8, apiUrl = "/api/stocks/") => {
  const stocks = await getPopularStocks(apiUrl);
  return stocks
    .filter((s) => (s.change || 0) < 0)
    .sort((a, b) => (a.change || 0) - (b.change || 0))
    .slice(0, limit);
};


export const getLastAvailablePopularStocks = () => {
  return getFallbackStocks();
};


export const clearPopularStocksCache = () => {
  localStorage.removeItem(CACHE_KEY);
  localStorage.removeItem(CACHE_TIMESTAMP_KEY);
};

export default {
  fetchLivePopularStocks,
  getPopularStocks,
  refreshPopularStocks,
  getPopularStocksBySetor,
  getTopStocksByVolume,
  getTopStocksByMovement,
  getTopGainers,
  getTopLosers,
  getLastAvailablePopularStocks,
  clearPopularStocksCache,
};
