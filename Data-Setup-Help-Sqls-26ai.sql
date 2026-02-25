

--Ground Truth Queries

CREATE TABLE NL_SQL_TEST_QUERIES (
  query_id       NUMBER PRIMARY KEY,
  nl_question    VARCHAR2(500),
  ground_truth_sql CLOB,
  complexity     VARCHAR2(20), -- 'simple', 'medium', 'complex'
  category       VARCHAR2(50)  -- 'aggregation', 'join', 'filter', etc.
);

BEGIN
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (1, 'What is the total quantity of items sold?', 'SELECT SUM(L_QUANTITY) FROM LINEITEM', 'simple', 'aggregation');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (2, 'How many customers are there?', 'SELECT COUNT(*) FROM CUSTOMER', 'simple', 'aggregation');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (3, 'Show me all orders from 1996.', 'SELECT * FROM ORDERS WHERE O_ORDERDATE BETWEEN ''1996-01-01'' AND ''1996-12-31''', 'medium', 'filter');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (4, 'List the names of customers in the ASIA region.', 'SELECT C.C_NAME FROM CUSTOMER C JOIN NATION N ON C.C_NATIONKEY = N.N_NATIONKEY JOIN REGION R ON N.N_REGIONKEY = R.R_REGIONKEY WHERE R.R_NAME = ''ASIA''', 'complex', 'join');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (5, 'What is the average retail price of parts?', 'SELECT AVG(P_RETAILPRICE) FROM PART', 'simple', 'aggregation');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (6, 'Show top 5 most expensive orders.', 'SELECT * FROM (SELECT * FROM ORDERS ORDER BY O_TOTALPRICE DESC) WHERE ROWNUM <= 5', 'medium', 'sort');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (7, 'Which nation has the most customers?', 'SELECT N_NAME, COUNT(*) FROM CUSTOMER JOIN NATION ON C_NATIONKEY = N_NATIONKEY GROUP BY N_NAME ORDER BY 2 DESC FETCH FIRST 1 ROW ONLY', 'complex', 'join_agg');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (8, 'How many unique parts were supplied by Supplier#1?', 'SELECT COUNT(DISTINCT PS_PARTKEY) FROM PARTSUPP S JOIN SUPPLIER SUP ON S.PS_SUPPKEY = SUP.S_SUPPKEY WHERE SUP.S_NAME = ''Supplier#000000001''', 'complex', 'join');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (9, 'What is the total discount given on all items?', 'SELECT SUM(L_EXTENDEDPRICE * L_DISCOUNT) FROM LINEITEM', 'medium', 'calculation');
  INSERT INTO NL_SQL_TEST_QUERIES VALUES (10, 'Find orders placed by Customer#1.', 'SELECT * FROM ORDERS WHERE O_CUSTKEY = 1', 'simple', 'filter');
  COMMIT;
END;
/

--Create Profile Setup --
BEGIN
  -- This identifies the LLM and the database objects it can "see"
  DBMS_CLOUD_AI.CREATE_PROFILE(
      profile_name => 'PROFILE-NAME',
      attributes   => '{"provider": "openai", "model": "gpt-4o", "credential_name": "OPENAI_CREDNEW"}',
      description  => 'Profile for TPC-H Accuracy Experiment'
  );
  
  -- Enable it for your current session
  DBMS_CLOUD_AI.SET_PROFILE('PROFILE-NAME');
END;
/

BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'CRED-NAME',
    username        => 'openai',
    password        => 'sk-proj--abcd'  -- Get from openai.com
  );
END;
/
--Error if any related to princial can be fixed by changing principal_type to xs_acl.ptype_db or xs_acl.ptype_user based on your setup
BEGIN
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => 'api.openai.com',
    ace  => xs$ace_type(privilege_list => xs$name_list('http'),
                        principal_name => 'ADMIN', -- or your specific username
                        principal_type => xs_acl.ptype_db));
END;
/
--The End