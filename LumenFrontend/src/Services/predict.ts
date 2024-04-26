import api from "../api";
import { PredictResponse } from "../Models/predict";

export const getPredictions = async (start_date: string, end_date: string) => {
  const response = await api.post<PredictResponse>("/predict/", {
    start_date: start_date,
    end_date: end_date,
  });
  return response.data;
};
