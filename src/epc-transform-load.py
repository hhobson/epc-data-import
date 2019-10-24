#!/usr/bin/env python3

import sys
import glob
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Date, Float, String, Text

cert_type = sys.argv[1]

cert_csv_path = cert_type + "/**/certificates.csv"
cert_csv_files = glob.glob(cert_csv_path, recursive=True)

keep_cols = ["LMK_KEY", "LODGEMENT_DATE", "TRANSACTION_TYPE", "TOTAL_FLOOR_AREA", "ADDRESS", "POSTCODE"]

db_name = os.environ["DB_NAME"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASSWORD"]
engine = create_engine("postgresql://" + db_user + ":" + db_pass + "@" + db_host + ":" + db_port + "/" + db_name, echo=False)

for cert_csv in cert_csv_files:
    epc_cert = pd.read_csv(cert_csv,
                           index_col=None,
                           usecols=keep_cols)
    epc_cert.to_sql(name="epc_staging",
                    con=engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                    dtype={
                      "LMK_KEY": Text(),
                      "LODGEMENT_DATE": Date(),
                      "TRANSACTION_TYPE": Text(),
                      "TOTAL_FLOOR_AREA": Float(precision=8),
                      "ADDRESS": Text(),
                      "POSTCODE": String(8)
                    })
