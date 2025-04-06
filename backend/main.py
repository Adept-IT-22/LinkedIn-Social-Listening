#This is the main module

import logging
from typing import Dict, Any
from flask import Flask, jsonify
from config import logging_config
from services.icp_scoring import icp_scoring

#create a flask app
app = Flask(__name__)

#initialize logging configs
logging_config.configure_logging()

#create module level logger
logger = logging.getLogger(__name__)

#endpoint to retrieve qualified leads based on icp scoring.
@app.route('/lead-data', methods=['GET'])
def lead_data() -> Dict[str, Any]:

    #minimum score for a lead to become qualified
    min_score = 50
    try:
        logger.info("Starting process of fetching lead data...")
        
        #run icp scoring. it will call get authors which will call search posts
        lead_data = icp_scoring(min_score=min_score)

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

if __name__ == "__main__":
    #run the flask app
    logger.info("Starting flask app...")
    app.run(debug=True)