
import { useState, useEffect, useCallback } from "react";
import { 
  getPopularStocks, 
  getLastAvailablePopularStocks,
  refreshPopularStocks,
  getTopGainers,
  getTopLosers,
  getTopStocksByVolume,
  getTopStocksByMovement
} from "./marketDataService";
import { marketStatus } from "./tradingEngine";

export const usePopularStocks = (refreshInterval = 5 * 60 * 1000) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [marketOpen, setMarketOpen] = useState(false);

  const loadStocks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const isOpen = marketStatus.isMarketOpen();
      setMarketOpen(isOpen);

      const fetchedStocks = await getPopularStocks();
      setStocks(fetchedStocks);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Error loading popular stocks:", err);
      setError(err.message);
      
      const fallbackStocks = getLastAvailablePopularStocks();
      setStocks(fallbackStocks);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStocks();
  }, [loadStocks]);

  useEffect(() => {
    const interval = setInterval(loadStocks, refreshInterval);
    return () => clearInterval(interval);
  }, [loadStocks, refreshInterval]);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const refreshedStocks = await refreshPopularStocks();
      setStocks(refreshedStocks);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Error refreshing stocks:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    stocks,
    loading,
    error,
    lastUpdated,
    marketOpen,
    refresh,
  };
};

export const useTopGainers = (limit = 8) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadGainers = async () => {
      try {
        setLoading(true);
        const gainers = await getTopGainers(limit);
        setStocks(gainers);
      } catch (err) {
        console.error("Error loading gainers:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadGainers();
  }, [limit]);

  return { stocks, loading, error };
};


export const useTopLosers = (limit = 8) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadLosers = async () => {
      try {
        setLoading(true);
        const losers = await getTopLosers(limit);
        setStocks(losers);
      } catch (err) {
        console.error("Error loading losers:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadLosers();
  }, [limit]);

  return { stocks, loading, error };
};


export const useTopByVolume = (limit = 8) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadByVolume = async () => {
      try {
        setLoading(true);
        const volumeStocks = await getTopStocksByVolume(limit);
        setStocks(volumeStocks);
      } catch (err) {
        console.error("Error loading volume stocks:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadByVolume();
  }, [limit]);

  return { stocks, loading, error };
};


export const useTopByMovement = (limit = 8) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadByMovement = async () => {
      try {
        setLoading(true);
        const movementStocks = await getTopStocksByMovement(limit);
        setStocks(movementStocks);
      } catch (err) {
        console.error("Error loading movement stocks:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadByMovement();
  }, [limit]);

  return { stocks, loading, error };
};

export default usePopularStocks;
