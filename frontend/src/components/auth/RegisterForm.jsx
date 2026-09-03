import { useState } from "react";

export default function RegisterForm({ onSubmit, error }) {
  const [form, setForm] = useState({
    username: "",
    password: "",
    email: "",
    phone: "",
    full_name: "",
    national_id: "",
    role: "patient",
  });
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
    >
      <label>
        Full name
        <input value={form.full_name} onChange={set("full_name")} required />
      </label>
      <label>
        Username
        <input value={form.username} onChange={set("username")} required minLength={3} />
      </label>
      <label>
        Email
        <input type="email" value={form.email} onChange={set("email")} required />
      </label>
      <label>
        Phone
        <input value={form.phone} onChange={set("phone")} />
      </label>
      <label>
        National ID / SSN
        <input value={form.national_id} onChange={set("national_id")} />
      </label>
      <label>
        Password
        <input type="password" value={form.password} onChange={set("password")} required minLength={8} />
      </label>
      <label>
        Role
        <select value={form.role} onChange={set("role")}>
          <option value="patient">Patient</option>
          <option value="doctor">Doctor</option>
        </select>
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Create encrypted account</button>
    </form>
  );
}
