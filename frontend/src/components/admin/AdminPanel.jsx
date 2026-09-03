export default function AdminPanel({ users, onDisable, onEnable, onRotate, message }) {
  return (
    <div className="stack">
      <p className="muted">Administrators can disable accounts and rotate wrapped RSA/ECC keys. Medical plaintext is never listed here as a bulk export.</p>
      {message && <p className="ok">{message}</p>}
      <table className="grid">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Role</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {(users || []).map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.role}</td>
              <td>{u.is_active ? "active" : "disabled"}</td>
              <td className="row">
                {u.is_active ? (
                  <button type="button" onClick={() => onDisable(u.id)}>
                    Disable
                  </button>
                ) : (
                  <button type="button" onClick={() => onEnable(u.id)}>
                    Enable
                  </button>
                )}
                <button type="button" className="ghost" onClick={() => onRotate(u.id)}>
                  Rotate keys
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
