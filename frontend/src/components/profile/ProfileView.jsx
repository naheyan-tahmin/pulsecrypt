export default function ProfileView({ profile, onSave, saving, error }) {
  if (!profile) return null;
  const fields = [
    ["full_name", "Full name"],
    ["email", "Email"],
    ["phone", "Phone"],
    ["national_id", "National ID"],
    ["address", "Address"],
    ["blood_type", "Blood type"],
    ["date_of_birth", "Date of birth"],
    ["emergency_contact", "Emergency contact"],
  ];
  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(e.target).entries());
        onSave(data);
      }}
    >
      <p className="muted">
        Username <strong>{profile.username}</strong> · role <strong>{profile.role}</strong> — stored under RSA, decrypted only for this session.
      </p>
      {fields.map(([name, label]) => (
        <label key={name}>
          {label}
          <input name={name} defaultValue={profile[name] || ""} />
        </label>
      ))}
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={saving}>
        {saving ? "Encrypting…" : "Save encrypted profile"}
      </button>
    </form>
  );
}
