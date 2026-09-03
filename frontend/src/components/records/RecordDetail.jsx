export default function RecordDetail({ record, exchanges, onShare, shareError }) {
  if (!record) return null;
  return (
    <article className="stack">
      <header>
        <h2>{record.title}</h2>
        <p className="muted">
          Record #{record.id} · owner {record.owner_id} · author {record.author_id}
          {record.shared ? " · received via DH share" : ""}
        </p>
      </header>
      <p>
        <strong>Diagnosis:</strong> {record.diagnosis || "—"}
      </p>
      <pre className="note">{record.body}</pre>
      {!record.shared && (
        <form
          className="row"
          onSubmit={(e) => {
            e.preventDefault();
            const exchange_id = Number(new FormData(e.target).get("exchange_id"));
            onShare(exchange_id);
          }}
        >
          <select name="exchange_id" required>
            <option value="">Complete DH channel…</option>
            {(exchanges || [])
              .filter((x) => x.status === "complete")
              .map((x) => (
                <option key={x.id} value={x.id}>
                  Exchange #{x.id} with user {x.initiator_id === record.owner_id ? x.peer_id : x.initiator_id}
                </option>
              ))}
          </select>
          <button type="submit">Share with doctor</button>
        </form>
      )}
      {shareError && <p className="error">{shareError}</p>}
    </article>
  );
}
