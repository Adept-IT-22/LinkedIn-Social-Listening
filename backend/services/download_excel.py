#This module downloads the list of leads as an excel sheet

import pandas as pd
from datetime import date
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

#Save data to excel
def save_as_excel(data_for_dataframe: list):
    # Parse the data into structured format
    parsed_data = []
    for row in data_for_dataframe:
        # Split by ' - ' and handle cases where there might be extra dashes in the text
        parts = row.split(' - ')
        if len(parts) >= 6:  # Ensure we have enough parts
            name = parts[0].strip()
            job_title= parts[1].strip()
            company_name = parts[2].strip()
            company_industry = parts[3].strip()
            company_location = parts[4].strip()
            employee_count = parts[5].strip() if len(parts) > 5 else 'Unknown'
            linkedin_post = parts[6].strip()

            parsed_data.append([name, job_title, company_name, company_industry, company_location, employee_count, linkedin_post])
    
    # Create DataFrame with specific columns
    df = pd.DataFrame(parsed_data, columns=["Name", "Job Title", "Company Name", "Company Industry", "Company Location", "Employee Count", "LinkedIn Post"])
    
    #Write dataframe to a ByteIO object
    today = str(date.today())
    buffer = BytesIO()
    with pd.ExcelWriter(buffer ,engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=today)
    buffer.seek(0) #Move the file pointer to the beginning of the stream

    logging.info(f"Data saved in Excel!")
    return buffer
