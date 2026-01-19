import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

export const useAuthStore = create(
  immer((set) => ({
    user: null,
    isAuthenticated: false,
    accessToken: typeof window !== "undefined" ? localStorage.getItem("access_token") : null,
    refreshToken: typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null,

    setUser: (user) =>
      set((state) => {
        state.user = user;
        state.isAuthenticated = !!user;
      }),

    setTokens: (access, refresh) => {
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access);
        localStorage.setItem("refresh_token", refresh);
      }
      set((state) => {
        state.accessToken = access;
        state.refreshToken = refresh;
      });
    },

    logout: () => {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
      }
      set((state) => {
        state.user = null;
        state.isAuthenticated = false;
        state.accessToken = null;
        state.refreshToken = null;
      });
    },
  }))
);

export const useTradingStore = create(
  immer((set, get) => ({
    stocks: [],
    recommendations: [],
    portfolio: null,
    selectedMode: "pro", 

    setMode: (mode) =>
      set((state) => {
        state.selectedMode = mode;
      }),

    setStocks: (stocks) =>
      set((state) => {
        state.stocks = stocks;
      }),

    setRecommendations: (recommendations) =>
      set((state) => {
        state.recommendations = recommendations;
      }),

    setPortfolio: (portfolio) =>
      set((state) => {
        state.portfolio = portfolio;
      }),

    addRecommendation: (rec) =>
      set((state) => {
        state.recommendations.unshift(rec);
      }),

    updateRecommendation: (id, updates) =>
      set((state) => {
        const index = state.recommendations.findIndex((r) => r.id === id);
        if (index !== -1) {
          state.recommendations[index] = {
            ...state.recommendations[index],
            ...updates,
          };
        }
      }),
  }))
);

export const useUIStore = create(
  immer((set) => ({
    sidebarOpen: true,
    darkMode: false,
    notifications: [],

    toggleSidebar: () =>
      set((state) => {
        state.sidebarOpen = !state.sidebarOpen;
      }),

    toggleDarkMode: () =>
      set((state) => {
        state.darkMode = !state.darkMode;
      }),

    addNotification: (message, type = "info") => {
      const id = Date.now();
      set((state) => {
        state.notifications.push({ id, message, type });
      });
      setTimeout(() => {
        set((state) => {
          state.notifications = state.notifications.filter((n) => n.id !== id);
        });
      }, 5000);
    },
  }))
);
