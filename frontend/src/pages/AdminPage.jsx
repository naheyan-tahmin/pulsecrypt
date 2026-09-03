import { useEffect, useState } from "react";
import AdminPanel from "../components/admin/AdminPanel";
import { disableUser, enableUser, listUsersAdmin, rotateKeys } from "../api/recordApi";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState("");

  const reload = () => listUsersAdmin().then((r) => setUsers(r.data));

  useEffect(() => {
    reload().catch(() => setMessage("Admin API denied"));
  }, []);

  return (
    <div className="layout">
      <section className="panel">
        <h1>Administration</h1>
        <AdminPanel
          users={users}
          message={message}
          onDisable={async (id) => {
            await disableUser(id);
            setMessage(`Disabled user ${id}`);
            reload();
          }}
          onEnable={async (id) => {
            await enableUser(id);
            setMessage(`Enabled user ${id}`);
            reload();
          }}
          onRotate={async (id) => {
            const { data } = await rotateKeys(id);
            setMessage(`Rotated keys for ${id}: RSA v${data.rsa_version}, ECC v${data.ecc_version}`);
            reload();
          }}
        />
      </section>
    </div>
  );
}
