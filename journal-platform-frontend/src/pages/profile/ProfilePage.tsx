import React from 'react';
import { UserCircleIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';

const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="section-container py-8">
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => window.history.back()}
            className="mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back
          </Button>

          <h1 className="text-4xl font-bold gradient-text mb-2">Profile</h1>
          <p className="text-lg text-gray-600">Manage your personal information</p>
        </div>

        <div className="grid gap-8 max-w-4xl">
          <div className="glass-effect rounded-2xl border border-color-border p-8">
            <div className="flex items-center gap-6 mb-8">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt={user.full_name}
                  className="h-20 w-20 rounded-full object-cover ring-4 ring-color-border"
                />
              ) : (
                <div className="h-20 w-20 rounded-full bg-gradient-to-br from-color-primary to-color-primary-dark flex items-center justify-center">
                  <UserCircleIcon className="h-16 w-16 text-white" />
                </div>
              )}
              <div>
                <h2 className="text-2xl font-bold">{user?.full_name || 'User'}</h2>
                <p className="text-gray-600">{user?.email}</p>
                <div className="mt-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r from-amber-100 to-amber-200 text-amber-800">
                    ⭐ Premium Account
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={user?.full_name || ''}
                    readOnly
                    className="w-full px-4 py-3 rounded-xl border border-color-border bg-color-bg-muted"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    readOnly
                    className="w-full px-4 py-3 rounded-xl border border-color-border bg-color-bg-muted"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Account Type
                </label>
                <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-200">
                  <span className="text-2xl">👑</span>
                  <div>
                    <p className="font-semibold text-amber-800">Premium Member</p>
                    <p className="text-sm text-amber-600">Unlimited AI journal creation</p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Member Since
                </label>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="font-medium">{new Date().toLocaleDateString()}</p>
                  <p className="text-sm text-gray-600">Thank you for being part of Journal Craft Crew!</p>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-effect rounded-2xl border border-color-border p-8">
            <h3 className="text-xl font-bold mb-6">Account Actions</h3>
            <div className="space-y-4">
              <Button
                variant="outline"
                onClick={() => alert('Account settings coming soon!')}
                className="w-full justify-start"
              >
                ⚙️ Account Settings
              </Button>
              <Button
                variant="outline"
                onClick={() => alert('Privacy settings coming soon!')}
                className="w-full justify-start"
              >
                🔒 Privacy Settings
              </Button>
              <Button
                variant="outline"
                onClick={() => alert('Export data coming soon!')}
                className="w-full justify-start"
              >
                📥 Export My Data
              </Button>
              <div className="border-t pt-4">
                <Button
                  variant="outline"
                  onClick={handleLogout}
                  className="w-full justify-start text-red-600 hover:bg-red-50"
                >
                  🚪 Sign Out
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;