import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { JournalCreationProvider } from '@/contexts/JournalCreationContext';
import Header from '@/components/layout/Header';
import Sidebar from '@/components/layout/Sidebar';
import Dashboard from '@/components/dashboard/Dashboard';
import SplashScreen from '@/components/splash/SplashScreen';
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage';
import TermsPage from '@/pages/legal/TermsPage';
import PrivacyPage from '@/pages/legal/PrivacyPage';
import ProfilePage from '@/pages/profile/ProfilePage';
import ProjectsPage from '@/pages/projects/ProjectsPage';
import ThemesPage from '@/pages/themes/ThemesPage';
import TemplatesPage from '@/pages/templates/TemplatesPage';
import SubscriptionPage from '@/pages/subscription/SubscriptionPage';
import ConnectionStatus from '@/components/ui/ConnectionStatus';
import PerformanceMonitor from '@/components/ui/PerformanceMonitor';
import ProjectDetail from '@/components/projects/ProjectDetail';
import AIWorkflowPage from '@/pages/ai-workflow/AIWorkflowPage';
import SettingsPage from '@/pages/settings/SettingsPage';

// Authenticated routes component
function AuthenticatedRoutes() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Convert user from auth context to the format expected by components
  const formatUserForComponents = (authUser: any) => ({
    id: authUser.id,
    email: authUser.email,
    name: authUser.full_name,
    avatar: undefined,
    subscription: 'premium' as const,
    createdAt: new Date(),
    lastActiveAt: new Date(),
    preferences: {
      theme: 'light' as const,
      language: 'en',
      timezone: 'UTC',
      notifications: {
        email: true,
        push: true,
        marketing: false,
        updates: true,
      },
      privacy: {
        profileVisibility: 'private' as const,
        shareAnalytics: true,
        allowCollaboration: true,
      },
    },
  });

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-6"></div>
          <p className="text-color-text-light text-lg">Welcome to Journal Craft Crew</p>
          <p className="text-color-text-light text-sm mt-2">Loading your workspace...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return (
    <div className="min-h-screen gradient-bg">
      <div className="header-container">
        <div className="section-container">
          <Header
            user={user ? formatUserForComponents(user) : undefined}
            onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
            isMobileMenuOpen={isSidebarOpen}
          />
        </div>
      </div>

      <div className="flex">
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main className="flex-1 p-6 md:ml-80">
          <div className="section-container">
            <JournalCreationProvider>
              <Dashboard user={user ? formatUserForComponents(user) : undefined} />
            </JournalCreationProvider>
          </div>
        </main>
      </div>

      <ConnectionStatus />
      <PerformanceMonitor />
    </div>
  );
}

// Authenticated wrapper components for new routes
function ProfilePageWrapper() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  return <ProfilePage />;
}

function ProjectsPageWrapper() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Redirect to dashboard if authenticated - the projects functionality is in the dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  // If not authenticated, redirect to login
  return <Navigate to="/auth/login" replace />;
}

function ThemesPageWrapper() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  return <ThemesPage />;
}

function TemplatesPageWrapper() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  return <TemplatesPage />;
}

function SubscriptionPageWrapper() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  return <SubscriptionPage />;
}

function SettingsPageWrapper() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  return <SettingsPage />;
}

function ProjectDetailWrapper() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return <ProjectDetail />;
}

function AIWorkflowPageWrapper() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return <AIWorkflowPage />;
}

// Main App component with routing
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<SplashScreen />} />
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />

          {/* Legal Pages */}
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />

          {/* Protected Routes */}
          <Route path="/dashboard/*" element={<AuthenticatedRoutes />} />
          <Route path="/profile" element={<ProfilePageWrapper />} />
          <Route path="/projects" element={<ProjectsPageWrapper />} />
          <Route path="/library/projects/:id" element={<ProjectDetailWrapper />} />
          <Route path="/ai-workflow" element={<AIWorkflowPageWrapper />} />
          <Route path="/ai-workflow/:workflowId" element={<AIWorkflowPageWrapper />} />
          <Route path="/themes" element={<ThemesPageWrapper />} />
          <Route path="/templates" element={<TemplatesPageWrapper />} />
          <Route path="/subscription" element={<SubscriptionPageWrapper />} />
          <Route path="/settings" element={<SettingsPageWrapper />} />

          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
