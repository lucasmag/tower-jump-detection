from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from data_processor import DataProcessor
from tower_jump_detector import TowerJumpDetector
import io
import uuid
import threading
import time

app = Flask(__name__)
CORS(app)

# Global variables to store analysis state
# Ideally this should be a database or persistent storage
current_data = None
analysis_results = None

# Job tracking for asynchronous analysis
analysis_jobs = {}  # {job_id: {status, progress, results, error, created_at}}

# Ideally we would use a more robust job queue system, like Celery + RabbitMQ
job_lock = threading.Lock()


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Tower Jumps API is running"})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    global current_data

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    try:
        processor = DataProcessor()
        current_data = processor.load_csv_from_file(file)

        return jsonify(
            {
                "message": "File uploaded successfully",
                "records": len(current_data),
                "columns": list(current_data.columns),
                "date_range": processor.get_date_range(current_data),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


def run_analysis_background(job_id):
    """Run analysis in background thread"""
    global current_data, analysis_results

    try:
        with job_lock:
            analysis_jobs[job_id]["status"] = "running"
            analysis_jobs[job_id]["progress"] = "Initializing tower jump detector..."

        detector = TowerJumpDetector()

        with job_lock:
            analysis_jobs[job_id]["progress"] = "Creating time periods from data... (may take a while for large files)"

        # Run the analysis
        results = detector.analyze(current_data)

        with job_lock:
            analysis_jobs[job_id]["progress"] = "Generating summary statistics..."

        # Generate summary
        summary = detector.get_summary_stats(results)

        with job_lock:
            analysis_jobs[job_id]["status"] = "completed"
            analysis_jobs[job_id]["progress"] = "Analysis completed successfully"
            analysis_jobs[job_id]["results"] = {
                "message": "Analysis completed successfully",
                "total_periods": len(results),
                "tower_jumps_detected": len(results[results["IsTowerJump"] == "yes"]),
                "analysis_summary": summary,
                "results": results.to_dict("records"),
            }
            analysis_results = results  # Update global for export endpoint

    except Exception as e:
        with job_lock:
            analysis_jobs[job_id]["status"] = "failed"
            analysis_jobs[job_id]["error"] = str(e)


@app.route("/api/analyze", methods=["POST"])
def analyze_data():
    global current_data

    if current_data is None:
        return (
            jsonify({"error": "No data uploaded. Please upload a CSV file first."}),
            400,
        )

    # Create a new job
    job_id = str(uuid.uuid4())

    with job_lock:
        analysis_jobs[job_id] = {
            "status": "pending",
            "progress": "Analysis job created",
            "results": None,
            "error": None,
            "created_at": time.time(),
        }

    # Start background analysis
    thread = threading.Thread(target=run_analysis_background, args=(job_id,))
    thread.daemon = True
    thread.start()

    return jsonify(
        {
            "job_id": job_id,
            "status": "pending",
            "message": "Analysis started. Use the job_id to check status.",
        }
    )


@app.route("/api/status/<job_id>", methods=["GET"])
def get_job_status(job_id):
    """Get the status of an analysis job"""
    with job_lock:
        if job_id not in analysis_jobs:
            return jsonify({"error": "Job not found"}), 404

        job = analysis_jobs[job_id]

        response = {
            "job_id": job_id,
            "status": job["status"],
            "progress": job["progress"],
            "created_at": job["created_at"],
        }

        if job["status"] == "completed":
            response["results"] = job["results"]
        elif job["status"] == "failed":
            response["error"] = job["error"]

        return jsonify(response)


@app.route("/api/results", methods=["GET"])
def get_results():
    global analysis_results

    if analysis_results is None:
        return (
            jsonify({"error": "No analysis results available. Run analysis first."}),
            400,
        )

    # Get pagination parameters
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    filter_type = request.args.get("filter", "all")
    sort_by = request.args.get("sort_by", "TimeStart")
    sort_order = request.args.get("sort_order", "asc")

    # Apply filtering
    filtered_results = analysis_results
    if filter_type == "jumps":
        filtered_results = analysis_results[analysis_results["IsTowerJump"] == "yes"]
    elif filter_type == "normal":
        filtered_results = analysis_results[analysis_results["IsTowerJump"] == "no"]

    # Apply sorting
    ascending = sort_order == "asc"
    if sort_by in filtered_results.columns:
        filtered_results = filtered_results.sort_values(by=sort_by, ascending=ascending)

    # Calculate pagination
    total_count = len(filtered_results)
    total_pages = (total_count + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Get paginated results
    paginated_results = filtered_results.iloc[start_idx:end_idx]
    results_dict = paginated_results.to_dict("records")

    return jsonify(
        {
            "results": results_dict,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }
    )


@app.route("/api/export", methods=["GET"])
def export_results():
    global analysis_results

    if analysis_results is None:
        return (
            jsonify({"error": "No analysis results available. Run analysis first."}),
            400,
        )

    try:
        # Create a temporary file for the CSV export
        output = io.StringIO()
        analysis_results.to_csv(output, index=False)
        output.seek(0)

        # Create a BytesIO object for Flask to send
        mem = io.BytesIO()
        mem.write(output.getvalue().encode("utf-8"))
        mem.seek(0)

        return send_file(
            mem,
            mimetype="text/csv",
            as_attachment=True,
            download_name="tower_jumps_analysis_result.csv",
        )

    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
