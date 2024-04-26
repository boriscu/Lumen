from flask import Blueprint, current_app, jsonify, request
from datetime import datetime, timedelta
from app.enums.room_id_dict import scaled_to_normal_id, scaled_id_list
from app.endpoints.file_endpoints import parquet_exists
import numpy as np

predict_blueprint = Blueprint("predict", __name__)


@predict_blueprint.route("/", methods=["POST"])
def get_date_prediction():
    model = current_app.config.get("MODEL")
    if model is None:
        return jsonify({"error": "Model not found"}), 404

    if parquet_exists("storage/") is False:
        return jsonify({"error": " Parquet file not found"}), 404

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

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
        start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
        end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
        if start_date > end_date:
            return (
                jsonify({"message": "Error, start date can't be after end date"}),
                400,
            )

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
                # TODO Placeholder for actual logic to calculate weather_coef and event_coef
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
                    return jsonify({"error": f"Model prediction failed: {str(e)}"}), 500

                predictions_for_date.append(
                    {
                        "room_id": scaled_to_normal_id.get(scaled_room_id),
                        "room_cnt": room_cnt,
                    }
                )

            all_predictions.append(
                {"date": date_key, "predictions": predictions_for_date}
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(all_predictions), 200
