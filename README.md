# Energy Performace Certificate Import Pipeline

## Energy Performance Certificate
Energy Performance Certificates (EPC) are a requirement for domestic and non-domestic builds. [EPC data](https://epc.opendatacommunities.org/docs/guidance) is open and relesed periodically - two to four times a year. 

Details:
 * Dataset: The Record level Energy Performance Certificate datas
 * Publisher: Ministry of Housing, Communities & Local Goverment
 * Area: England & Wales
 * Coverage: Incomplete
 * License: [Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) except [Address data](https://epc.opendatacommunities.org/docs/copyright)

EPC dataset is sperated into three non-overlapping categories - domestic, non-domestic & display - that need to be accessed seperatly. The data is avaliable via an API, but returns a maximum of 10,000 results per call.

Zip files contain directory for each Local Authority District (LAD) in England & Wales - 348 - plus directory for when LAD is unknown. Each LAD directory contains two CSVs - `certificates.csv` & `recommendations.csv`.

## Requirements
Data ingestion pipeline that allows for automated importing of data. Specific data fields need to be extracted and data enriched with Lat/Lon via third-party API. Data loaded into database.

## Approch
 * Pipeline trigger
   * Lambda that hits API and checks latest *Lodgement Date* last lodgement data from previous release
   * This an optimisation as AWS Batch job can be triggered from cli
 * Extract
   * Download Zip files from site rather than use API with filters
   * The Zips are large - biggest >3Gb - and want pipeline to sacale
   * Run job in AWS Batch - negates time and give contorl over memory & CPU
   * Do validation at extract - if fails dump data in S3 for debugging
 * Store raw data in S3
 * Transformation & Load
   * Continue in same batch job for simplicity
   * Use python to loop over `certificates.csv`'s and keep just requried fields
     * `LMK_KEY`
     * `LODGEMENT_DATE`
     * `TRANSACTION_TYPE`
     * `TOTAL_FLOOR_AREA`
     * `ADDRESS`
     * `POSTCODE`
   * Add to staging table
   * Do validation at DB
 * Enrich w/ Lat/Lon enrich
   * Get unique addresses from staging table
   * Call external API for all unique addresses
   * Add API outputs to sepearte staging table
   * Add data to DB table - `INSERT SELECT` with query joining two staging tables
