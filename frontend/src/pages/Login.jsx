import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../api/endpoints";
import { useAuthStore } from "../store";
import toast from "react-hot-toast";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Alert } from "../components/ui/Common";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username || !password) {
      toast.error("Please enter username and password");
      return;
    }

    setIsLoading(true);

    try {
      const response = await authApi.login(username, password);
      const { access, refresh, user } = response.data;

      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);
      localStorage.setItem("user", JSON.stringify(user));

      setTokens(access, refresh);
      setUser(user);
      toast.success("Login successful!");
      navigate("/dashboard");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-500 to-cyan-500 flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 -right-40 w-80 h-80 bg-blue-400 rounded-full opacity-20 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-400 rounded-full opacity-20 blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-8 pt-12 pb-8 text-center">
            <div className="text-5xl font-bold text-white mb-3">📈</div>
            <h1 className="text-3xl font-bold text-white mb-2">KVK Trading</h1>
            <p className="text-blue-100">AI-Powered Stock Trading Platform</p>
          </div>

          <div className="px-8 py-8">
            <Alert
              type="info"
              title="Demo Access"
              message="Username: vinod8833 | Password: test123"
              icon="ℹ️"
              className="mb-6"
            />

            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                label="Username"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                icon="👤"
              />

              <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                icon="🔐"
              />

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-gray-700">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  Remember me
                </label>
                <button className="text-blue-600 hover:text-blue-700 font-medium">
                  Forgot password?
                </button>
              </div>

              <Button
                type="submit"
                isLoading={isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-semibold py-3 rounded-lg hover:shadow-lg transition"
              >
                {isLoading ? "Signing in..." : "Sign In"}
              </Button>
            </form>

\            <p className="text-center text-gray-600 text-sm mt-6">
              Don't have an account?{" "}
              <button className="text-blue-600 hover:text-blue-700 font-medium">
                Contact Administrator
              </button>
            </p>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="text-white">
            <div className="text-2xl mb-2">📊</div>
            <p className="text-sm font-medium">Live Analysis</p>
          </div>
          <div className="text-white">
            <div className="text-2xl mb-2">🎯</div>
            <p className="text-sm font-medium">AI Signals</p>
          </div>
          <div className="text-white">
            <div className="text-2xl mb-2">⚡</div>
            <p className="text-sm font-medium">Real-time Data</p>
          </div>
        </div>
      </div>
    </div>
  );
}
