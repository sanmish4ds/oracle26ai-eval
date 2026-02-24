# config.py
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("ORACLE_USER", "admin")
PASSWORD = os.getenv("ORACLE_PASSWORD")
DSN = os.getenv("ORACLE_DSN", "prishivdb_high")
WALLET_PATH = os.getenv("ORACLE_WALLET_PATH", "/Users/sanjaymishra/downloads/Wallet_PRISHIVDB")
WALLET_PWD = os.getenv("ORACLE_WALLET_PWD")
PROFILE = os.getenv("ORACLE_PROFILE", "EVAL_PROFILE")
RESULTS_FILE = os.getenv("RESULTS_FILE", "TPCH_Exp_Results.csv")

if not PASSWORD or not WALLET_PWD:
    raise RuntimeError("Missing required environment variables: ORACLE_PASSWORD, ORACLE_WALLET_PWD. Set them in .env file.")