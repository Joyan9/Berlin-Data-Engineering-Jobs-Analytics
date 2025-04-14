import dlt
import requests
import json
import ast
import urllib.parse
import os
import logging
from typing import Dict, Iterator, Any
from datetime import datetime
import os

# Set BigQuery destination configuration
os.environ["DESTINATION__BIGQUERY__DATASET_NAME"] = os.environ.get("BIGQUERY_RAW_DATASET", "raw_data")
os.environ["DESTINATION__BIGQUERY__LOCATION"] = os.environ.get("BIGQUERY_LOCATION", "europe-west10")

# Make sure you set GOOGLE_APPLICATION_CREDENTIALS env variable to point towards your service account key file - dlt uses that

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("linkedin_jobs_pipeline")

# Define the resource that yields LinkedIn job listings one row at a time
@dlt.resource(primary_key="id", write_disposition="append")
def linkedin_jobs(
    title_filter: str = "Data Engineer",
    location_filter: str = "Berlin",
    limit: int = 100,
    offset: int = 0
) -> Iterator[Dict[str, Any]]:
    """
    Resource that yields LinkedIn job listings one row at a time.
    """
    api_key = os.getenv("LINKEDIN_JOBS_API_KEY").strip('“”"')

    url = "https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d"
    querystring = {
        "limit": "99",
        "offset": "0",
        "title_filter": f"{title_filter}",
        "location_filter": f"{location_filter}",
        "include_ai": "true"
    }
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    job_data = response.json()

    logger.info(f"Retrieved {len(job_data)} job listings")

    needed_columns = [
        'id', 'title', 'date_posted', 'organization',
        'linkedin_org_employees', 'linkedin_org_url',
        'linkedin_org_industry', 'linkedin_org_followers',
        'locations_raw', 'employment_type', 'seniority',
        'source', 'directapply', 'url', 'ai_experience_level', 
        'ai_key_skills', 'ai_job_language', 'ai_work_arrangement'
    ]

    for job in job_data:
        job_row = {col: job.get(col) for col in needed_columns if col in job}

        # Process locations_raw
        if 'locations_raw' in job_row:
            try:
                loc_raw = job_row['locations_raw']
                if isinstance(loc_raw, str):
                    # Use json.loads with UTF-8 encoding
                    data = json.loads(loc_raw.encode('utf-8').decode('utf-8'))
                else:
                    data = loc_raw
                
                if isinstance(data, list) and len(data) > 0 and 'address' in data[0]:
                    job_row['location_city'] = data[0]['address'].get('addressLocality')
                else:
                    job_row['location_city'] = None
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error in locations_raw: {e}")
                job_row['location_city'] = None
            except Exception as e:
                logger.warning(f"Error parsing location data: {e}")
                job_row['location_city'] = None

        # Process employment_type
        if 'employment_type' in job_row:
            try:
                emp_type = job_row['employment_type']
                if isinstance(emp_type, str):
                    # Use json.loads with UTF-8 encoding
                    data = json.loads(emp_type.encode('utf-8').decode('utf-8'))
                else:
                    data = emp_type
                
                if isinstance(data, list) and len(data) > 0:
                    job_row['employment_type'] = data[0]
                else:
                    job_row['employment_type'] = None
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error in employment_type: {e}")
                job_row['employment_type'] = None
            except Exception as e:
                logger.warning(f"Error parsing employment type: {e}")
                job_row['employment_type'] = None

        # Remove original raw fields
        job_row.pop('locations_raw', None)

        # Add metadata
        job_row.update({
            'extraction_timestamp': datetime.now().isoformat(),
            'job_search_title': title_filter,
            'job_search_location': location_filter
        })

        # Sanitize all string fields
        for key in job_row:
            if isinstance(job_row[key], str):
                job_row[key] = job_row[key].encode('utf-8', 'ignore').decode('utf-8')

        yield job_row
        logger.info(f"Yielded job listing with ID: {job_row['id']}")


# Define the source that returns the resources
# https://dlthub.com/docs/general-usage/source#reduce-the-nesting-level-of-generated-tables
# will not generate nested tables and will not flatten dicts into columns at all
@dlt.source(max_table_nesting=1) 
def linkedin_jobs_source():
    """
    A dlt source that retrieves LinkedIn job data based on filters.
    """
    return linkedin_jobs


if __name__ == "__main__":
    # Create the source instance
    source_data = linkedin_jobs_source()
    
    try:
        logger.info(f"Fetching LinkedIn jobs data once")
        
        # Run BigQuery pipeline with the extracted data
        logger.info("Processing jobs for BigQuery")
        bq_pipeline = dlt.pipeline(
            pipeline_name="linkedin_jobs_pipeline",
            destination="bigquery",
            dataset_name="raw_data"
        )
        load_info_bq = bq_pipeline.run(source_data, table_name="linkedin_jobs")
        logger.info(f"Successfully loaded data for BigQuery")

        
    except Exception as e:
        logger.error(f"Error loading data: {e}")