import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Layouts
import DashboardLayout from './layouts/DashboardLayout';
import PublicLayout from './layouts/PublicLayout';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';

// Dashboard Pages
import Dashboard from './pages/dashboard/Dashboard';
import MyManuscripts from './pages/dashboard/MyManuscripts';
import SubmitManuscript from './pages/dashboard/SubmitManuscript';
import MyReviews from './pages/dashboard/MyReviews';
import ReviewManuscript from './pages/dashboard/ReviewManuscript';

// Editor Pages
import EditorDashboard from './pages/editor/EditorDashboard';
import ManuscriptList from './pages/editor/ManuscriptList';
import ManuscriptDetail from './pages/editor/ManuscriptDetail';
import ReviewerManagement from './pages/editor/ReviewerManagement';
import AssignReviewers from './pages/editor/AssignReviewers';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import UserManagement from './pages/admin/UserManagement';
import JournalSettings from './pages/admin/JournalSettings';
import Analytics from './pages/admin/Analytics';

// Public Pages
import Home from './pages/public/Home';
import ArticleView from './pages/public/ArticleView';
import IssueView from './pages/public/IssueView';
import SearchResults from './pages/public/SearchResults';
import About from './pages/public/About';
import EditorialBoard from './pages/public/EditorialBoard';

// Context
import { AuthProvider } from './context/AuthContext';

// Hooks
import { useAuth } from './hooks/useAuth';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
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
      <AuthProvider>
        <Router>
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
        </Router>
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
