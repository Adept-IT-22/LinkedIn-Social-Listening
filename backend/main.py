#This is the main module

import json
import psycopg
import logging
from typing import Dict, Any
from backend.config import logging_config
from backend.config.app_config import DB_CONFIG
from backend.services.icp_scoring import icp_scoring
from flask import Flask, jsonify, Response, stream_with_context, request, send_file
from flask_cors import CORS
from backend.services.icp_scores.total_score import icp_scorer
from backend.services.download_excel import save_as_excel
from backend.services.db_service import check_if_duplicate_post_exists, add_data_into_database

#DB Configs
host = DB_CONFIG.get("host")
port = DB_CONFIG.get("port")
user_name = DB_CONFIG.get("user")
password = DB_CONFIG.get("password")
db_name = DB_CONFIG.get("name")

#create a flask app
app = Flask(__name__)
CORS(app)

#initialize logging configs
logging_config.configure_logging()

#create module level logger
logger = logging.getLogger(__name__)
    
#minimum score for a lead to become qualified
MIN_SCORE = 60

#store all icp_scoring results
all_authors_cache = []

@app.route("/", methods=['GET'])
def landing_page():
    return jsonify({"message": "Gunicorn Works! Flask is up & running!"})

#endpoint to retrieve qualified leads based on icp scoring.
@app.route('/lead-data', methods=['GET'])
def lead_data() -> Dict[str, Any]:

    try:
        logger.info("Starting process of fetching lead data...")
        
        #run icp scoring. it will call get authors which will call search posts
        lead_data = icp_scoring(min_score=MIN_SCORE)

        logger.info(
           "Successfully retrieved %d qualified leads", len(lead_data),
           extra={"metrics": {
               "Qualified Leads": len(lead_data)
           }} 
        )

        return jsonify({
            "status": "success",
            "count": len(lead_data),
            "data": lead_data
        })

    except Exception as e:
        logging.error(
            "Lead data could not be retrieved",
            exc_info=True,
            extra={"error_details": str(e)}
        )
        return jsonify({
            "status": "error", 
            "message": "Failed to retrieve lead data",
        }), 500

@app.route('/stream-leads', methods=['GET'])
def stream_leads():
    def generate():
        try:
            for scored_lead in icp_scoring(min_score=MIN_SCORE):
                score = scored_lead.get("score", 0)
                if "error" in scored_lead:
                    yield f"data: {json.dumps(scored_lead)}\n\n"
                else:
                    all_authors_cache.append(scored_lead)

                    # Extract data from the scored lead
                    author = scored_lead.get('author', {})
                    author_name = author.get('name', '')
                    job_title = author.get('job_title', '')
                    company_name = author.get('company', '')
                    company_industry = author.get('company_industry', '')
                    company_location = author.get('location', '')
                    employee_count = author.get('employee_count', '')
                    linkedin_post = author.get('linkedin_post', '')

                    #if post exists in database move to the next one
                    if check_if_duplicate_post_exists(linkedin_post):
                        logger.info("Data saving skipped. Post already exists")
                        continue
                    
                    #Otherwise store in DB
                    add_data_into_database(author_name, job_title, company_name, company_industry, company_location, employee_count, linkedin_post, score)

                    yield f"data: {json.dumps(scored_lead)}\n\n"
                            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/total_scores', methods= ["GET"])
def total_scores():
    return icp_scorer.total_score()

#Download Excel
@app.route('/download-excel', methods=['GET'])
def download_excel():
    global all_authors_cache
    local_all_authors_cache = all_authors_cache
    try:
        filename = "Social Listening Results.xlsx"

        #Get qualified leads
        qualified_leads = local_all_authors_cache

        #save qualified leads to excel
        logger.info("Saving data to excel...")
        saved_file = save_as_excel(qualified_leads)
        logger.info("Saving to excel done.")

        #Make file downloadable
        return send_file(
            saved_file,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            as_attachment=True,
            download_name=filename
            )
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message" : str(e)
        }), 500
    
if __name__ == "__main__":
    #run the flask app
    logger.info("Starting flask app...")
    app.run(debug=True)