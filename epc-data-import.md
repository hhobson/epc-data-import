# Challenge: EPC Data Import

## Getting Started

- This problem uses real data that we already import into our application regularly
- Register a user at [epc.opendatacommunities.org](https://epc.opendatacommunities.org/#register) so that you can access the EPC data
- This challenge is concerned with the "Domestic EPC". There is a downloadable zip (~3Gb+) for around 18,000,000 EPC records.

## Problem

We'd like to import the data as part of a regular, repeatable, automated data pipeline.

- Within the zip, we want to import data from all the `certificates.csv` files
- Within each `certificates.csv` we only want the columns `LMK_KEY`, `LODGEMENT_DATE`, `TRANSACTION_TYPE`, `TOTAL_FLOOR_AREA`, `ADDRESS`, `POSTCODE`, all other columns can be ignored.
- We'd like to write the results to a database (can be any flavour of database you prefer)

## Scope

- We have AWS resources and a Kubernetes cluster (including an ELK stack and Prometheus) at our disposal (can be included as part of your decisions and solutions)
- The data changes/updates every quarter and may increase in size
- For each EPC entry we have to call an external API with the `ADDRESS` column to get a lat/lng. This API isn't provided nor do you need to code for it, but do be aware that the response time is 250ms for a single request when designing your solution. You can assume the API can happily handle a hundreds of requests a second.

## Requirements

We'd like to see how you would approach this problem, from getting the data to putting it into a database. As part of this we would expect to see:

- A proof of concept, some code/execution and explanation/diagrams etc...
- What tools/resources you would use?
- How would you treat/manage the import as part of your operational workload
- How you would scale the import if it grew massively in size?
- How often would you run the import? How fast is fast-enough?
- How would you know when the import has failed?

## Guidelines

Here are some guidelines to things we look for, none are mandatory:

- We would like be able to run part/some of the code ourselves
- We like automation (hint - even the downloading of the zip)
- We like tests
- We like shell, python, docker
- We like clear, concise documentation
- We like simplicity... less is more

We don't expect everything to be included in code. Aspects of your solution can be described using whatever means you feel best gets the design across (a picture is a 1,000 words etc...)

There is no restriction on the technology stack you choose to use, however bear in mind that we use mostly work in node.js, python, shell and docker. If in doubt, keep it simple - we like simplicity!
