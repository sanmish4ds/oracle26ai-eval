-- 1. REGION Table
CREATE TABLE REGION (
    R_REGIONKEY  NUMBER(38,0) NOT NULL PRIMARY KEY,
    R_NAME       CHAR(25) NOT NULL,
    R_COMMENT    VARCHAR2(152)
);

-- 2. NATION Table
CREATE TABLE NATION (
    N_NATIONKEY  NUMBER(38,0) NOT NULL PRIMARY KEY,
    N_NAME       CHAR(25) NOT NULL,
    N_REGIONKEY  NUMBER(38,0) NOT NULL,
    N_COMMENT    VARCHAR2(152)
);

-- 3. PART Table
CREATE TABLE PART (
    P_PARTKEY     NUMBER(38,0) NOT NULL PRIMARY KEY,
    P_NAME        VARCHAR2(55) NOT NULL,
    P_MFGR        CHAR(25) NOT NULL,
    P_BRAND       CHAR(10) NOT NULL,
    P_TYPE        VARCHAR2(25) NOT NULL,
    P_SIZE        NUMBER(38,0) NOT NULL,
    P_CONTAINER   CHAR(10) NOT NULL,
    P_RETAILPRICE NUMBER(15,2) NOT NULL,
    P_COMMENT     VARCHAR2(23) NOT NULL
);

-- 4. SUPPLIER Table
CREATE TABLE SUPPLIER (
    S_SUPPKEY     NUMBER(38,0) NOT NULL PRIMARY KEY,
    S_NAME        CHAR(25) NOT NULL,
    S_ADDRESS     VARCHAR2(40) NOT NULL,
    S_NATIONKEY   NUMBER(38,0) NOT NULL,
    S_PHONE       CHAR(15) NOT NULL,
    S_ACCTBAL     NUMBER(15,2) NOT NULL,
    S_COMMENT     VARCHAR2(101) NOT NULL
);

-- 5. PARTSUPP Table
CREATE TABLE PARTSUPP (
    PS_PARTKEY     NUMBER(38,0) NOT NULL,
    PS_SUPPKEY     NUMBER(38,0) NOT NULL,
    PS_AVAILQTY    NUMBER(38,0) NOT NULL,
    PS_SUPPLYCOST  NUMBER(15,2) NOT NULL,
    PS_COMMENT     VARCHAR2(199) NOT NULL,
    PRIMARY KEY (PS_PARTKEY, PS_SUPPKEY)
);


-- 6. CUSTOMER Table
CREATE TABLE CUSTOMER (
    C_CUSTKEY     NUMBER(38,0) NOT NULL PRIMARY KEY,
    C_NAME        VARCHAR2(25) NOT NULL,
    C_ADDRESS     VARCHAR2(40) NOT NULL,
    C_NATIONKEY   NUMBER(38,0) NOT NULL,
    C_PHONE       CHAR(15) NOT NULL,
    C_ACCTBAL     NUMBER(15,2) NOT NULL,
    C_MKTSEGMENT  CHAR(10) NOT NULL,
    C_COMMENT     VARCHAR2(117) NOT NULL
);

-- 7. ORDERS Table
CREATE TABLE ORDERS (
    O_ORDERKEY       NUMBER(38,0) NOT NULL PRIMARY KEY,
    O_CUSTKEY        NUMBER(38,0) NOT NULL,
    O_ORDERSTATUS    CHAR(1) NOT NULL,
    O_TOTALPRICE     NUMBER(15,2) NOT NULL,
    O_ORDERDATE      DATE NOT NULL,
    O_ORDERPRIORITY  CHAR(15) NOT NULL,
    O_CLERK          CHAR(15) NOT NULL,
    O_SHIPPRIORITY   NUMBER(38,0) NOT NULL,
    O_COMMENT        VARCHAR2(79) NOT NULL
);

-- 8. LINEITEM Table
CREATE TABLE LINEITEM (
    L_ORDERKEY    NUMBER(38,0) NOT NULL,
    L_PARTKEY     NUMBER(38,0) NOT NULL,
    L_SUPPKEY     NUMBER(38,0) NOT NULL,
    L_LINENUMBER  NUMBER(38,0) NOT NULL,
    L_QUANTITY    NUMBER(15,2) NOT NULL,
    L_EXTENDEDPRICE NUMBER(15,2) NOT NULL,
    L_DISCOUNT    NUMBER(15,2) NOT NULL,
    L_TAX         NUMBER(15,2) NOT NULL,
    L_RETURNFLAG  CHAR(1) NOT NULL,
    L_LINESTATUS  CHAR(1) NOT NULL,
    L_SHIPDATE    DATE NOT NULL,
    L_COMMITDATE  DATE NOT NULL,
    L_RECEIPTDATE DATE NOT NULL,
    L_SHIPINSTRUCT CHAR(25) NOT NULL,
    L_SHIPMODE    CHAR(10) NOT NULL,
    L_COMMENT     VARCHAR2(44) NOT NULL,
    PRIMARY KEY (L_ORDERKEY, L_LINENUMBER)
);

--Insert Scripts to Load Data 1000 rows

BEGIN
  -- Generate 1,000 Customers
  FOR i IN 1..1000 LOOP
    INSERT INTO CUSTOMER (C_CUSTKEY, C_NAME, C_ADDRESS, C_NATIONKEY, C_PHONE, C_ACCTBAL, C_MKTSEGMENT, C_COMMENT)
    VALUES (i, 'Customer#' || i, 'Address' || i, MOD(i, 5), '15-123-' || i, 1000 + i, 'BUILDING', 'No comment');
  END LOOP;

  -- Generate 1,000 Parts
  FOR i IN 1..1000 LOOP
    INSERT INTO PART (P_PARTKEY, P_NAME, P_MFGR, P_BRAND, P_TYPE, P_SIZE, P_CONTAINER, P_RETAILPRICE, P_COMMENT)
    VALUES (i, 'Part#' || i, 'Manufacturer#1', 'Brand#1', 'PROMO BRUSHED COPPER', 10, 'JUMBO BAG', 900.00, 'Comment');
  END LOOP;

  -- Generate 1,000 Orders
  FOR i IN 1..1000 LOOP
    INSERT INTO ORDERS (O_ORDERKEY, O_CUSTKEY, O_ORDERSTATUS, O_TOTALPRICE, O_ORDERDATE, O_ORDERPRIORITY, O_CLERK, O_SHIPPRIORITY, O_COMMENT)
    VALUES (i, MOD(i, 1000) + 1, 'O', 1500.50, SYSDATE - MOD(i, 100), '1-URGENT', 'Clerk#001', 0, 'Ok');
  END LOOP;

  -- Generate 1,000 Lineitems
  FOR i IN 1..1000 LOOP
    INSERT INTO LINEITEM (L_ORDERKEY, L_PARTKEY, L_SUPPKEY, L_LINENUMBER, L_QUANTITY, L_EXTENDEDPRICE, L_DISCOUNT, L_TAX, L_RETURNFLAG, L_LINESTATUS, L_SHIPDATE, L_COMMITDATE, L_RECEIPTDATE, L_SHIPINSTRUCT, L_SHIPMODE, L_COMMENT)
    VALUES (i, i, 1, 1, 10, 200.00, 0.05, 0.02, 'N', 'O', SYSDATE, SYSDATE, SYSDATE, 'DELIVER IN PERSON', 'TRUCK', 'Testing');
  END LOOP;

  COMMIT;
END;
/

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
--Error if any related to princial
BEGIN
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => 'api.openai.com',
    ace  => xs$ace_type(privilege_list => xs$name_list('http'),
                        principal_name => 'ADMIN', -- or your specific username
                        principal_type => xs_acl.ptype_db));
END;
/
--The End