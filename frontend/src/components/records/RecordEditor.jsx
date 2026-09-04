import { useState } from "react";

export default function RecordEditor({ initial, onSubmit, error }) {
  const [title, setTitle] = useState(initial?.title || "");
  const [diagnosis, setDiagnosis] = useState(initial?.diagnosis || "");
  const [body, setBody] = useState(initial?.body || "");
  const [ownerId, setOwnerId] = useState(initial?.owner_id || "");
  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        const payload = { title, diagnosis, body };
        if (ownerId) payload.owner_id = Number(ownerId);
        onSubmit(payload);
      }}
    >
      <label>
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Diagnosis
        <input value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} />
      </label>
      <label>
        Clinical note
        <textarea rows={8} value={body} onChange={(e) => setBody(e.target.value)} required />
      </label>
      <label>
        Patient user id (doctors only, optional)
        <input value={ownerId} onChange={(e) => setOwnerId(e.target.value)} placeholder="Leave blank for yourself" title="Enter patient user ID" />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Save (ECC-encrypted)</button>
    </form>
  );
}
