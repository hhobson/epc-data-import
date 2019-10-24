# Energy Performace Certificate Import Pipeline

## Energy Performance Certificate
Energy Performance Certificates (EPC) are a requirement for domestic and non-domestic builds. [EPC data](https://epc.opendatacommunities.org/docs/guidance) is open and relesed periodically - two to four times a year. 

Details:
 * Dataset: The Record level Energy Performance Certificate datas
 * Publisher: Ministry of Housing, Communities & Local Government
 * Area: England & Wales
 * Coverage: Incomplete
 * License: [Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) except [Address data](https://epc.opendatacommunities.org/docs/copyright)

EPC dataset is sperated into three non-overlapping categories - domestic, non-domestic & display - that need to be accessed seperatly. The data is avaliable via an API but returns a maximum of 10,000 results per call.

Zip files contain directory for each Local Authority District (LAD) in England & Wales - 348 - plus directory for when LAD is unknown. Each LAD directory contains two CSVs - `certificates.csv` & `recommendations.csv`.

## Requirements
Data ingestion pipeline that allows for automated importing of data. Specific data fields need to be extracted and data enriched with Lat/Lon via third-party API. Data loaded into database.

## Pipeline
The pipeline is run as a single [AWS Batch](https://aws.amazon.com/batch/) job.

Currently the domestic dataset is 3.3Gb comprising of more than 18.3 million records and the pipeline needs to be able to scale. Batch allows for the pipeline so scale, with the EBS maximum volume size of the underlying EC2 instances is 16 TiB.

### Pipeline trigger
Job runs are manually triggered from awscli when required, though this will require manual monitoring for data releases. 

**Improvement** -
The API returns records for the most recent *Lodgement Date* first, which would allow it to be used to detect when data release occures. A Lambda function could be setup to check the returned lodgement date of the first record against a reference date of the previous lodgement date. When the dates differ it would trigger the batch job and update the reference date.


### Extract
A bash script will download the zip file from site as the API is not a viable option. As ECP data includes personal data the site requires the user to be logged in, but provides a login with token functionalty that can me used to login programmatically using the API key.

The data is validated at extract, although these could be improved. Currently the decompressed data is check for:
 * Expected number of directories
 * Expected number of files
 * That each file is not empty
 * That each file contains the Individual lodgement identifier - `LMK_KEY`

When the validation fails the data is put in an extract failed bucket so that it is avaliable to inspect.

On sucessful extract all the raw data is put in S3, both `certificates.csv` and `recommendations.csv`. This allows for future changes in required data points or new products that can be backfilled.

**Improvement** -
Lifecycle rules could be added to S3 buckets to archive the data once instant access is no longer required.

### Transformation & Load
The transform and load are done as part of the same batch job for simplicity. A python script loops over each `certificates.csv` and loads just the required fields to a staging table in a PostgreSQL database.

The required fields are:
   * `LMK_KEY`
   * `LODGEMENT_DATE`
   * `TRANSACTION_TYPE`
   * `TOTAL_FLOOR_AREA`
   * `ADDRESS`
   * `POSTCODE`

Further data validation could be carried out once the data has been loaded into a staging table. However, without further understanding of what the data use cases are it is hard to define what these test should be.

### Enrich w/ Lat/Lon
The geocoding of records address could be carried out during the transformation & load step or once the data has been loaded into the staging table. The dataset contains duplicate addresses, so only unique addresses should be geocoded.

If the geocoding is done after the data has been loaded to the staging table a third script could be added to the Batch job. This would call the external API for each unique address and add output to a second staging table. The data could then be added to the production table(s) using an `INSERT SELECT` with the query joining two staging tables.

## Deploy AWS Infrastructure
Will need to have awscli installed

### Deploy CloudFormation template
CloudFormation template will build AWS architecture. To deploy run:
```
aws cloudformation deploy --template-file cloudformation.yaml \ 
  --stack-name EPCImport<Environment> \
  --parameter-overrides \
    Environment=<environment [dev|staging|production]> \
    KeyPair=<EC2 key pair name> \
    EPCOpenDataApiKey=<opendatacommunities.org API key> \
    EPCOpenDataApiEmail=<opendatacommunities.org API email> \
    DatabaseName <database name> \
    DatabaseHost <database host> \
    DatabaseUsername <database user name> \
    DatabasePassword=<database user password [10 to 40 char]> \
  --no-fail-on-empty-changeset \
  --capabilities CAPABILITY_IAM
```
Will need to add database credentials and EC2 Key Pair name as they are not included in the CloudFormation template. 

### Deploy Docker Image
To build and deploy docker image to ECR run `bin/image-build <environment [dev|staging|production]> `

## Trigger Batch Job
To trigger a batch job run:
```
aws batch submit-job --job-name "epc-import-job-`date +%y%m%d_%H%M%S`" \
  --job-queue arn:aws:batch:us-east-1:598346750316:job-queue/JustAnotherJobQueue \
  --job-definition arn:aws:batch:us-east-1:598346750316:job-definition/epc-import-job:1 \
  --parameters certtype=<certificate type [domestic|non-domestic|display]>
```
Default `certtype` parameter is `domestic`, only need to include if want to run non-domestic or display. 
