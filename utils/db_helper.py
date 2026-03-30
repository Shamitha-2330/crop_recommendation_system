# utils/db_helper.py
import psycopg2
from config import POSTGRES

def get_conn_history():
    cfg = POSTGRES["history_db"]
    return psycopg2.connect(host=POSTGRES["host"], port=POSTGRES["port"],
                            database=cfg["database"], user=cfg["user"], password=cfg["password"])

def get_conn_current():
    cfg = POSTGRES["current_db"]
    return psycopg2.connect(host=POSTGRES["host"], port=POSTGRES["port"],
                            database=cfg["database"], user=cfg["user"], password=cfg["password"])

def get_conn_reco():
    cfg = POSTGRES["recommendations_db"]
    return psycopg2.connect(host=POSTGRES["host"], port=POSTGRES["port"],
                            database=cfg["database"], user=cfg["user"], password=cfg["password"])
