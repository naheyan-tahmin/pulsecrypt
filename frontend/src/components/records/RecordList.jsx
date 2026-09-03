import { Link } from "react-router-dom";

export default function RecordList({ records }) {
  if (!records?.length) return <p className="muted">No records yet. Create an encrypted EHR note to get started.</p>;
  return (
    <ul className="record-list">
      {records.map((r) => (
        <li key={`${r.id}-${r.shared}`}>
          <Link to={`/records/${r.id}`}>
            <strong>{r.title || "Untitled note"}</strong>
            <span>{r.diagnosis || "No diagnosis tag"}</span>
            {r.shared && <em className="pill">shared</em>}
          </Link>
        </li>
      ))}
    </ul>
  );
}
