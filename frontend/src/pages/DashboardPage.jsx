import { useEffect, useState } from "react";
import { listDirectory } from "../api/userApi";
import { listDh, startDh, acceptDh, listRecords } from "../api/recordApi";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";

export default function DashboardPage() {
  const { profile } = useAuth();
  const [people, setPeople] = useState([]);
  const [exchanges, setExchanges] = useState([]);
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");

  const reload = () => {
    listDirectory().then((r) => setPeople(r.data)).catch(() => {});
    listDh().then((r) => setExchanges(r.data)).catch(() => {});
    listRecords().then((r) => setRecords(r.data)).catch(() => {});
  };

  useEffect(() => {
    reload();
  }, []);

  const onStart = async (peerId) => {
    setError("");
    try {
      await startDh(peerId);
      reload();
    } catch (e) {
      setError(e.response?.data?.detail || "DH start failed");
    }
  };

  const onAccept = async (id) => {
    setError("");
    try {
      await acceptDh(id);
      reload();
    } catch (e) {
      setError(e.response?.data?.detail || "DH accept failed");
    }
  };

  return (
    <div className="layout">
      <section className="panel">
        <h1>Welcome, {profile?.full_name || profile?.username}</h1>
        <p className="muted">
          Your demographics use RSA. Chart notes use secp256k1 hashed-ElGamal. Sharing requires a completed Diffie–Hellman handshake, then a re-encryption to the recipient’s ECC public key.
        </p>
        <p>
          You have <strong>{records.length}</strong> visible record(s). <Link to="/records">Open chart</Link>
        </p>
      </section>
      <section className="panel">
        <h2>Doctor–patient key exchange</h2>
        {error && <p className="error">{error}</p>}
        <div className="split">
          <div>
            <h3>Directory</h3>
            <ul className="plain">
              {people
                .filter((p) => p.id !== profile?.id)
                .map((p) => (
                  <li key={p.id}>
                    {p.username} <em>({p.role})</em>
                    <button type="button" className="ghost" onClick={() => onStart(p.id)}>
                      Start DH
                    </button>
                  </li>
                ))}
            </ul>
          </div>
          <div>
            <h3>Exchanges</h3>
            <ul className="plain">
              {exchanges.map((x) => (
                <li key={x.id}>
                  #{x.id} {x.status} · {x.initiator_id} → {x.peer_id}
                  {x.status === "pending" && x.peer_id === profile?.id && (
                    <button type="button" onClick={() => onAccept(x.id)}>
                      Accept
                    </button>
                  )}
                  {x.shared_secret_hash_hex && (
                    <code className="tiny">{x.shared_secret_hash_hex.slice(0, 16)}…</code>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
