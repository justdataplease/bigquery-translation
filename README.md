# Microservices as Functions in BigQuery - Language Translation using SQL (Part 1)

Read original
article [here](https://medium.com/geekculture/microservices-as-functions-in-bigquery-language-translation-using-sql-part-1-bd875b291338)
.

## How to reproduce

***Perform the following actions

Enable Google Cloud Functions. Read more [here](https://cloud.google.com/functions/docs/create-deploy-gcloud). \
Install and configure gcloud CLI. Read more [here](https://cloud.google.com/functions/docs/create-deploy-gcloud). \
Enable Azure Translator API. Read
more [here](https://learn.microsoft.com/en-us/azure/cognitive-services/translator/translator-text-apis?tabs=csharp).

***Replace the following with your own

1) \<your-project-id>
2) \<gcf-endpoint> (step 2)
3) \<gcf-conn> (step 3)

### 1. Clone the repository

    git clone https://github.com/justdataplease/bigquery-translation.git

### 2. CLI : Deploy Cloud Function (gcf-endpoint)

    gcloud functions deploy bigquery-translation --gen2 --runtime python39 --trigger-http --project=<your-project-id> --entry-point=translate --source . --region=europe-west3 --memory=128Mi --max-instances=3 --allow-unauthenticated

From the output note the uri  <gcf-endpoint> (i.e https://bigquery-translation-xxxxxx.a.run.app)
or visit Google [Cloud Console Functions](https://console.cloud.google.com/functions/list?project=).

### 3. CLI : Create a connection between BigQuery and Cloud Functions (gcf-conn).

    gcloud components update
    bq mk --connection --display_name='my_gcf_conn' --connection_type=CLOUD_RESOURCE --project_id=<your-project-id> --location=EU gcf-conn
    bq show --project_id=<your-project-id> --location=EU --connection gcf-conn

From the output of the last command, note the name <gcf-conn-name> (i.e. xxxxxx.eu.gcf-conn)

### 4. CLI : Create a toy dataset

    bq mk --dataset_id=<your-project-id>:translation --location=EU

### 5. BIGQUERY : Create an example table

    CREATE OR REPLACE TABLE `<your-project-id>.translation.example_table` (
      text STRING,
      to_language STRING
    );
    
    INSERT INTO `<your-project-id>.translation.example_table`(text, to_language)
    VALUES ('I love programming', 'es'),
           ('We are learning great things today', 'es'),
           ('Support me as a writer', 'es'),
           ('Support me as a writer', 'fr'),
           ('Support me as a writer', 'de');

### 6. BIGQUERY : Create a Remote Function

    CREATE OR REPLACE FUNCTION `<your-project-id>.translation.translate`(text STRING, to_language STRING)
    RETURNS STRING
    REMOTE WITH CONNECTION `<gcf-conn>`
        OPTIONS (
            -- change this to reflect the Trigger URL of your cloud function (look for the TRIGGER tab)
            endpoint = '<gcf-endpoint>'
        );

### 7. BIGQUERY : Test the Remote Function

    WITH A AS (SELECT `<your-project-id>.translation.translate`(text,to_language) trans_rs,text origin_text FROM `<your-project-id>.translation.example_table`)
    
    select
      origin_text,
      json_value(trans_rs, '$.detected_lang') detected_lang,
      json_value(trans_rs, '$.detected_conf') detected_conf,
      json_value(trans_rs, '$.trans_text') trans_text,
      json_value(trans_rs, '$.trans_lang') trans_lang,
      json_value(trans_rs, '$.error') error
    from a A;
    
    -- Output 
    1
    origin_text : We are learning great things today
    detected_lang : en
    detected_conf : 1.0
    trans_text : estamos aprendiendo grandes cosas hoy
    trans_lang : es

    2
    origin_text : I love programming
    detected_lang : en
    detected_conf : 1.0
    trans_text : me encanta programar
    trans_lang : es

    3
    origin_text : Support me as a writer
    detected_lang : en
    detected_conf : 1.0
    trans_text : apóyame como escritor
    trans_lang : es

    4
    origin_text : Support me as a writer
    detected_lang : en
    detected_conf : 1.0
    trans_text : unterstütze mich als schriftsteller
    trans_lang : de

    5
    origin_text : Support me as a writer
    detected_lang : en
    detected_conf : 1.0
    trans_text : soutenez-moi en tant qu’écrivain
    trans_lang : fr

### 8. CLI : Remove everything

    # Remove Cloud Function (gcf)
    gcloud functions delete bigquery-translation --region=europe-west3 --project=<your-project-id> --gen2

    # Remove DATASET
    bq rm -r -f -d <your-project-id>:translation

    # Remove connection between BigQuery and Cloud Functions (gcf-conn)
    bq rm --connection --location=EU <gcf-conn>