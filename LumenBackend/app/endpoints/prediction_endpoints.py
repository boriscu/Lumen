from flask import Blueprint, current_app, jsonify, request
from datetime import timedelta
from app.enums.room_id_dict import scaled_to_normal_id, scaled_id_list
from app.enums.room_indices_dict import room_dict
from app.endpoints.file_endpoints import parquet_exists
import numpy as np
import pandas as pd
import joblib

features = [
    "day_of_week",
    "week_day_avg",
    "month_avg",
    "week_day_importance",
    "event",
    "occupancy_lag_1",
    "occupancy_lag_2",
    "occupancy_lag_3",
    "occupancy_lag_4",
    "occupancy_lag_5",
    "occupancy_lag_6",
    "occupancy_lag_7",
    "mean_last_7",
]

predict_blueprint = Blueprint("predict", __name__)


def predict_date(date, room_type, day_num):

    dataset = pd.read_csv(f"datasets/dataset_room_type_{room_type}.csv")
    model_path = (
        f"separated_models/model_rt_{room_type}/mapie_model_lag_{day_num}.joblib"
    )
    try:
        model = joblib.load(model_path)
    except Exception as e:
        print(e)

    day = dataset[pd.to_datetime(dataset["stay_date"]) == date]
    day_series = day[features]
    day_input = pd.DataFrame(day_series)
    m_pred, m_piss = model.predict(day_input, alpha=0.6)
    low = np.round_(m_piss[0][0][0]) if m_piss[0][0][0] > 0 else 0
    high = np.round_(m_piss[0][1][0])
    if low == high:
        high += 1
    return np.round_(m_pred), low, high


@predict_blueprint.route("/", methods=["POST"])
def get_date_prediction():

    model = current_app.config.get("MODEL")
    if model is None:
        return jsonify({"error": "Model not found"}), 404

    if parquet_exists("storage/") is False:
        return jsonify({"error": " Parquet file not found"}), 404

    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 40

    required_fields = ["start_date", "end_date"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return (
            jsonify({"error": "Missing data for fields: " + ", ".join(missing_fields)}),
            400,
        )

    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    try:

        start_date = pd.to_datetime(start_date_str, dayfirst=True)
        end_date = pd.to_datetime(end_date_str, dayfirst=True)

        if start_date > end_date:
            return (
                jsonify({"message": "Error, start date can't be after end date"}),
                400,
            )

        date_range = pd.date_range(start=start_date, end=end_date, freq="D")

        all_predictions = []

        if len(date_range) > 7:
            all_predictions = []

            for current_date in (
                start_date + timedelta(days=n)
                for n in range((end_date - start_date).days + 1)
            ):
                date_key = current_date.isoformat()
                predictions_for_date = []
                day_of_week = current_date.isoweekday()
                day_of_year = current_date.timetuple().tm_yday

                for scaled_room_id in scaled_id_list:
                    weather_coef = 0
                    event_coef = 0

                    model_input = np.array(
                        [
                            [
                                day_of_week,
                                day_of_year,
                                weather_coef,
                                scaled_room_id,
                                event_coef,
                            ]
                        ]
                    )

                    try:
                        room_cnt = round(model.predict(model_input)[0])
                    except Exception as e:
                        return (
                            jsonify({"error": f"Model prediction failed: {str(e)}"}),
                            500,
                        )

                    predictions_for_date.append(
                        {
                            "room_id": scaled_to_normal_id.get(scaled_room_id),
                            "room_cnt": room_cnt,
                        }
                    )

                all_predictions.append(
                    {"date": date_key, "predictions": predictions_for_date}
                )

        else:

            for i, date in enumerate(date_range):

                one_day_predictions = []

                for room_type_num in room_dict.values():

                    try:

                        occupancy, low, high = predict_date(date, room_type_num, i)

                    except Exception as e:
                        return (
                            jsonify({"error": f"Model prediction failed: {str(e)}"}),
                            500,
                        )

                    one_day_predictions.append(
                        {
                            "room_id": room_type_num,
                            "room_cnt": int(occupancy),
                            "low_boundary": int(low),
                            "high_boundary": int(high),
                        }
                    )

                all_predictions.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "predictions": one_day_predictions,
                    }
                )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(all_predictions), 200
