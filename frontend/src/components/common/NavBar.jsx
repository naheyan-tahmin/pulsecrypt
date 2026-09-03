import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function NavBar() {
  const { isAuthed, profile, logout, role } = useAuth();
  if (!isAuthed) return null;
  return (
    <header className="nav">
      <NavLink to="/" className="brand">
        PulseCrypt
      </NavLink>
      <nav>
        <NavLink to="/">Dashboard</NavLink>
        <NavLink to="/records">Records</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        {role === "admin" && <NavLink to="/admin">Admin</NavLink>}
      </nav>
      <div className="nav-user">
        <span>{profile?.full_name || profile?.username}</span>
        <em>{role}</em>
        <button className="linkish" onClick={logout}>
          Sign out
        </button>
      </div>
    </header>
  );
}
