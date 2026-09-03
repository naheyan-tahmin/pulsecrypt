import { useState } from "react";

export default function TotpVerifyForm({ onSubmit, error, hint }) {
  const [code, setCode] = useState("");
  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(code);
      }}
    >
      {hint}
      <label>
        Authenticator code
        <input
          inputMode="numeric"
          pattern="[0-9]{6}"
          maxLength={6}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="123456"
          required
        />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Verify and enter</button>
    </form>
  );
}
