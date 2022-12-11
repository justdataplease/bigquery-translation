# Microservices as Functions in BigQuery - Language Translation (Part 1)

## How to reproduce

***Replace the following with your own 
1) \<your-project-id>
2) \<gcf-conn-name> - https://xxx.eu.gcf-conn
3) \<gcf-endpoint> - https://bigquery-iplookup-xxx.a.run.app

### 1. Clone the repository

### 2. CLI : Deploy Cloud Function (gcf)
    gcloud functions deploy bigquery-translation --gen2 --runtime python39 --trigger-http --project=<your-project-id> --entry-point=translate --source . --region=europe-west3 --memory=128Mi --max-instances=3 --allow-unauthenticated

### 3. CLI : Create an example DATASET, in BigQuery. 
    bq mk --dataset_id=<your-project-id>:translation --location=EU

### 4. CLI : Create a connection between BigQuery and Cloud Functions (gcf-conn). Make sure to note the first part of the last command (<gcf-conn-name> format xxxx.eu.gcf-conn)
    gcloud components update
    bq mk --connection --display_name='my_gcf_conn' --connection_type=CLOUD_RESOURCE --project_id=<your-project-id> --location=EU gcf-conn
    bq show --project_id=<your-project-id> --location=EU --connection gcf-conn

### 5. BIGQUERY : Create a remote UDF
    CREATE OR REPLACE FUNCTION `<your-project-id>.translation.translate`(text STRING, to_language STRING)
    RETURNS STRING
    REMOTE WITH CONNECTION `<gcf-conn-name>`
        OPTIONS (
            -- change this to reflect the Trigger URL of your cloud function (look for the TRIGGER tab)
            endpoint = '<gcf-endpoint>'
        );


### 6. BIGQUERY : Create an example TABLE
    CREATE OR REPLACE TABLE `<your-project-id>.translation.example_dataset` (
      text STRING,
      to_language STRING
    );
    
    INSERT INTO `<your-project-id>.translation.example_dataset`(text, to_language)
    VALUES ('I love programming', 'es'),
           ('We are learning great things today', 'es'),
           ('Support me as a writer', 'es'),
           ('Support me as a writer', 'fr'),
           ('Support me as a writer', 'de');

### 7. BIGQUERY : Test remote UDF
    WITH A AS (SELECT `<your-project-id>.translation.translate`(text,to_language) trans_rs,text origin_text FROM `<your-project-id>.translation.example_dataset`)
    
    select
      origin_text,
      json_value(trans_rs, '$.detected_lang') detected_lang,
      json_value(trans_rs, '$.detected_conf') detected_conf,
      json_value(trans_rs, '$.trans_text') trans_text,
      json_value(trans_rs, '$.trans_lang') trans_lang,
      json_value(trans_rs, '$.error') error
    from a A;
    
### 8. CLI : Remove everything
    # Remove Cloud Function (gcf)
    gcloud functions delete bigquery-translation --region=europe-west3 --project=<your-project-id> --gen2

    # Remove DATASET
    bq rm -r -f -d <your-project-id>:translation

    # Remove connection between BigQuery and Cloud Functions (gcf-conn)
    bq rm --connection --location=EU <gcf-conn-name>