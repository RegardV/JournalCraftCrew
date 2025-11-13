import React, { useState } from 'react';
import {
  CogIcon,
  BellIcon,
  ShieldCheckIcon,
  UserIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/contexts/AuthContext';

const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    marketing: false,
    updates: true,
  });

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
  ];

  return (
    <div className="min-h-screen gradient-bg p-6">
      <div className="section-container">
        <div className="mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-2">Account Settings</h1>
          <p className="text-color-text-light">Manage your profile and personal preferences</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="glass-effect rounded-xl p-4">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-color-primary to-color-primary-dark text-white shadow-lg'
                        : 'text-color-text-light hover:bg-gradient-to-r hover:from-color-bg-muted hover:to-white hover:text-color-text'
                    }`}
                  >
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="glass-effect rounded-xl p-6">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div>
                  <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
                    <UserIcon className="h-6 w-6 text-color-primary" />
                    Profile Information
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-color-text mb-2">Name</label>
                      <Input
                        value={user?.full_name || ''}
                        disabled
                        className="bg-color-bg-muted"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-color-text mb-2">Email</label>
                      <Input
                        value={user?.email || ''}
                        disabled
                        className="bg-color-bg-muted"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-color-text mb-2">Account Type</label>
                      <Input
                        value="Premium"
                        disabled
                        className="bg-color-bg-muted"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div>
                  <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
                    <BellIcon className="h-6 w-6 text-color-primary" />
                    Notification Preferences
                  </h2>
                  <div className="space-y-4">
                    {Object.entries({
                      email: 'Email notifications',
                      push: 'Push notifications',
                      marketing: 'Marketing emails',
                      updates: 'Product updates'
                    }).map(([key, label]) => (
                      <label key={key} className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={notifications[key as keyof typeof notifications]}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            [key]: e.target.checked
                          }))}
                          className="rounded text-color-primary focus:ring-color-primary"
                        />
                        <span className="text-color-text">{label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div>
                  <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
                    <ShieldCheckIcon className="h-6 w-6 text-color-primary" />
                    Security Settings
                  </h2>
                  <div className="space-y-4">
                    <div className="p-4 bg-color-bg-muted rounded-xl">
                      <h3 className="font-medium text-color-text mb-2">Password</h3>
                      <p className="text-sm text-color-text-light mb-3">Last changed recently</p>
                      <Button variant="outline" size="sm">
                        Change Password
                      </Button>
                    </div>
                    <div className="p-4 bg-color-bg-muted rounded-xl">
                      <h3 className="font-medium text-color-text mb-2">Two-Factor Authentication</h3>
                      <p className="text-sm text-color-text-light mb-3">Add an extra layer of security to your account</p>
                      <Button variant="outline" size="sm">
                        Enable 2FA
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;