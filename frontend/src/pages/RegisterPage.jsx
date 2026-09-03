import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import RegisterForm from "../components/auth/RegisterForm";
import TotpVerifyForm from "../components/auth/TotpVerifyForm";
import { register, verify2fa } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { persist } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [enroll, setEnroll] = useState(null);

  const onRegister = async (form) => {
    setError("");
    try {
      const { data } = await register(form);
      persist(data.access_token, data.stage);
      setEnroll(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Registration failed");
    }
  };

  const onTotp = async (code) => {
    setError("");
    try {
      const { data } = await verify2fa({ pre2fa_token: enroll.access_token, code });
      persist(data.access_token, data.stage);
      navigate("/");
    } catch (e) {
      setError(e.response?.data?.detail || "2FA failed — add the secret to your authenticator first");
    }
  };

  return (
    <div className="auth-shell">
      <div className="panel">
        <h1>Register</h1>
        {!enroll ? (
          <>
            <p className="muted">PII is RSA-encrypted before it ever reaches PostgreSQL. Passwords are salted and stretched with PulseHash.</p>
            <RegisterForm onSubmit={onRegister} error={error} />
          </>
        ) : (
          <TotpVerifyForm
            error={error}
            onSubmit={onTotp}
            hint={
              <div className="callout">
                <p>Scan or enter this TOTP secret in an authenticator app:</p>
                <code>{enroll.totp_secret}</code>
                <p className="muted break">{enroll.totp_uri}</p>
              </div>
            }
          />
        )}
        <p>
          Already enrolled? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
