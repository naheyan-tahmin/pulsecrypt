import axiosClient from "./axiosClient";

export const register = (payload) => axiosClient.post("/auth/register", payload);
export const login = (payload) => axiosClient.post("/auth/login", payload);
export const verify2fa = (payload) => axiosClient.post("/auth/verify-2fa", payload);
