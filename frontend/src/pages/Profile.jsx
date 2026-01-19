import React, { useState, useEffect } from "react";
import { useAuthStore } from "../store";
import { usersApi } from "../api/endpoints";
import toast from "react-hot-toast";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

export default function Profile() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true);
        const response = await usersApi.getProfile();
        setProfile(response.data);
        setFormData({
          first_name: response.data.first_name || "",
          last_name: response.data.last_name || "",
          email: response.data.email || "",
        });
      } catch {
        console.error("Failed to fetch profile");
        toast.error("Failed to load profile");
      } finally {
        setIsLoading(false);
      }
    };

    if (user?.id) {
      fetchProfile();
    }
  }, [user?.id]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      const response = await usersApi.updateProfile(formData);
      setProfile(response.data);
      setUser(response.data);
      toast.success("✅ Profile updated successfully!");
      setEditMode(false);
    } catch (err) {
      console.error("Failed to update profile:", err);
      toast.error(err.response?.data?.detail || "Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">👤 My Profile</h1>
        <p className="text-gray-600">Manage your account information and preferences</p>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-8 py-12">
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center text-4xl font-bold text-blue-600">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div className="text-white">
              <h2 className="text-3xl font-bold mb-1">{user?.username}</h2>
              <p className="text-blue-100">Member since {new Date(user?.date_joined || Date.now()).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="p-8">
          {editMode ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="First Name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  placeholder="Enter your first name"
                  icon="📝"
                />
                <Input
                  label="Last Name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  placeholder="Enter your last name"
                  icon="📝"
                />
              </div>
              <Input
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                icon="📧"
              />

              <div className="flex gap-3 pt-6 border-t">
                <Button
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isSaving ? "💾 Saving..." : "💾 Save Changes"}
                </Button>
                <Button
                  onClick={() => {
                    setEditMode(false);
                    setFormData({
                      first_name: profile?.first_name || "",
                      last_name: profile?.last_name || "",
                      email: profile?.email || "",
                    });
                  }}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700"
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="text-sm font-semibold text-gray-600">First Name</label>
                  <p className="text-lg text-gray-900 mt-1">{profile?.first_name || "Not set"}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Last Name</label>
                  <p className="text-lg text-gray-900 mt-1">{profile?.last_name || "Not set"}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-600">Email</label>
                <p className="text-lg text-gray-900 mt-1">{profile?.email || "Not set"}</p>
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-600">Username</label>
                <p className="text-lg text-gray-900 mt-1">{profile?.username}</p>
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-600">User ID</label>
                <p className="text-lg text-gray-900 mt-1 font-mono text-sm">{profile?.id}</p>
              </div>

              <div className="pt-6 border-t">
                <Button
                  onClick={() => setEditMode(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  ✏️ Edit Profile
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">📋 Account Information</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ Your profile is securely stored</li>
          <li>✓ Changes are saved to your account immediately</li>
          <li>✓ You can update your information anytime</li>
          <li>✓ Email verification required for email changes</li>
        </ul>
      </div>
    </div>
  );
}
