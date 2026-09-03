import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import NavBar from "./components/common/NavBar";
import ProtectedRoute from "./components/common/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import RecordPage from "./pages/RecordPage";
import AdminPage from "./pages/AdminPage";
import ProfilePage from "./pages/ProfilePage";

function Shell() {
  const { isAuthed } = useAuth();
  return (
    <>
      <NavBar />
      <main>
        <Routes>
          <Route path="/login" element={isAuthed ? <Navigate to="/" /> : <LoginPage />} />
          <Route path="/register" element={isAuthed ? <Navigate to="/" /> : <RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/records"
            element={
              <ProtectedRoute>
                <RecordPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/records/:id"
            element={
              <ProtectedRoute>
                <RecordPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute roles={["admin"]}>
                <AdminPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </AuthProvider>
  );
}
