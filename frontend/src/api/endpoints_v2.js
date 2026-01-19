import api from "./client";

async function safeApiCall(apiFunc, errorMessage = "Operation failed") {
  try {
    const response = await apiFunc();
    
    if (response.data && response.data.success === false) {
      throw {
        response: {
          data: {
            error: response.data.error || "UNKNOWN_ERROR",
            message: response.data.message || errorMessage,
            details: response.data.details,
          },
          status: response.status || 400,
        },
      };
    }
    
    return response;
  } catch (error) {
    if (!error.response) {
      error.response = {
        data: {
          error: "NETWORK_ERROR",
          message: "Network error. Please check your connection.",
          details: { originalError: error.message },
        },
        status: 0,
      };
    }
    
    throw error;
  }
}


function getErrorMessage(error) {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  switch (error.response?.status) {
    case 400:
      return "Invalid request. Please check your input.";
    case 401:
      return "Session expired. Please log in again.";
    case 403:
      return "You don't have permission to do this.";
    case 404:
      return "Resource not found.";
    case 422:
      return error.response?.data?.details?.missing_fields
        ? `Missing fields: ${error.response.data.details.missing_fields.join(", ")}`
        : "Invalid data provided.";
    case 429:
      return "Too many requests. Please try again later.";
    case 500:
      return "Server error. Please try again later.";
    case 503:
      return "Service temporarily unavailable. Please try again later.";
    default:
      return error.message || "An error occurred. Please try again.";
  }
}

// ============================================
// AUTHENTICATION API
// ============================================

export const authApi = {
  login: async (username, password) => {
    return safeApiCall(
      () => api.post("/api/auth/token/", { username, password }),
      "Login failed"
    );
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },

  getUser: async () => {
    return safeApiCall(
      () => api.get("/api/auth/user/"),
      "Failed to fetch user data"
    );
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      throw new Error("No refresh token available");
    }
    
    return safeApiCall(
      () => api.post("/api/auth/token/refresh/", { refresh: refreshToken }),
      "Failed to refresh token"
    );
  },
};

export const stockApi = {
  analyzeStock: async (symbol) => {
    if (!symbol || typeof symbol !== "string") {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Invalid stock symbol",
          },
          status: 422,
        },
      };
    }
    
    return safeApiCall(
      () => api.post("/api/stocks/", { symbol: symbol.toUpperCase() }),
      `Failed to analyze stock ${symbol}`
    );
  },

  getStockAnalysis: async (symbol) => {
    return safeApiCall(
      () => api.get(`/api/stocks/${symbol.toUpperCase()}/`),
      `Failed to fetch analysis for ${symbol}`
    );
  },

  getStocks: async () => {
    return safeApiCall(
      () => api.get("/api/stocks/"),
      "Failed to fetch stocks"
    );
  },
};

export const recommendationApi = {
  generateRecommendation: async (data) => {
    if (!data.stock_symbol) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Stock symbol is required",
            details: { field: "stock_symbol" },
          },
          status: 422,
        },
      };
    }
    
    if (!data.trading_style) {
      data.trading_style = "SWING";
    }
    
    if (!data.capital || data.capital < 1000) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Capital must be at least 1000",
            details: { field: "capital" },
          },
          status: 422,
        },
      };
    }
    
    return safeApiCall(
      () => api.post("/api/recommendations/generate/", {
        stock_symbol: data.stock_symbol.toUpperCase(),
        trading_style: data.trading_style.toUpperCase(),
        capital: parseFloat(data.capital),
      }),
      `Failed to generate recommendation for ${data.stock_symbol}`
    );
  },

  getRecommendations: async () => {
    return safeApiCall(
      () => api.get("/api/recommendations/"),
      "Failed to fetch recommendations"
    );
  },

  getActiveSignals: async () => {
    return safeApiCall(
      () => api.get("/api/recommendations/active/"),
      "Failed to fetch active signals"
    );
  },

  executeRecommendation: async (id) => {
    return safeApiCall(
      () => api.post(`/api/recommendations/${id}/execute/`),
      "Failed to execute recommendation"
    );
  },
};

export const intradayApi = {
  generateIntradaySignal: async (data) => {
    if (!data.stock_symbol) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Stock symbol is required",
          },
          status: 422,
        },
      };
    }
    
    const timeframe = data.timeframe || "5m";
    
    return safeApiCall(
      () => api.post("/api/intraday-signals/", {
        stock_symbol: data.stock_symbol.toUpperCase(),
        timeframe,
      }),
      "Failed to generate intraday signal"
    );
  },

  getIntradaySignals: async () => {
    return safeApiCall(
      () => api.get("/api/intraday-signals/"),
      "Failed to fetch intraday signals"
    );
  },

  closeSignal: async (id) => {
    return safeApiCall(
      () => api.post(`/api/intraday-signals/${id}/close/`),
      "Failed to close signal"
    );
  },
};


export const paperTradingApi = {
  startPaperTrade: async (data) => {
    if (!data.stock_symbol || !data.entry_price || !data.quantity) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Missing required fields",
          },
          status: 422,
        },
      };
    }
    
    return safeApiCall(
      () => api.post("/api/paper-trading/", data),
      "Failed to start paper trade"
    );
  },

  getPaperTrades: async (status = null) => {
    let url = "/api/paper-trading/";
    if (status) {
      url += `?status=${status}`;
    }
    
    return safeApiCall(
      () => api.get(url),
      "Failed to fetch paper trades"
    );
  },

  closePaperTrade: async (id, exitPrice) => {
    return safeApiCall(
      () => api.post(`/api/paper-trading/${id}/close/`, { exit_price: exitPrice }),
      "Failed to close paper trade"
    );
  },

  getPaperTradeDetails: async (id) => {
    return safeApiCall(
      () => api.get(`/api/paper-trading/${id}/`),
      "Failed to fetch paper trade details"
    );
  },
};

export const signalApi = {
  generateSignals: async (data) => {
    return safeApiCall(
      () => api.post("/api/signals/", data),
      "Failed to generate signals"
    );
  },

  getSignals: async () => {
    return safeApiCall(
      () => api.get("/api/signals/"),
      "Failed to fetch signals"
    );
  },

  getSignalDetails: async (id) => {
    return safeApiCall(
      () => api.get(`/api/signals/${id}/`),
      "Failed to fetch signal details"
    );
  },
};

export const scannerApi = {
  scanPatterns: async (data) => {
    if (!data.stock_symbol) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Stock symbol is required",
          },
          status: 422,
        },
      };
    }
    
    return safeApiCall(
      () => api.post("/api/stock-scanner/scan/", {
        symbol: data.stock_symbol.toUpperCase(),
        pattern_types: data.pattern_types || ["candlestick", "chart"],
      }),
      "Failed to scan patterns"
    );
  },

  getPatterns: async (symbol) => {
    return safeApiCall(
      () => api.get(`/api/stock-scanner/patterns/?symbol=${symbol.toUpperCase()}`),
      "Failed to fetch patterns"
    );
  },

  scanMultiple: async (symbols) => {
    if (!Array.isArray(symbols) || symbols.length === 0) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "At least one symbol is required",
          },
          status: 422,
        },
      };
    }
    
    return safeApiCall(
      () => api.post("/api/stock-scanner/scan-multiple/", {
        symbols: symbols.map(s => s.toUpperCase()),
      }),
      "Failed to scan multiple stocks"
    );
  },
};


export const portfolioApi = {
  getPortfolios: async () => {
    return safeApiCall(
      () => api.get("/api/portfolio/"),
      "Failed to fetch portfolios"
    );
  },

  createPortfolio: async (data) => {
    return safeApiCall(
      () => api.post("/api/portfolio/", data),
      "Failed to create portfolio"
    );
  },

  getPortfolio: async (id) => {
    return safeApiCall(
      () => api.get(`/api/portfolio/${id}/`),
      "Failed to fetch portfolio"
    );
  },

  getPortfolioSummary: async (id) => {
    return safeApiCall(
      () => api.get(`/api/portfolio/${id}/summary/`),
      "Failed to fetch portfolio summary"
    );
  },

  addCapital: async (id, amount) => {
    return safeApiCall(
      () => api.post(`/api/portfolio/${id}/add_capital/`, { amount }),
      "Failed to add capital"
    );
  },
};
export const marketApi = {
  getMarketSummary: async () => {
    return safeApiCall(
      () => api.get("/api/market-summary/"),
      "Failed to fetch market summary"
    );
  },

  getSupportResistance: async (symbol) => {
    return safeApiCall(
      () => api.post("/api/support-resistance/", { symbol: symbol.toUpperCase() }),
      "Failed to fetch support/resistance levels"
    );
  },

  getMarketStatus: async () => {
    return safeApiCall(
      () => api.get("/api/health/"),
      "Failed to fetch market status"
    );
  },
};

export const usersApi = {
  getProfile: async () => {
    return safeApiCall(
      () => api.get("/api/users/profile/"),
      "Failed to fetch profile"
    );
  },

  updateProfile: async (data) => {
    return safeApiCall(
      () => api.put("/api/users/profile/", data),
      "Failed to update profile"
    );
  },

  getSettings: async () => {
    return safeApiCall(
      () => api.get("/api/users/settings/"),
      "Failed to fetch settings"
    );
  },

  updateSettings: async (data) => {
    return safeApiCall(
      () => api.put("/api/users/settings/", data),
      "Failed to update settings"
    );
  },

  changePassword: async (data) => {
    if (!data.old_password || !data.new_password) {
      throw {
        response: {
          data: {
            error: "VALIDATION_ERROR",
            message: "Both old and new passwords are required",
          },
          status: 422,
        },
      };
    }
    
    return safeApiCall(
      () => api.post("/api/users/change-password/", data),
      "Failed to change password"
    );
  },
};

export const errorUtils = {
  getErrorMessage,
  parseErrorDetails: (error) => {
    return {
      message: getErrorMessage(error),
      code: error.response?.data?.error || "UNKNOWN",
      status: error.response?.status || 0,
      details: error.response?.data?.details || {},
    };
  },
  

  logError: (error, context = "") => {
    const details = errorUtils.parseErrorDetails(error);
    console.error(`[${context}] ${details.code}: ${details.message}`, details);
  },
};

export default {
  authApi,
  stockApi,
  recommendationApi,
  intradayApi,
  paperTradingApi,
  signalApi,
  scannerApi,
  portfolioApi,
  marketApi,
  usersApi,
  errorUtils,
  safeApiCall,
};
