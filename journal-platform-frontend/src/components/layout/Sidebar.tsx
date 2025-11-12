import React from 'react';
import {
  HomeIcon,
  BookOpenIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  CogIcon,
  UserGroupIcon,
  ChartBarIcon,
  FolderIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  SparklesIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, current: false },
  { name: 'My Journals', href: '/dashboard?view=library', icon: BookOpenIcon, current: false },
  { name: 'Themes', href: '/themes', icon: PaintBrushIcon, current: false },
  { name: 'Templates', href: '/templates', icon: DocumentTextIcon, current: false },
  { name: 'Analytics', href: '/dashboard?view=analytics', icon: ChartBarIcon, current: false },
];

const secondaryNavigation = [
  { name: 'Settings', href: '/settings', icon: CogIcon },
  { name: 'AI Assistant', href: '/ai-workflow', icon: SparklesIcon },
];

const recentProjects = [
  // Remove fake projects - will be populated from API
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, className }) => {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-80 transform glass-effect border-r border-color-border transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:z-auto',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          className
        )}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-20 items-center justify-between px-8 border-b border-color-border bg-gradient-to-r from-white to-color-bg-muted">
            <div>
              <h2 className="text-lg font-bold gradient-text">Navigation</h2>
              <p className="text-xs text-color-text-light">Explore your workspace</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="md:hidden hover:bg-color-bg-muted rounded-xl"
            >
              <XMarkIcon className="h-6 w-6 text-color-text" />
            </Button>
          </div>

          {/* Quick Actions */}
          <div className="p-6 border-b border-color-border bg-gradient-to-br from-color-bg-muted to-white">
            <Button className="w-full justify-start btn-primary shadow-lg hover:shadow-xl" asChild>
              <a href="/ai-workflow" className="flex items-center gap-3">
                <PlusIcon className="h-5 w-5" />
                <div className="text-left">
                  <div className="font-medium">Create New Journal</div>
                  <div className="text-xs opacity-90">Start with AI assistance</div>
                </div>
              </a>
            </Button>
          </div>

          {/* Search */}
          <div className="p-6 border-b border-color-border">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-color-text-light" />
              <Input
                placeholder="Search your journals..."
                className="pl-12 pr-4 py-3 border-color-border bg-color-bg-muted rounded-xl focus:border-color-primary focus:ring-2 focus:ring-color-primary/20"
              />
            </div>
          </div>

          {/* Main Navigation */}
          <nav className="flex-1 space-y-2 px-4 py-6 overflow-y-auto">
            <div className="space-y-2">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center gap-4 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 hover:bg-gradient-to-r hover:from-color-bg-muted hover:to-white hover:shadow-md',
                    item.current
                      ? 'bg-gradient-to-r from-color-primary to-color-primary-dark text-white shadow-lg'
                      : 'text-color-text-light hover:text-color-text'
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-5 w-5 flex-shrink-0',
                      item.current
                        ? 'text-white'
                        : 'text-color-text-light group-hover:text-color-primary'
                    )}
                  />
                  <span>{item.name}</span>
                  {item.current && (
                    <div className="ml-auto w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  )}
                </a>
              ))}
            </div>

            <div className="pt-8 mt-8 border-t border-color-border">
              <h3 className="px-4 text-xs font-bold text-color-text-light uppercase tracking-wider mb-4">
                Recent Projects
              </h3>
              <div className="space-y-2">
                {recentProjects.map((project) => (
                  <a
                    key={project.id}
                    href={`/projects/${project.id}`}
                    className="group flex items-center gap-3 px-4 py-3 text-sm rounded-xl transition-all duration-200 hover:bg-gradient-to-r hover:from-color-bg-muted hover:to-white hover:shadow-sm"
                  >
                    <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-color-primary/20 to-color-primary/10 flex items-center justify-center group-hover:from-color-primary/30 group-hover:to-color-primary/20 transition-all duration-200">
                      <FolderIcon className="h-5 w-5 text-color-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-color-text truncate">{project.name}</p>
                      <p className="text-xs text-color-text-light">{project.lastEdited}</p>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          </nav>

          {/* Secondary Navigation */}
          <div className="border-t border-color-border p-4 bg-gradient-to-r from-color-bg-muted to-white">
            <div className="space-y-1">
              {secondaryNavigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="group flex items-center gap-3 px-4 py-3 text-sm rounded-xl text-color-text-light hover:bg-white hover:shadow-sm transition-all duration-200"
                >
                  <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-color-accent/20 to-color-accent/10 flex items-center justify-center group-hover:from-color-accent/30 group-hover:to-color-accent/20 transition-all duration-200">
                    <item.icon className="h-4 w-4 text-color-accent" />
                  </div>
                  <span className="font-medium">{item.name}</span>
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;