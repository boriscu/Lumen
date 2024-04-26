import { CheckFileResponse, DeleteFileResponse } from "../Models/file";
import api from "../api";

export const uploadFile = async (file: FormData) => {
  const response = await api.post("/file/", file);
  return response.data;
};

export const downloadFile = async () => {
  const response = await api.get("/file/download/");
  return response.data;
};

export const deleteFile = async () => {
  const response = await api.delete<DeleteFileResponse>("/file/");
  return response.data;
};

export const checkFile = async () => {
  const response = await api.get<CheckFileResponse>("/file/");
  return response.data;
};
