import React, { useState } from 'react';
import { Key, Eye, EyeOff, Trash2, Download, Shield, LogOut, User, Mail, Lock } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const AccountSettings: React.FC = () => {
  const { user, logout } = useAuth();
  const [showApiKey, setShowApiKey] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Mock API key for now - in real implementation this would come from backend
  const userApiKey = 'sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

  const handleSaveApiKey = async () => {
    setIsLoading(true);
    try {
      // TODO: Implement actual API call to save API key
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setMessage({ type: 'success', text: 'API key saved successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save API key. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteApiKey = async () => {
    setIsLoading(true);
    try {
      // TODO: Implement actual API call to delete API key
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setApiKey('');
      setMessage({ type: 'success', text: 'API key removed successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to remove API key. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') {
      setMessage({ type: 'error', text: 'Please type DELETE to confirm account deletion.' });
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Implement actual API call to delete account
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      await logout();
      setMessage({ type: 'success', text: 'Account deleted successfully.' });
      // Redirect to home page would happen automatically due to logout
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete account. Please contact support.' });
      setIsLoading(false);
    }
  };

  const handleExportData = async () => {
    setIsLoading(true);
    try {
      // TODO: Implement actual data export
      const userData = {
        id: user?.id,
        email: user?.email,
        full_name: user?.full_name,
        created_at: user?.created_at,
        projects: [], // Would come from backend
        journals: [], // Would come from backend
        export_date: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(userData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `journal-craft-crew-data-${user?.id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setMessage({ type: 'success', text: 'Data exported successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to export data. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h2 className="text-heading mb-2">Account Settings</h2>
        <p className="text-gray-600">Manage your account settings, API keys, and privacy options.</p>
      </div>

      {/* Message Display */}
      {message.text && (
        <div className={`p-4 rounded-xl mb-6 ${
          message.type === 'success'
            ? 'bg-green-50 text-green-800 border border-green-200'
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Profile Information */}
      <div className="content-card mb-6">
        <h3 className="text-subheading font-semibold mb-4">Profile Information</h3>

        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-sm text-gray-600">{user?.email}</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Account ID</p>
              <p className="font-mono text-sm">{user?.id}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Member Since</p>
              <p className="text-sm">{new Date().toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* API Key Management */}
      <div className="content-card mb-6">
        <h3 className="text-subheading font-semibold mb-4 flex items-center gap-2">
          <Key className="w-5 h-5" />
          API Key Management
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              OpenAI API Key
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={userApiKey || apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your OpenAI API key"
                  className="input pr-11"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showApiKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {userApiKey && (
                <button
                  onClick={handleDeleteApiKey}
                  disabled={isLoading}
                  className="btn btn-outline px-4"
                  title="Remove API key"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Your API key is used to generate AI-powered journals. Keep it secure and never share it publicly.
            </p>
          </div>

          <button
            onClick={handleSaveApiKey}
            disabled={isLoading || !apiKey.trim()}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Saving...' : 'Save API Key'}
          </button>
        </div>
      </div>

      {/* Data Management */}
      <div className="content-card mb-6">
        <h3 className="text-subheading font-semibold mb-4 flex items-center gap-2">
          <Download className="w-5 h-5" />
          Data Management
        </h3>

        <div className="space-y-4">
          <div>
            <p className="text-gray-600 mb-4">
              Export all your personal data, including journals, projects, and settings.
            </p>
            <button
              onClick={handleExportData}
              disabled={isLoading}
              className="btn btn-outline flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              {isLoading ? 'Exporting...' : 'Export My Data'}
            </button>
          </div>
        </div>
      </div>

      {/* Account Security */}
      <div className="content-card mb-6">
        <h3 className="text-subheading font-semibold mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Account Security
        </h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Password</p>
              <p className="text-sm text-gray-600">Last changed recently</p>
            </div>
            <button className="btn btn-outline">
              Change Password
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-gray-600">Add an extra layer of security</p>
            </div>
            <button className="btn btn-outline">
              Enable 2FA
            </button>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="content-card border-red-200">
        <h3 className="text-subheading font-semibold mb-4 text-red-600 flex items-center gap-2">
          <Trash2 className="w-5 h-5" />
          Danger Zone
        </h3>

        <div className="space-y-4">
          <div>
            <p className="text-gray-600 mb-4">
              Once you delete your account, there is no going back. Please be certain.
            </p>

            {!showDeleteConfirm ? (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="btn bg-red-600 text-white hover:bg-red-700 border-0"
              >
                Delete Account
              </button>
            ) : (
              <div className="p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-red-800 mb-4">
                  To confirm deletion, type <strong>DELETE</strong> in all caps below:
                </p>
                <input
                  type="text"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Type DELETE to confirm"
                  className="input mb-4"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleDeleteAccount}
                    disabled={isLoading || deleteConfirmText !== 'DELETE'}
                    className="btn bg-red-600 text-white hover:bg-red-700 border-0 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Deleting...' : 'Delete My Account'}
                  </button>
                  <button
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setDeleteConfirmText('');
                    }}
                    className="btn btn-outline"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sign Out */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <button
          onClick={logout}
          className="btn btn-outline flex items-center gap-2"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default AccountSettings;