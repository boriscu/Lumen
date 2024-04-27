interface RoomPrediction {
  room_cnt: number;
  room_id: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 11;
  high_boundary?: number;
  low_boundary?: number;
}

interface DailyPrediction {
  date: string;
  predictions: RoomPrediction[];
}

export type PredictResponse = DailyPrediction[];
