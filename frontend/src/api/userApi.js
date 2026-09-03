import axiosClient from "./axiosClient";

export const getProfile = () => axiosClient.get("/profile");
export const updateProfile = (payload) => axiosClient.put("/profile", payload);
export const listDirectory = () => axiosClient.get("/keys/directory");
