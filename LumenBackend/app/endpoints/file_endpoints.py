from flask import Blueprint, Response, request, jsonify
import os
from werkzeug.utils import secure_filename

file_blueprint = Blueprint("file", __name__)


def allowed_file(filename):
    """Check if the file is of a .parquet type."""
    return filename.lower().endswith(".parquet")


def parquet_exists(directory):
    """Check if a .parquet file already exists in the directory."""
    for filename in os.listdir(directory):
        if filename.endswith(".parquet"):
            return True
    return False


@file_blueprint.route("/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        if parquet_exists("storage/"):
            return (
                jsonify({"error": "A .parquet file already exists on the server"}),
                400,
            )

        filename = secure_filename(file.filename)
        file.save(os.path.join("storage/", filename))
        return jsonify({"success": "File uploaded successfully"}), 200

    else:
        return jsonify({"error": "Only .parquet files are allowed"}), 400


@file_blueprint.route("/", methods=["DELETE"])
def delete_file():
    deleted_files = []
    for filename in os.listdir("storage/"):
        if filename.endswith(".parquet"):
            os.remove(os.path.join("storage/", filename))
            deleted_files.append(filename)

    if deleted_files:
        return (
            jsonify(
                {"success": "Deleted .parquet file", "deleted_file": deleted_files}
            ),
            200,
        )
    else:
        return jsonify({"message": "No .parquet files found to delete"}), 200


@file_blueprint.route("/", methods=["GET"])
def check_file():
    for filename in os.listdir("storage/"):
        if filename.endswith(".parquet"):
            return jsonify({"filename": filename, "exists": True}), 200

    return jsonify({"filename": "", "exists": False}), 200


@file_blueprint.route("/download/", methods=["GET"])
def download_parquet():
    storage_path = "storage/"
    parquet_file = next(
        (file for file in os.listdir(storage_path) if file.endswith(".parquet")), None
    )

    if parquet_file is None:
        return jsonify({"error": "No .parquet file found"}), 404

    document_path = os.path.join(storage_path, parquet_file)
    file_name = os.path.basename(document_path)
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f"attachment; filename={file_name}",
    }

    def generate():
        with open(document_path, "rb") as file:
            yield from file

    return Response(generate(), headers=headers)