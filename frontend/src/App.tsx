import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Context
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

// Hooks
import { useAuth } from './hooks/useAuth';

// Loading component
const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
  </div>
);

// Lazy-loaded Layouts
const DashboardLayout = lazy(() => import('./layouts/DashboardLayout'));
const PublicLayout = lazy(() => import('./layouts/PublicLayout'));

// Lazy-loaded Auth Pages
const Login = lazy(() => import('./pages/auth/Login'));
const Register = lazy(() => import('./pages/auth/Register'));
const ForgotPassword = lazy(() => import('./pages/auth/ForgotPassword'));

// Lazy-loaded Dashboard Pages
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard'));
const MyManuscripts = lazy(() => import('./pages/dashboard/MyManuscripts'));
const SubmitManuscript = lazy(() => import('./pages/dashboard/SubmitManuscript'));
const MyReviews = lazy(() => import('./pages/dashboard/MyReviews'));
const ReviewManuscript = lazy(() => import('./pages/dashboard/ReviewManuscript'));

// Lazy-loaded Editor Pages
const EditorDashboard = lazy(() => import('./pages/editor/EditorDashboard'));
const ManuscriptList = lazy(() => import('./pages/editor/ManuscriptList'));
const ManuscriptDetail = lazy(() => import('./pages/editor/ManuscriptDetail'));
const ReviewerManagement = lazy(() => import('./pages/editor/ReviewerManagement'));
const AssignReviewers = lazy(() => import('./pages/editor/AssignReviewers'));

// Lazy-loaded Admin Pages
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const UserManagement = lazy(() => import('./pages/admin/UserManagement'));
const JournalSettings = lazy(() => import('./pages/admin/JournalSettings'));
const Analytics = lazy(() => import('./pages/admin/Analytics'));

// Lazy-loaded Public Pages
const Home = lazy(() => import('./pages/public/Home'));
const ArticleView = lazy(() => import('./pages/public/ArticleView'));
const IssueView = lazy(() => import('./pages/public/IssueView'));
const SearchResults = lazy(() => import('./pages/public/SearchResults'));
const About = lazy(() => import('./pages/public/About'));
const EditorialBoard = lazy(() => import('./pages/public/EditorialBoard'));

// Optimized QueryClient configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,  // 5 minutes - data stays fresh longer
      cacheTime: 10 * 60 * 1000,  // 10 minutes - cache persists longer
      refetchOnMount: false,      // Don't refetch on mount if data is fresh
      refetchOnReconnect: true,   // Refetch when network reconnects
    },
    mutations: {
      retry: 1,
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode; roles?: string[] }> = ({
  children,
  roles,
}) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/dashboard" />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <Suspense fallback={<LoadingFallback />}>
              <Routes>
                {/* Public Routes */}
                <Route element={<PublicLayout />}>
              <Route path="/" element={<Home />} />
              <Route path="/article/:manuscriptId" element={<ArticleView />} />
              <Route path="/issue/:volume/:issue" element={<IssueView />} />
              <Route path="/search" element={<SearchResults />} />
              <Route path="/about" element={<About />} />
              <Route path="/editorial-board" element={<EditorialBoard />} />
            </Route>

            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            {/* Author Dashboard */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="manuscripts" element={<MyManuscripts />} />
              <Route path="manuscripts/submit" element={<SubmitManuscript />} />
              <Route path="reviews" element={<MyReviews />} />
              <Route path="reviews/:reviewId" element={<ReviewManuscript />} />
            </Route>

            {/* Editor Dashboard */}
            <Route
              path="/editor"
              element={
                <ProtectedRoute roles={['editor_in_chief', 'associate_editor', 'admin']}>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<EditorDashboard />} />
              <Route path="manuscripts" element={<ManuscriptList />} />
              <Route path="manuscripts/:manuscriptId" element={<ManuscriptDetail />} />
              <Route path="reviewers" element={<ReviewerManagement />} />
              <Route
                path="manuscripts/:manuscriptId/assign-reviewers"
                element={<AssignReviewers />}
              />
            </Route>

            {/* Admin Dashboard */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute roles={['admin']}>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<UserManagement />} />
              <Route path="settings" element={<JournalSettings />} />
              <Route path="analytics" element={<Analytics />} />
            </Route>

                {/* 404 */}
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
            </Suspense>
          </Router>
          <Toaster position="top-right" />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
