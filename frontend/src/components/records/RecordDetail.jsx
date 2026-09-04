export default function RecordDetail({ record, exchanges, onShare, shareError, shareSuccess, isSharing, currentUserId, userRole, onDelete }) {
  if (!record) return null;
  const isOwner = currentUserId != null && record.owner_id === currentUserId;
  const canDelete = isOwner || (userRole === "admin");
  const complete = (exchanges || []).filter((x) => x.status === "complete");

  const otherParty = (x) => (x.initiator_id === record.owner_id ? x.peer_id : x.initiator_id);

  return (
    <article className="stack">
      <header>
        <h2>{record.title}</h2>
        <p className="muted">
          Record #{record.id} · owner {record.owner_username || `user ${record.owner_id}`} · author {record.author_username || `user ${record.author_id}`}
          {record.shared ? " · received via DH share" : ""}
        </p>
      </header>
      <p>
        <strong>Diagnosis:</strong> {record.diagnosis || "—"}
      </p>
      <pre className="note">{record.body}</pre>

      {record.shared && (
        <p className="muted">
          This copy was shared with you. You can read it, but only the owner can share it onward.
        </p>
      )}

      {isOwner && !record.shared && (
        <div className="callout">
          <p>
            <strong>Share this chart note</strong> — you are the owner. Diffie–Hellman only proves you and
            the other account have a shared channel. Then PulseCrypt re-encrypts this note with{" "}
            <em>their</em> ECC public key so they can decrypt it. The other person does not click Share;
            they later see the note in Records marked <em>shared</em>.
          </p>
          {complete.length === 0 ? (
            <p className="muted">
              No completed DH channel yet. On Dashboard, start DH with the doctor (or accept theirs), wait
              until status is <strong>complete</strong>, then come back here.
            </p>
          ) : (
            <form
              className="row"
              onSubmit={(e) => {
                e.preventDefault();
                const exchange_id = Number(new FormData(e.target).get("exchange_id"));
                onShare(exchange_id);
              }}
            >
              <select name="exchange_id" required disabled={isSharing}>
                <option value="">Give access to…</option>
                {complete.map((x) => {
                  const otherPartyId = otherParty(x);
                  const otherPartyUsername = x.initiator_id === record.owner_id 
                    ? x.peer_username 
                    : x.initiator_username;
                  return (
                    <option key={x.id} value={x.id}>
                      {otherPartyUsername || `User ${otherPartyId}`} (DH exchange #{x.id})
                    </option>
                  );
                })}
              </select>
              <button type="submit" disabled={isSharing}>
                {isSharing ? "Sharing..." : "Share with selected user"}
              </button>
            </form>
          )}
        </div>
      )}

      {!isOwner && !record.shared && (
        <p className="muted">
          Only {record.owner_username || `user ${record.owner_id}`} (the record owner) can share this note. If you are the doctor, ask
          the patient to share it after you both complete DH on the Dashboard.
        </p>
      )}

      {canDelete && onDelete && (
        <div className="row">
          <button 
            type="button" 
            className="danger" 
            onClick={() => onDelete(record.id)}
          >
            Delete this record
          </button>
        </div>
      )}

      {shareError && <p className="error">{shareError}</p>}
      {shareSuccess && <p className="success">{shareSuccess}</p>}
    </article>
  );
}
