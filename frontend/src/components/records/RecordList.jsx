import { Link } from "react-router-dom";

export default function RecordList({ records, currentUserId, userRole, onEdit, onDelete }) {
  if (!records?.length) return <p className="muted">No records yet. Create an encrypted EHR note to get started.</p>;
  return (
    <ul className="record-list">
      {records.map((r) => {
        const isOwner = r.owner_id === currentUserId;
        const canEdit = isOwner || (userRole === "admin");
        const canDelete = isOwner || (userRole === "admin");
        
        return (
          <li key={`${r.id}-${r.shared}`} className="record-item">
            <Link to={`/records/${r.id}`}>
              <strong>{r.title || "Untitled note"}</strong>
              <span>{r.diagnosis || "No diagnosis tag"}</span>
              {r.shared && <em className="pill">shared</em>}
            </Link>
            <div className="record-actions">
              {canEdit && (
                <button 
                  type="button" 
                  className="ghost" 
                  onClick={(e) => { e.preventDefault(); onEdit(r.id); }}
                  title="Edit record"
                >
                  ✏️
                </button>
              )}
              {canDelete && (
                <button 
                  type="button" 
                  className="ghost danger" 
                  onClick={(e) => { e.preventDefault(); onDelete(r.id); }}
                  title="Delete record"
                >
                  🗑️
                </button>
              )}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
