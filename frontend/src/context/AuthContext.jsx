import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getProfile } from "../api/userApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("pc_token"));
  const [stage, setStage] = useState(() => localStorage.getItem("pc_stage"));
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(!!token && stage === "active");

  const persist = (accessToken, nextStage) => {
    setToken(accessToken);
    setStage(nextStage);
    if (accessToken) localStorage.setItem("pc_token", accessToken);
    else localStorage.removeItem("pc_token");
    if (nextStage) localStorage.setItem("pc_stage", nextStage);
    else localStorage.removeItem("pc_stage");
  };

  const logout = () => {
    persist(null, null);
    setProfile(null);
  };

  useEffect(() => {
    if (!token || stage !== "active") {
      setLoading(false);
      return;
    }
    getProfile()
      .then((res) => setProfile(res.data))
      .catch(() => logout())
      .finally(() => setLoading(false));
  }, [token, stage]);

  const value = useMemo(
    () => ({
      token,
      stage,
      profile,
      setProfile,
      loading,
      isAuthed: stage === "active" && !!token,
      role: profile?.role,
      persist,
      logout,
    }),
    [token, stage, profile, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
