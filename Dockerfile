FROM apache/airflow:2.7.3-python3.8

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    gnupg \
    software-properties-common \
    wget \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor > /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow
ENV PROJECT_ROOT=/opt/airflow/berlin_jobs_analytics
ENV DBT_PROJECT_PATH=/opt/airflow/berlin_jobs_analytics/dbt_project/berlin_data_engg_job_analytics
ENV TERRAFORM_PATH=/opt/airflow/berlin_jobs_analytics/terraform

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.8.txt"

# Create project directory structure
RUN mkdir -p ${PROJECT_ROOT}/pipeline \
    ${PROJECT_ROOT}/dbt_project/berlin_data_engg_job_analytics \
    ${PROJECT_ROOT}/airflow/dags \
    ${PROJECT_ROOT}/terraform \
    ${PROJECT_ROOT}/logs \
    ${PROJECT_ROOT}/.dlt

# Copy project files
WORKDIR ${PROJECT_ROOT}