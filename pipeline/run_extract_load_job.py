import dlt
from dlt.destinations import filesystem
import http.client
import json
import ast
import urllib.parse
import os
import logging
from typing import Dict, Iterator, Any
from datetime import datetime



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

    Args:
        title_filter: Job title to search for
        location_filter: Location to search in
        limit: Maximum number of results to return
        offset: Number of results to skip
    """
    # Get API key from dlt secrets.toml
    api_key = dlt.secrets['sources']['linkedin_jobs_api']['rapid_api_key']

    if not api_key:
        raise ValueError("API key not found in environment variables")

    # Set up the connection and headers for the API request
    conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
    }

    # Properly URL encode the parameters
    encoded_title = urllib.parse.quote_plus(f'"{title_filter}"')
    encoded_location = urllib.parse.quote_plus(f'"{location_filter}"')

    # Prepare the API endpoint with properly encoded query parameters
    endpoint = f"/active-jb-7d?limit={limit}&offset={offset}&title_filter={encoded_title}&location_filter={encoded_location}"

    logger.info(f"Function linkedin_jobs logs - Fetching jobs for title '{title_filter}' in location '{location_filter}'")

    # Send the request to the API
    conn.request("GET", endpoint, headers=headers)

    # Get the response and read the data
    res = conn.getresponse()
    data = res.read()

    # Load the JSON data into a Python dictionary
    job_data = json.loads(data.decode("utf-8"))

    logger.info(f"Function linkedin_jobs logs - Retrieved {len(job_data)} job listings")

    # Define the columns we need
    needed_columns = [
        'id', 'title', 'date_posted', 'organization',
        'linkedin_org_employees', 'linkedin_org_url',
        'linkedin_org_industry', 'linkedin_org_followers',
        'locations_raw', 'employment_type', 'seniority',
        'source', 'directapply', 'url'
    ]

    # Process each job listing individually and yield one at a time
    for job in job_data:
        # Create a row with only the needed columns
        job_row = {col: job.get(col) for col in needed_columns if col in job}

        # Extract location city from locations_raw
        if 'locations_raw' in job_row:
            try:
                loc_raw = job_row['locations_raw']
                data = ast.literal_eval(loc_raw) if isinstance(loc_raw, str) else loc_raw
                if isinstance(data, list) and len(data) > 0 and 'address' in data[0]:
                    job_row['location_city'] = data[0]['address'].get('addressLocality')
                else:
                    job_row['location_city'] = None
            except Exception as e:
                logger.warning(f"Function linkedin_jobs logs - Error parsing location data: {e}")
                job_row['location_city'] = None

        # Extract employment type
        if 'employment_type' in job_row:
            try:
                emp_type = job_row['employment_type']
                data = ast.literal_eval(emp_type) if isinstance(emp_type, str) else emp_type
                if isinstance(data, list) and len(data) > 0:
                    job_row['employment_type'] = data[0]
                else:
                    job_row['employment_type'] = None
            except Exception as e:
                logger.warning(f"Function linkedin_jobs logs - Error parsing employment type: {e}")
                job_row['employment_type'] = None

        # Remove the locations_raw field as we've extracted what we need
        if 'locations_raw' in job_row:
            del job_row['locations_raw']

        # Add extraction timestamp
        job_row['extraction_timestamp'] = datetime.now().isoformat()
        job_row['job_search_title'] = title_filter
        job_row['job_search_location'] = location_filter

        # Yield one job at a time
        yield job_row


# Define the source that returns the resources
@dlt.source
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