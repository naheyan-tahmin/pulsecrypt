import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import RecordList from "../components/records/RecordList";
import RecordEditor from "../components/records/RecordEditor";
import RecordDetail from "../components/records/RecordDetail";
import { createRecord, getRecord, listDh, listRecords, shareRecord, updateRecord, deleteRecord } from "../api/recordApi";
import { useAuth } from "../context/AuthContext";

function apiError(e, fallback) {
  const d = e.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg || JSON.stringify(x)).join("; ");
  return fallback;
}

export default function RecordPage() {
  const { profile } = useAuth();
  const { id } = useParams();
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [current, setCurrent] = useState(null);
  const [exchanges, setExchanges] = useState([]);
  const [mode, setMode] = useState("list");
  const [error, setError] = useState("");
  const [shareError, setShareError] = useState("");
  const [shareSuccess, setShareSuccess] = useState("");
  const [isSharing, setIsSharing] = useState(false);

  const reload = () => listRecords().then((r) => setRecords(r.data));

  useEffect(() => {
    reload();
    listDh().then((r) => setExchanges(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!id) {
      setCurrent(null);
      setMode("list");
      return;
    }
    getRecord(id)
      .then((r) => {
        setCurrent(r.data);
        setMode("detail");
      })
      .catch((e) => setError(e.response?.data?.detail || "Unable to decrypt record"));
  }, [id]);

  const onCreate = async (payload) => {
    setError("");
    try {
      const { data } = await createRecord(payload);
      await reload();
      navigate(`/records/${data.id}`);
    } catch (e) {
      setError(apiError(e, "Create failed"));
    }
  };

  const onUpdate = async (payload) => {
    setError("");
    try {
      const { data } = await updateRecord(id, payload);
      setCurrent(data);
      setMode("detail");
      await reload();
    } catch (e) {
      setError(apiError(e, "Update failed"));
    }
  };

  const onShare = async (exchange_id) => {
    setShareError("");
    setShareSuccess("");
    setIsSharing(true);
    try {
      await shareRecord({ record_id: Number(id), exchange_id });
      setShareSuccess("Record successfully shared with the user!");
      setShareError("");
    } catch (e) {
      setShareError(apiError(e, "Share failed"));
    } finally {
      setIsSharing(false);
    }
  };

  const onEditRecord = (recordId) => {
    navigate(`/records/${recordId}`);
  };

  const onDeleteRecord = async (recordId) => {
    if (!confirm("Are you sure you want to delete this record?")) return;
    setError("");
    try {
      await deleteRecord(recordId);
      await reload();
    } catch (e) {
      setError(apiError(e, "Delete failed"));
    }
  };

  return (
    <div className="layout">
      <section className="panel">
        <div className="row-between">
          <h1>Medical records</h1>
          <button type="button" className="ghost" onClick={() => { setMode("create"); navigate("/records"); }}>
            New note
          </button>
        </div>
        {mode === "list" && (
          <RecordList 
            records={records} 
            currentUserId={profile?.id}
            userRole={profile?.role}
            onEdit={onEditRecord}
            onDelete={onDeleteRecord}
          />
        )}
        {mode === "create" && <RecordEditor onSubmit={onCreate} error={error} />}
        {mode === "detail" && current && (
          <>
            <RecordDetail
              record={current}
              exchanges={exchanges}
              onShare={onShare}
              shareError={shareError}
              shareSuccess={shareSuccess}
              isSharing={isSharing}
              currentUserId={profile?.id}
              userRole={profile?.role}
              onDelete={onDeleteRecord}
            />
            {(current.owner_id === profile?.id || profile?.role === "admin") && (
              <>
                <h3>Edit</h3>
                <RecordEditor initial={current} onSubmit={onUpdate} error={error} />
              </>
            )}
          </>
        )}
        {error && mode === "list" && <p className="error">{error}</p>}
      </section>
    </div>
  );
}
