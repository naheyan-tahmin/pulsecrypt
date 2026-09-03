import { useEffect, useState } from "react";
import ProfileView from "../components/profile/ProfileView";
import { getProfile, updateProfile } from "../api/userApi";
import { useAuth } from "../context/AuthContext";

export default function ProfilePage() {
  const { setProfile } = useAuth();
  const [profile, setLocal] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getProfile().then((r) => {
      setLocal(r.data);
      setProfile(r.data);
    });
  }, [setProfile]);

  const onSave = async (data) => {
    setSaving(true);
    setError("");
    try {
      const { data: next } = await updateProfile(data);
      setLocal(next);
      setProfile(next);
    } catch (e) {
      setError(e.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="layout">
      <section className="panel">
        <h1>Profile</h1>
        <ProfileView profile={profile} onSave={onSave} saving={saving} error={error} />
      </section>
    </div>
  );
}
