import axiosClient from "./axiosClient";

export const listRecords = () => axiosClient.get("/records");
export const createRecord = (payload) => axiosClient.post("/records", payload);
export const getRecord = (id) => axiosClient.get(`/records/${id}`);
export const updateRecord = (id, payload) => axiosClient.put(`/records/${id}`, payload);
export const deleteRecord = (id) => axiosClient.delete(`/records/${id}`);
export const startDh = (peer_user_id) => axiosClient.post("/keys/dh/start", { peer_user_id });
export const acceptDh = (exchange_id) => axiosClient.post("/keys/dh/accept", { exchange_id });
export const listDh = () => axiosClient.get("/keys/dh");
export const shareRecord = (payload) => axiosClient.post("/keys/share", payload);
export const listUsersAdmin = () => axiosClient.get("/admin/users");
export const disableUser = (id) => axiosClient.post(`/admin/users/${id}/disable`);
export const enableUser = (id) => axiosClient.post(`/admin/users/${id}/enable`);
export const rotateKeys = (id) => axiosClient.post(`/admin/users/${id}/rotate-keys`);
