import React, { useState, useEffect } from "react";
import { portfolioApi } from "../api/endpoints";
import toast from "react-hot-toast";
import { riskManagement, marketStatus } from "../utils/tradingEngine";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input, Select } from "../components/ui/Input";
import { Badge, Stat, Progress, Alert } from "../components/ui/Common";
import { Tabs, Modal } from "../components/ui/Layouts";

export default function Portfolio() {
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState("");
  const [addCapitalAmount, setAddCapitalAmount] = useState("");
  const [marketOpen, setMarketOpen] = useState(false);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchPortfolios();

    const updateMarketStatus = () => {
      setMarketOpen(marketStatus.isMarketOpen());
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (selectedPortfolio) {
      calculateRiskMetrics(selectedPortfolio);
    }
  }, [selectedPortfolio]);

  const fetchPortfolios = async () => {
    setIsLoading(true);
    try {
      const response = await portfolioApi.getPortfolios();
      const ports = Array.isArray(response.data) ? response.data : response.data?.results || [];
      setPortfolios(ports);
      if (ports.length > 0) {
        setSelectedPortfolio(ports[0]);
      }
    } catch (error) {
      toast.error("Failed to fetch portfolios");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateRiskMetrics = (portfolio) => {
    const metrics = {
      totalCapital: portfolio.total_capital || 0,
      investedAmount: portfolio.invested_amount || 0,
      currentValue: portfolio.current_value || 0,
      totalGain: (portfolio.current_value || 0) - (portfolio.invested_amount || 0),
      gainPercentage: ((portfolio.current_value - portfolio.invested_amount) / portfolio.invested_amount * 100) || 0,
      riskExposure: (portfolio.invested_amount / portfolio.total_capital * 100) || 0,
      drawdown: portfolio.max_drawdown || 0,
      sharpeRatio: portfolio.sharpe_ratio || 0,
    };
    setRiskMetrics(metrics);
  };

  const handleCreatePortfolio = async () => {
    if (!newPortfolioName.trim() || !addCapitalAmount) {
      toast.error("Please fill in all fields");
      return;
    }

    try {
      await portfolioApi.createPortfolio({
        name: newPortfolioName,
        total_capital: parseFloat(addCapitalAmount),
      });
      toast.success("Portfolio created successfully");
      setNewPortfolioName("");
      setAddCapitalAmount("");
      setShowCreateForm(false);
      fetchPortfolios();
    } catch (error) {
      toast.error("Failed to create portfolio");
      console.error(error);
    }
  };

  const handleDeletePortfolio = async (portfolioId) => {
    if (!window.confirm("Are you sure you want to delete this portfolio?")) {
      return;
    }

    try {
      await portfolioApi.deletePortfolio(portfolioId);
      toast.success("Portfolio deleted");
      setSelectedPortfolio(null);
      fetchPortfolios();
    } catch (error) {
      toast.error("Failed to delete portfolio");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Management</h1>
          <p className="text-gray-600 mt-1">Track and manage your investment portfolios</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)} variant="primary">
          ➕ New Portfolio
        </Button>
      </div>

      {!marketOpen && (
        <Alert
          type="info"
          title="Market Closed"
          message="Portfolio data is updated during market hours. Current values shown are EOD prices."
          icon="🕐"
        />
      )}

      <Modal
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create New Portfolio"
      >
        <div className="space-y-4">
          <Input
            label="Portfolio Name"
            placeholder="e.g., Conservative Growth"
            value={newPortfolioName}
            onChange={(e) => setNewPortfolioName(e.target.value)}
          />
          <Input
            label="Initial Capital (₹)"
            type="number"
            placeholder="e.g., 100000"
            value={addCapitalAmount}
            onChange={(e) => setAddCapitalAmount(e.target.value)}
            min="0"
            step="10000"
          />
        </div>
        <div className="flex gap-3 justify-end mt-6">
          <Button
            variant="outline"
            onClick={() => {
              setShowCreateForm(false);
              setNewPortfolioName("");
              setAddCapitalAmount("");
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleCreatePortfolio} variant="primary">
            Create
          </Button>
        </div>
      </Modal>

      {portfolios.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
            {portfolios.map((portfolio) => (
              <button
                key={portfolio.id}
                onClick={() => setSelectedPortfolio(portfolio)}
                className={`
                  p-4 rounded-lg border-2 transition-all
                  ${selectedPortfolio?.id === portfolio.id
                    ? "border-blue-600 bg-blue-50"
                    : "border-gray-200 hover:border-blue-300"
                  }
                `}
              >
                <p className="font-semibold text-gray-900">{portfolio.name}</p>
                <p className="text-sm text-gray-600 mt-1">₹{portfolio.total_capital?.toLocaleString()}</p>
                <p className={`text-sm font-medium mt-2 ${
                  (portfolio.current_value - portfolio.invested_amount) >= 0
                    ? "text-green-600"
                    : "text-red-600"
                }`}>
                  {((portfolio.current_value - portfolio.invested_amount) / portfolio.invested_amount * 100)?.toFixed(2)}%
                </p>
              </button>
            ))}
          </div>

          {selectedPortfolio && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Stat
                  label="Total Capital"
                  value={`₹${riskMetrics?.totalCapital?.toLocaleString()}`}
                  icon="💰"
                />
                <Stat
                  label="Invested Amount"
                  value={`₹${riskMetrics?.investedAmount?.toLocaleString()}`}
                  icon="📊"
                />
                <Stat
                  label="Current Value"
                  value={`₹${riskMetrics?.currentValue?.toLocaleString()}`}
                  change={`${riskMetrics?.gainPercentage?.toFixed(2)}%`}
                  changeType={riskMetrics?.gainPercentage > 0 ? "up" : "down"}
                  icon="📈"
                />
                <Stat
                  label="Total Gain/Loss"
                  value={`₹${riskMetrics?.totalGain?.toLocaleString()}`}
                  changeType={riskMetrics?.totalGain > 0 ? "up" : "down"}
                  icon="💹"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Risk Metrics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-600">Risk Exposure</span>
                        <span className="font-semibold">{riskMetrics?.riskExposure?.toFixed(1)}%</span>
                      </div>
                      <Progress value={riskMetrics?.riskExposure || 0} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-600">Max Drawdown</span>
                        <span className="font-semibold">{riskMetrics?.drawdown?.toFixed(2)}%</span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-600">Sharpe Ratio</span>
                        <span className="font-semibold">{riskMetrics?.sharpeRatio?.toFixed(2)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Holdings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Total Holdings</span>
                        <span className="font-semibold">{selectedPortfolio.holdings_count || 0}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Active Positions</span>
                        <span className="font-semibold">{selectedPortfolio.active_positions || 0}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Avg Holding Period</span>
                        <span className="font-semibold">{selectedPortfolio.avg_holding_days || 0} days</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Performance</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Win Rate</span>
                      <span className="font-semibold">{selectedPortfolio.win_rate?.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Profit Factor</span>
                      <span className="font-semibold">{selectedPortfolio.profit_factor?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">ROI</span>
                      <span className="font-semibold text-green-600">{selectedPortfolio.roi?.toFixed(2)}%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Current Holdings</CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedPortfolio.holdings && selectedPortfolio.holdings.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="border-b border-gray-200">
                          <tr>
                            <th className="text-left py-3 px-4 font-semibold">Stock</th>
                            <th className="text-left py-3 px-4 font-semibold">Quantity</th>
                            <th className="text-left py-3 px-4 font-semibold">Entry Price</th>
                            <th className="text-left py-3 px-4 font-semibold">Current Price</th>
                            <th className="text-left py-3 px-4 font-semibold">Gain/Loss</th>
                            <th className="text-right py-3 px-4 font-semibold">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedPortfolio.holdings.map((holding, idx) => {
                            const gainLoss = ((holding.current_price - holding.entry_price) / holding.entry_price * 100) || 0;
                            return (
                              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-3 px-4 font-medium">{holding.symbol}</td>
                                <td className="py-3 px-4">{holding.quantity}</td>
                                <td className="py-3 px-4">₹{holding.entry_price?.toFixed(2)}</td>
                                <td className="py-3 px-4">₹{holding.current_price?.toFixed(2)}</td>
                                <td className={`py-3 px-4 font-medium ${gainLoss > 0 ? "text-green-600" : "text-red-600"}`}>
                                  {gainLoss.toFixed(2)}%
                                </td>
                                <td className="py-3 px-4 text-right">
                                  <Button size="sm" variant="outline">
                                    Edit
                                  </Button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-center py-8 text-gray-500">No holdings in this portfolio</p>
                  )}
                </CardContent>
              </Card>

              <div className="flex gap-3 flex-wrap">
                <Button variant="primary" onClick={() => window.location.href = "/analysis"}>
                  📊 Add Stock
                </Button>
                <Button variant="secondary">📥 Import</Button>
                <Button variant="outline">📤 Export</Button>
                <Button
                  variant="danger"
                  onClick={() => handleDeletePortfolio(selectedPortfolio.id)}
                >
                  🗑️ Delete
                </Button>
              </div>
            </>
          )}
        </>
      ) : (
        <Card className="text-center py-16">
          <p className="text-xl text-gray-600 mb-4">📭 No portfolios yet</p>
          <p className="text-gray-500 mb-6">Create your first portfolio to start tracking your investments</p>
          <Button onClick={() => setShowCreateForm(true)} variant="primary">
            ➕ Create Portfolio
          </Button>
        </Card>
      )}
    </div>
  );
}
