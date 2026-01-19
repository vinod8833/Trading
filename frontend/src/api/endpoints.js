import api from "./client";

async function safeCall(apiFunc) {
  try {
    const response = await apiFunc();
    if (response.data && response.data.success === false) {
      throw response;
    }
    return response;
  } catch (error) {
    if (!error.response) {
      error.response = {
        data: { error: "NETWORK_ERROR", message: "Network connection failed" },
        status: 0,
      };
    }
    throw error;
  }
}

export const authApi = {
  login: (username, password) =>
    safeCall(() => api.post("/api/auth/token/", { username, password })),

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },

  getUser: () => safeCall(() => api.get("/api/auth/user/")),
};

export const stockApi = {
  analyzeStock: (symbol) => {
    if (!symbol) throw new Error("Symbol required");
    return safeCall(() => api.post("/api/stocks/", { symbol: symbol.toUpperCase() }));
  },

  getStockAnalysis: (symbol) =>
    safeCall(() => api.get(`/api/stocks/${symbol.toUpperCase()}/`)),

  getStocks: () => safeCall(() => api.get("/api/stocks/")),
};

export const recommendationApi = {
  generateRecommendation: (data) => {
    if (!data.stock_symbol) throw new Error("Stock symbol required");
    if (!data.trading_style) data.trading_style = "SWING";
    if (!data.capital || data.capital < 1000) throw new Error("Capital must be >= 1000");
    
    return safeCall(() =>
      api.post("/api/recommendations/generate/", {
        stock_symbol: data.stock_symbol.toUpperCase(),
        trading_style: data.trading_style.toUpperCase(),
        capital: parseFloat(data.capital),
      })
    );
  },

  getRecommendations: () =>
    safeCall(() => api.get("/api/recommendations/")),

  getActiveSignals: () =>
    safeCall(() => api.get("/api/recommendations/active/")),

  executeRecommendation: (id) =>
    safeCall(() => api.post(`/api/recommendations/${id}/execute/`)),
};

export const portfolioApi = {
  getPortfolios: () =>
    safeCall(() => api.get("/api/portfolio/")),

  createPortfolio: (data) =>
    safeCall(() => api.post("/api/portfolio/", data)),

  getPortfolio: (id) =>
    safeCall(() => api.get(`/api/portfolio/${id}/`)),

  getPortfolioSummary: (id) =>
    safeCall(() => api.get(`/api/portfolio/${id}/summary/`)),

  addCapital: (id, amount) =>
    safeCall(() => api.post(`/api/portfolio/${id}/add_capital/`, { amount })),
};

export const riskApi = {
  assessRisk: (data) =>
    safeCall(() => api.post("/api/risk/assess/", data)),

  getRiskAssessments: () =>
    safeCall(() => api.get("/api/risk/")),
};

export const signalApi = {
  generateSignals: (data) =>
    safeCall(() => api.post("/api/signals/", data)),

  getSignals: () =>
    safeCall(() => api.get("/api/signals/")),
};

export const intradayApi = {
  generateIntradaySignal: (data) => {
    if (!data.stock_symbol) throw new Error("Stock symbol required");
    return safeCall(() =>
      api.post("/api/intraday-signals/", {
        stock_symbol: data.stock_symbol.toUpperCase(),
        timeframe: data.timeframe || "5m",
      })
    );
  },

  getIntradaySignals: () =>
    safeCall(() => api.get("/api/intraday-signals/")),

  closeSignal: (id) =>
    safeCall(() => api.post(`/api/intraday-signals/${id}/close/`)),
};

export const paperTradingApi = {
  startPaperTrade: (data) => {
    if (!data.stock_symbol || !data.entry_price || !data.quantity) {
      throw new Error("Missing required fields");
    }
    return safeCall(() => api.post("/api/paper-trading/", data));
  },

  getPaperTrades: () =>
    safeCall(() => api.get("/api/paper-trading/")),

  closePaperTrade: (id, exitPrice) =>
    safeCall(() => api.post(`/api/paper-trading/${id}/close/`, { exit_price: exitPrice })),
};

export const alertApi = {
  createAlert: (data) =>
    safeCall(() => api.post("/api/smart-alerts/", data)),

  getAlerts: () =>
    safeCall(() => api.get("/api/smart-alerts/")),

  deleteAlert: (id) =>
    safeCall(() => api.delete(`/api/smart-alerts/${id}/`)),
};

export const marketApi = {
  getMarketSummary: () =>
    safeCall(() => api.get("/api/market-summary/")),

  getSupportResistance: (symbol) =>
    safeCall(() => api.post("/api/support-resistance/", { symbol: symbol.toUpperCase() })),

  getMarketStatus: () =>
    safeCall(() => api.get("/health/")),
};

export const investmentApi = {
  getInvestmentPlan: (data) =>
    safeCall(() => api.post("/api/investment-planner/", data)),

  getAlternatives: (data) =>
    safeCall(() => api.post("/api/ai-explain/", data)),
};

export const technicalAnalysisApi = {
  analyzeTechnical: (symbol, timeframe = "1D", market_open = true) =>
    safeCall(() =>
      api.post("/api/technical-analysis/analyze_technical/", {
        symbol: symbol.toUpperCase(),
        timeframe,
        market_open,
      })
    ),

  getPatterns: (symbol) =>
    safeCall(() => api.get(`/api/technical-analysis/patterns/${symbol.toUpperCase()}/`)),
};

export const usersApi = {
  getProfile: () =>
    safeCall(() => api.get("/api/users/profile/")),

  updateProfile: (data) =>
    safeCall(() => api.put("/api/users/profile/", data)),

  updateSettings: (data) =>
    safeCall(() => api.put("/api/users/settings/", data)),

  getSettings: () =>
    safeCall(() => api.get("/api/users/settings/")),

  changePassword: (data) => {
    if (!data.old_password || !data.new_password) {
      throw new Error("Both passwords required");
    }
    return safeCall(() => api.post("/api/users/change-password/", data));
  },
};

export const tradingApi = {
  getPortfolios: () =>
    safeCall(() => api.get("/api/portfolio/")),
};

export const scannerApi = {
  scanPatterns: (data) => {
    if (!data.stock_symbol) throw new Error("Symbol required");
    return safeCall(() =>
      api.post("/api/stock-scanner/scan/", {
        symbol: data.stock_symbol.toUpperCase(),
        pattern_types: data.pattern_types || ["candlestick", "chart"],
      })
    );
  },

  getPatterns: (symbol) =>
    safeCall(() => api.get(`/api/stock-scanner/patterns/?symbol=${symbol.toUpperCase()}`)),
};

// Error utilities
export const errorUtils = {
  getErrorMessage: (error) => {
    if (error.response?.data?.message) return error.response.data.message;
    if (error.message) return error.message;
    
    const statusMessages = {
      400: "Invalid request",
      401: "Please log in",
      403: "Access denied",
      404: "Not found",
      422: "Invalid data",
      429: "Too many requests",
      500: "Server error",
      503: "Service unavailable",
    };
    
    return statusMessages[error.response?.status] || "An error occurred";
  },
};
