import { useState } from "react";

export default function LoginForm({ onSubmit, error }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ username, password });
      }}
    >
      <label>
        Username
        <input value={username} onChange={(e) => setUsername(e.target.value)} required />
      </label>
      <label>
        Password
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Continue to 2FA</button>
    </form>
  );
}
