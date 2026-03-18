import oracledb


def create_ai_profile(cursor, profile_name, attributes_json, description=None):
    """
    Create a DBMS_CLOUD_AI profile.

    Example attributes_json:
      '{"provider": "openai", "model": "gpt-4o", "credential_name": "OPENAI_CREDNEW"}'
    """
    desc_clause = (
        ", description  => :description" if description is not None else ""
    )
    plsql = (
        "BEGIN "
        "DBMS_CLOUD_AI.CREATE_PROFILE("
        "profile_name => :profile_name, "
        "attributes   => :attributes"
        f"{desc_clause}"
        "); "
        "END;"
    )
    binds = {
        "profile_name": profile_name,
        "attributes": attributes_json,
    }
    if description is not None:
        binds["description"] = description
    cursor.execute(plsql, binds)


def init_ai_session(cursor, profile_name="EVAL_PROFILE"):
    """Initialize the Select AI profile for the current session."""
    cursor.execute(
        "BEGIN DBMS_CLOUD_AI.SET_PROFILE(:profile_name); END;",
        {"profile_name": profile_name},
    )


def generate_select_ai_sql(cursor, prompt, action="showsql"):
    """
    Call DBMS_CLOUD_AI.GENERATE for a natural language prompt.

    By default uses action='showsql' so that only SQL generation latency
    is measured and the database does not execute the generated SQL.
    """
    gen_cmd = (
        "SELECT DBMS_CLOUD_AI.GENERATE("
        f"prompt => '{prompt}', "
        f"action => '{action}'"
        ") FROM DUAL"
    )
    cursor.execute(gen_cmd)
    row = cursor.fetchone()
    return row[0] if row else None


def set_time_limit(cursor, seconds):
    """Set an execution time limit for the current session (in seconds)."""
    cursor.execute(
        "BEGIN DBMS_SESSION.SET_TIME_LIMIT(:limit_sec); END;",
        {"limit_sec": seconds},
    )

