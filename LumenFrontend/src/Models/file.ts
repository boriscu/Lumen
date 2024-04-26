export interface DeleteFileResponse {
  deleted_file: string[];
  success: string;
}

export interface CheckFileResponse {
  exists: boolean;
  filename: string;
}
