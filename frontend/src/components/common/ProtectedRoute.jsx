import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { isAuthed, role, loading } = useAuth();
  if (loading) return <div className="panel">Loading session…</div>;
  if (!isAuthed) return <Navigate to="/login" replace />;
  if (roles && role && !roles.includes(role)) return <Navigate to="/" replace />;
  return children;
}
