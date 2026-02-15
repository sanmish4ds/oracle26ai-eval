# db_utils.py
import oracledb
import config

def get_connection():
    conn = oracledb.connect(
        user=config.USER,
        password=config.PASSWORD,
        dsn=config.DSN,
        config_dir=config.WALLET_PATH,
        wallet_location=config.WALLET_PATH,
        wallet_password=config.WALLET_PWD
    )
    
    # This is the "Magic" handler that kills the LOB error forever
    def return_as_string(cursor, name, default_type, size, precision, scale):
        if default_type == oracledb.DB_TYPE_CLOB:
            return cursor.var(oracledb.DB_TYPE_LONG, arraysize=cursor.arraysize)
        if default_type == oracledb.DB_TYPE_BLOB:
            return cursor.var(oracledb.DB_TYPE_LONG_RAW, arraysize=cursor.arraysize)

    conn.outputtypehandler = return_as_string
    return conn

def init_ai_session(cursor):
    """Initializes the Select AI profile for the current session."""
    cursor.execute("BEGIN DBMS_CLOUD_AI.SET_PROFILE('EVAL_PROFILE'); END;")