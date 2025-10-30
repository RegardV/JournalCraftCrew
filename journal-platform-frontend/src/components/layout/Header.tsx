import React, { useState } from 'react';
import { Bars3Icon, XMarkIcon, UserCircleIcon, BellIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import type { User } from '@/types';

interface HeaderProps {
  user?: User;
  onMenuToggle: () => void;
  isMobileMenuOpen: boolean;
}

const Header: React.FC<HeaderProps> = ({ user, onMenuToggle, isMobileMenuOpen }) => {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  return (
    <header className="glass-effect border-b border-color-border shadow-sm">
      <div className="section-container flex h-16 items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={onMenuToggle}
            className="md:hidden hover:bg-color-bg-muted"
            aria-label="Toggle navigation menu"
          >
            {isMobileMenuOpen ? (
              <XMarkIcon className="h-6 w-6 text-color-text" />
            ) : (
              <Bars3Icon className="h-6 w-6 text-color-text" />
            )}
          </Button>

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-color-primary to-color-primary-dark text-white shadow-lg">
              <span className="text-sm font-bold">JC</span>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Journal Craft Crew</h1>
              <p className="text-xs text-color-text-light">AI-Powered Platform</p>
            </div>
          </div>
        </div>

        <nav className="hidden lg:flex items-center gap-8">
          {[
            { name: 'Dashboard', href: '/dashboard' },
            { name: 'My Journals', href: '/projects' },
            { name: 'Themes', href: '/themes' },
            { name: 'Templates', href: '/templates' },
          ].map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="relative text-sm font-medium text-color-text-light hover:text-color-primary transition-colors duration-200 group"
            >
              {item.name}
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-color-primary transition-all duration-300 group-hover:w-full"></span>
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="relative hover:bg-color-bg-muted group"
          >
            <BellIcon className="h-5 w-5 text-color-text-light group-hover:text-color-primary" />
            {user && (
              <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-color-error animate-pulse">
                <span className="sr-only">Notifications</span>
              </span>
            )}
          </Button>

          {user ? (
            <div className="relative">
              <Button
                variant="ghost"
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center gap-3 px-4 py-2 hover:bg-color-bg-muted rounded-xl transition-all duration-200"
              >
                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="h-8 w-8 rounded-full object-cover ring-2 ring-color-border"
                  />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-color-primary to-color-primary-dark flex items-center justify-center">
                    <UserCircleIcon className="h-6 w-6 text-white" />
                  </div>
                )}
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-color-text">{user.name}</p>
                  <p className="text-xs text-color-text-light capitalize">{user.subscription}</p>
                </div>
              </Button>

              {isUserMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-64 glass-effect rounded-2xl border border-color-border shadow-xl p-2 z-50">
                  <div className="p-4 border-b border-color-border">
                    <p className="text-sm font-semibold text-color-text">{user.name}</p>
                    <p className="text-xs text-color-text-light">{user.email}</p>
                    <div className="mt-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        user.subscription === 'premium'
                          ? 'bg-gradient-to-r from-amber-100 to-amber-200 text-amber-800'
                          : 'bg-color-bg-muted text-color-text-light'
                      }`}>
                        {user.subscription === 'premium' ? '⭐ Premium' : '📝 Free'}
                      </span>
                    </div>
                  </div>

                  <div className="p-2">
                    {[
                      { name: 'Profile', href: '/profile', icon: UserCircleIcon },
                      { name: 'Settings', href: '/settings', icon: '⚙️' },
                      { name: 'Subscription', href: '/subscription', icon: '💎' },
                    ].map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                        className="flex items-center gap-3 px-4 py-3 text-sm text-color-text-light hover:bg-color-bg-muted hover:text-color-text rounded-xl transition-all duration-200"
                      >
                        <span className="text-base">{item.icon}</span>
                        {item.name}
                      </a>
                    ))}

                    <div className="border-t border-color-border mt-2 pt-2">
                      <a
                        href="/logout"
                        className="flex items-center gap-3 px-4 py-3 text-sm text-color-error hover:bg-red-50 rounded-xl transition-all duration-200"
                      >
                        <span className="text-base">🚪</span>
                        Sign Out
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                asChild
                className="hover:border-color-primary hover:text-color-primary"
              >
                <a href="/login">Sign In</a>
              </Button>
              <Button
                size="sm"
                asChild
                className="btn-primary shadow-lg hover:shadow-xl"
              >
                <a href="/register">Get Started</a>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;