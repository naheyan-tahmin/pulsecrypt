import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import LoginForm from "../components/auth/LoginForm";
import TotpVerifyForm from "../components/auth/TotpVerifyForm";
import { login, verify2fa } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { persist } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [pre2fa, setPre2fa] = useState(null);

  const onLogin = async (creds) => {
    setError("");
    try {
      const { data } = await login(creds);
      persist(data.access_token, data.stage);
      setPre2fa(data.access_token);
    } catch (e) {
      setError(e.response?.data?.detail || "Login failed");
    }
  };

  const onTotp = async (code) => {
    setError("");
    try {
      const { data } = await verify2fa({ pre2fa_token: pre2fa, code });
      persist(data.access_token, data.stage);
      navigate("/");
    } catch (e) {
      setError(e.response?.data?.detail || "2FA failed");
    }
  };

  return (
    <div className="auth-shell">
      <div className="panel">
        <h1>Sign in</h1>
        <p className="muted">Password first, then TOTP. Session tokens are RSA-encrypted and HMAC-tagged.</p>
        {!pre2fa ? (
          <LoginForm onSubmit={onLogin} error={error} />
        ) : (
          <TotpVerifyForm onSubmit={onTotp} error={error} />
        )}
        <p>
          New here? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
