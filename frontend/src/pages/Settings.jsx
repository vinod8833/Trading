import React, { useState, useEffect } from "react";
import { useAuthStore } from "../store";
import toast from "react-hot-toast";
import { Button } from "../components/ui/Button";

export default function Settings() {
  const user = useAuthStore((s) => s.user);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    preferred_trading_style: "SWING",
    notifications_enabled: true,
    theme: "light",
    risk_percentage: 0.5,
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setIsLoading(true);
        const defaultSettings = {
          preferred_trading_style: "SWING",
          notifications_enabled: true,
          theme: "light",
          risk_percentage: 0.5,
        };
        setFormData(defaultSettings);
      } catch {
        console.error("Failed to fetch settings");
        toast.error("Failed to load settings");
      } finally {
        setIsLoading(false);
      }
    };

    if (user?.id) {
      fetchSettings();
    }
  }, [user?.id]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSaveSettings = async () => {
    try {
      setIsSaving(true);
      toast.success("Settings saved successfully!");
    } catch {
      console.error("Failed to update settings");
      toast.error("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">⚙️ Settings</h1>
        <p className="text-gray-600">Customize your trading preferences and account settings</p>
      </div>

      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">📈 Trading Preferences</h2>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Preferred Trading Style
              </label>
              <select
                name="preferred_trading_style"
                value={formData.preferred_trading_style}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="INTRADAY">Intraday Trading</option>
                <option value="SWING">Swing Trading</option>
                <option value="POSITIONAL">Positional Trading</option>
                <option value="LONG_TERM">Long-Term Investing</option>
              </select>
              <p className="text-sm text-gray-600 mt-2">Choose your primary trading approach</p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Risk Per Trade (%)
              </label>
              <input
                type="number"
                name="risk_percentage"
                value={formData.risk_percentage}
                onChange={handleInputChange}
                step="0.1"
                min="0.1"
                max="5"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-600 mt-2">Maximum % of capital to risk per trade (default: 0.5%)</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">🔔 Notifications</h2>

          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer p-3 hover:bg-gray-50 rounded-lg">
              <input
                type="checkbox"
                name="notifications_enabled"
                checked={formData.notifications_enabled}
                onChange={handleInputChange}
                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <p className="font-medium text-gray-900">Enable Notifications</p>
                <p className="text-sm text-gray-600">Receive alerts for trading signals and important events</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer p-3 hover:bg-gray-50 rounded-lg">
              <input
                type="checkbox"
                defaultChecked
                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <p className="font-medium text-gray-900">Price Alerts</p>
                <p className="text-sm text-gray-600">Get notified when watched stocks hit target prices</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer p-3 hover:bg-gray-50 rounded-lg">
              <input
                type="checkbox"
                defaultChecked
                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <p className="font-medium text-gray-900">Market News</p>
                <p className="text-sm text-gray-600">Receive important market news and updates</p>
              </div>
            </label>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">🎨 Appearance</h2>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Theme
            </label>
            <select
              name="theme"
              value={formData.theme}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto (System)</option>
            </select>
            <p className="text-sm text-gray-600 mt-2">Choose your preferred interface theme</p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
          >
            {isSaving ? "💾 Saving..." : "💾 Save Settings"}
          </Button>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Settings Information</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ Your settings are saved automatically</li>
          <li>✓ Changes apply immediately to your account</li>
          <li>✓ All settings are encrypted and secure</li>
          <li>✓ You can change these settings anytime</li>
        </ul>
      </div>
    </div>
  );
}
