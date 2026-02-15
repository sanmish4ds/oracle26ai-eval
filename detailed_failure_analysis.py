#!/usr/bin/env python3
"""
Detailed Failure Analysis: Execute both AI-generated and ground truth queries
to identify exact differences and improvement opportunities.

This generates publication-ready comparison data for the whitepaper.
"""

import pandas as pd
import csv
from datetime import datetime
from db_utils import get_connection, init_ai_session

# Define the 4 failed queries with their ground truth
FAILED_QUERIES = {
    6: {
        'question': "Show top 5 most expensive orders.",
        'ground_truth': """SELECT * FROM (
    SELECT * FROM ORDERS ORDER BY O_TOTALPRICE DESC
) WHERE ROWNUM <= 5""",
        'complexity': 'Medium',
        'pattern': 'ROWNUM + Nested SELECT *'
    },
    10: {
        'question': "Find orders placed by Customer#1.",
        'ground_truth': "SELECT * FROM ORDERS WHERE O_CUSTKEY = 1",
        'complexity': 'Medium',
        'pattern': 'Entity Reference (Customer#1 → C_CUSTKEY)'
    },
    17: {
        'question': "Find the top 5 customers by total spending.",
        'ground_truth': """SELECT C.C_CUSTKEY, C.C_NAME, SUM(O.O_TOTALPRICE)
FROM CUSTOMER C
JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY
GROUP BY C.C_CUSTKEY, C.C_NAME
ORDER BY 3 DESC
FETCH FIRST 5 ROWS ONLY""",
        'complexity': 'Complex',
        'pattern': 'JOIN + GROUP BY + Aggregation + FETCH'
    },
    21: {
        'question': "Find customers who placed no orders in 1996.",
        'ground_truth': """SELECT C.C_CUSTKEY, C.C_NAME FROM CUSTOMER C
WHERE NOT EXISTS (
    SELECT 1 FROM ORDERS O
    WHERE C.C_CUSTKEY = O.O_CUSTKEY
    AND EXTRACT(YEAR FROM O.O_ORDERDATE) = 1996
)""",
        'complexity': 'Complex',
        'pattern': 'NOT EXISTS + Correlated Subquery + Date Extraction'
    }
}

SCHEMA_CONTEXT_V2 = """You are an Oracle SQL expert. Generate ONLY the SQL query, no explanations.

DATABASE SCHEMA (TPC-H Benchmark):
- CUSTOMER: C_CUSTKEY (ID), C_NAME, C_NATIONKEY, C_ADDRESS, C_PHONE
- ORDERS: O_ORDERKEY, O_CUSTKEY, O_ORDERDATE, O_TOTALPRICE, O_ORDERSTATUS, O_ORDERPRIORITY
- LINEITEM: L_ORDERKEY, L_PARTKEY, L_SUPPKEY, L_LINENUMBER, L_QUANTITY, L_EXTENDEDPRICE, L_DISCOUNT, L_TAX, L_LINESTATUS
- PART: P_PARTKEY (ID), P_NAME, P_RETAILPRICE, P_TYPE, P_SIZE, P_BRAND
- SUPPLIER: S_SUPPKEY (ID), S_NAME, S_ADDRESS, S_NATIONKEY
- PARTSUPP: PS_PARTKEY, PS_SUPPKEY, PS_AVAILQTY, PS_SUPPLYCOST
- NATION: N_NATIONKEY, N_NAME, N_REGIONKEY
- REGION: R_REGIONKEY, R_NAME

ORACLE SQL GENERATION RULES (CRITICAL):
1. QUOTE SYNTAX: NEVER use empty quotes (""), never quote aliases unnecessarily
2. ENTITY REFERENCES: "Customer#1" = C_CUSTKEY=1; "Supplier#5" = S_SUPPKEY=5
3. COLUMN SELECTION: For "List X with criteria", include ID + name, exclude other IDs
4. CALCULATIONS: Discount = SUM(price * (1 - discount))
5. SORTING/LIMITING: Use FETCH FIRST N ROWS ONLY (not ROWNUM)
6. JOINS: Use INNER JOIN for required, LEFT JOIN only when needed
7. ZERO-LENGTH IDENTIFIER FIX: Never generate empty alias quotes
8. AGGREGATIONS: Always include entity ID in GROUP BY
9. DATES: Use EXTRACT(YEAR FROM column) for year filtering, >= DATE for range
10. SUBQUERIES: Use table aliases consistently"""

class DetailedFailureAnalyzer:
    def __init__(self):
        self.results = []
        self.comparison_report = []
        
    def generate_ai_sql(self, conn, question):
        """Generate SQL using Oracle AI"""
        prompt = f"""{SCHEMA_CONTEXT_V2}

Question: {question}

Generate only the SQL query."""
        
        try:
            with conn.cursor() as cursor:
                init_ai_session(cursor)
                
                # Escape single quotes for Oracle
                safe_prompt = prompt.replace("'", "''")
                gen_cmd = f"""BEGIN
    DBMS_OUTPUT.PUT_LINE(
        DBMS_CLOUD_AI.GENERATE(
            prompt => '{safe_prompt}',
            action => 'showsql'
        )
    );
END;"""
                
                cursor.execute(gen_cmd)
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            return f"GENERATION_ERROR: {str(e)[:100]}"
    
    def execute_query(self, conn, sql):
        """Execute a query and return results or error"""
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                return {
                    'status': 'SUCCESS',
                    'rows': rows,
                    'row_count': len(rows),
                    'columns': columns,
                    'error': None
                }
        except Exception as e:
            error_msg = str(e)
            return {
                'status': 'ERROR',
                'rows': [],
                'row_count': 0,
                'columns': [],
                'error': error_msg,
                'error_code': error_msg.split('-')[0] if '-' in error_msg else 'UNKNOWN'
            }
    
    def compare_results(self, gt_result, ai_result):
        """Compare ground truth vs AI results"""
        comparison = {
            'both_success': gt_result['status'] == 'SUCCESS' and ai_result['status'] == 'SUCCESS',
            'both_error': gt_result['status'] == 'ERROR' and ai_result['status'] == 'ERROR',
            'gt_success_ai_error': gt_result['status'] == 'SUCCESS' and ai_result['status'] == 'ERROR',
            'gt_error_ai_success': gt_result['status'] == 'ERROR' and ai_result['status'] == 'SUCCESS',
            'row_count_match': gt_result['row_count'] == ai_result['row_count'] if gt_result['status'] == 'SUCCESS' and ai_result['status'] == 'SUCCESS' else None,
            'results_match': False
        }
        
        # If both succeeded, check if results match
        if comparison['both_success']:
            gt_set = set(tuple(str(x) if x is not None else 'NULL' for x in row) for row in gt_result['rows'])
            ai_set = set(tuple(str(x) if x is not None else 'NULL' for x in row) for row in ai_result['rows'])
            comparison['results_match'] = gt_set == ai_set
        
        return comparison
    
    def analyze_query(self, query_id, question, ground_truth_sql, complexity, pattern):
        """Comprehensive analysis of a single failed query"""
        
        print(f"\n{'='*100}")
        print(f"Q{query_id}: {question}")
        print(f"{'='*100}")
        
        with get_connection() as conn:
            # Generate AI SQL
            print(f"\n🤖 GENERATING AI SQL...")
            ai_sql = self.generate_ai_sql(conn, question)
            
            print(f"\n📌 GROUND TRUTH SQL:")
            print(f"{'-'*100}")
            print(ground_truth_sql)
            
            print(f"\n🤖 AI-GENERATED SQL:")
            print(f"{'-'*100}")
            print(ai_sql if ai_sql else "(None)")
            
            # Execute both queries
            print(f"\n⚙️  EXECUTING QUERIES...")
            gt_result = self.execute_query(conn, ground_truth_sql)
            ai_result = self.execute_query(conn, ai_sql) if ai_sql and not ai_sql.startswith("GENERATION_ERROR") else {'status': 'SKIPPED', 'error': 'AI SQL not generated'}
            
            # Display execution results
            print(f"\n📊 EXECUTION RESULTS:")
            print(f"{'-'*100}")
            print(f"Ground Truth: {gt_result['status']}")
            if gt_result['status'] == 'SUCCESS':
                print(f"  Rows returned: {gt_result['row_count']}")
                print(f"  Columns: {', '.join(gt_result['columns'][:5])}")
                if gt_result['rows']:
                    print(f"  Sample row: {gt_result['rows'][0]}")
            else:
                print(f"  Error: {gt_result['error']}")
            
            print(f"\nAI Generated: {ai_result['status']}")
            if ai_result['status'] == 'SUCCESS':
                print(f"  Rows returned: {ai_result['row_count']}")
                print(f"  Columns: {', '.join(ai_result['columns'][:5])}")
                if ai_result['rows']:
                    print(f"  Sample row: {ai_result['rows'][0]}")
            elif ai_result['status'] != 'SKIPPED':
                print(f"  Error: {ai_result['error']}")
            else:
                print(f"  Skipped: {ai_result['error']}")
            
            # Compare
            comparison = self.compare_results(gt_result, ai_result)
            
            print(f"\n🔍 COMPARISON:")
            print(f"{'-'*100}")
            if comparison['both_success']:
                print(f"✓ Both queries executed successfully")
                print(f"  Row count match: {comparison['row_count_match']}")
                print(f"  Results match: {comparison['results_match']}")
                if not comparison['results_match']:
                    print(f"  GT rows: {gt_result['row_count']}, AI rows: {ai_result['row_count']}")
            elif comparison['gt_success_ai_error']:
                print(f"✗ Ground Truth PASSED, AI FAILED")
                print(f"  GT returned {gt_result['row_count']} rows")
                print(f"  AI error: {ai_result['error']}")
            elif comparison['both_error']:
                print(f"✗ Both queries failed")
                print(f"  GT error: {gt_result['error']}")
                print(f"  AI error: {ai_result['error']}")
            
            # Pattern analysis
            self._pattern_analysis(ground_truth_sql, ai_sql if ai_sql and not ai_sql.startswith("GENERATION_ERROR") else "")
            
            # Store results
            result_record = {
                'query_id': query_id,
                'question': question,
                'complexity': complexity,
                'pattern': pattern,
                'gt_status': gt_result['status'],
                'ai_status': ai_result['status'],
                'gt_rows': gt_result['row_count'],
                'ai_rows': ai_result['row_count'],
                'results_match': comparison['results_match'],
                'gt_error': gt_result['error'] if gt_result['error'] else '',
                'ai_error': ai_result['error'] if ai_result['error'] else '',
                'ai_sql': ai_sql,
                'gt_sql': ground_truth_sql
            }
            
            self.results.append(result_record)
            self.comparison_report.append(self._generate_report(result_record))
            
            return result_record
    
    def _pattern_analysis(self, gt_sql, ai_sql):
        """Analyze which SQL patterns are present in each query"""
        print(f"\n📋 PATTERN ANALYSIS:")
        print(f"{'-'*100}")
        
        patterns = {
            'ROWNUM': 'ROWNUM',
            'FETCH FIRST': 'FETCH FIRST',
            'NOT EXISTS': 'NOT EXISTS',
            'LEFT JOIN': 'LEFT JOIN',
            'INNER JOIN': 'INNER JOIN|JOIN',
            'GROUP BY': 'GROUP BY',
            'SELECT *': 'SELECT \\*',
            'WHERE': 'WHERE',
            'ORDER BY': 'ORDER BY',
            'EXTRACT': 'EXTRACT',
            'CORRELATED': 'WHERE.*SELECT.*WHERE'
        }
        
        import re
        
        gt_upper = gt_sql.upper()
        ai_upper = ai_sql.upper() if ai_sql else ""
        
        for pattern_name, pattern in patterns.items():
            gt_has = bool(re.search(pattern, gt_upper))
            ai_has = bool(re.search(pattern, ai_upper))
            
            if gt_has or ai_has:
                status = "✓" if gt_has == ai_has else "✗"
                print(f"  {status} {pattern_name:18s}: GT={str(gt_has):5s} AI={str(ai_has):5s}")
    
    def _generate_report(self, record):
        """Generate narrative report for each query"""
        report = f"""
### Q{record['query_id']}: {record['question']}
**Complexity:** {record['complexity']}  
**Pattern:** {record['pattern']}

#### Ground Truth Execution
- **Status:** {record['gt_status']}
- **Rows Returned:** {record['gt_rows']}
"""
        
        if record['gt_error']:
            report += f"- **Error:** {record['gt_error']}\n"
        
        report += f"""
#### AI-Generated Execution
- **Status:** {record['ai_status']}
- **Rows Returned:** {record['ai_rows']}
"""
        
        if record['ai_error']:
            report += f"- **Error:** {record['ai_error']}\n"
        
        if record['ai_status'] == 'SUCCESS' and record['gt_status'] == 'SUCCESS':
            if record['results_match']:
                report += "- **Result Match:** ✅ YES - Queries produce identical results\n"
            else:
                report += f"- **Result Match:** ❌ NO - GT returned {record['gt_rows']} rows, AI returned {record['ai_rows']} rows\n"
        
        if record['ai_status'] == 'ERROR' and record['gt_status'] == 'SUCCESS':
            # Extract error code
            error_code = record['ai_error'].split('-')[0] if '-' in record['ai_error'] else 'UNKNOWN'
            report += f"\n#### Issue\nAI Query throws `{error_code}` error:\n```\n{record['ai_error']}\n```\n"
        
        report += f"\n#### Queries\n\n**Ground Truth:**\n```sql\n{record['gt_sql']}\n```\n"
        report += f"\n**AI-Generated:**\n```sql\n{record['ai_sql'] if record['ai_sql'] else 'Failed to generate'}\n```\n"
        
        return report
    
    def save_results(self):
        """Save detailed results to CSV"""
        df = pd.DataFrame(self.results)
        
        # Save full report
        output_path = "detailed_failure_comparison.csv"
        df.to_csv(output_path, index=False)
        print(f"\n✅ Detailed comparison saved to: {output_path}")
        
        # Save markdown report
        md_path = "DETAILED_FAILURE_COMPARISON.md"
        with open(md_path, 'w') as f:
            f.write("# Detailed Failure Analysis: AI-Generated vs Ground Truth\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write("## Summary\n\n")
            
            # Summary table
            f.write("| Query | Status | GT Status | AI Status | Match | Issue |\n")
            f.write("|-------|--------|-----------|-----------|-------|-------|\n")
            
            for record in self.results:
                issue = ""
                if record['gt_status'] == 'SUCCESS' and record['ai_status'] == 'ERROR':
                    issue = f"AI Error: {record['ai_error'].split('-')[0]}"
                elif record['ai_status'] == 'SUCCESS' and record['gt_status'] == 'SUCCESS' and not record['results_match']:
                    issue = f"Row mismatch: GT={record['gt_rows']} AI={record['ai_rows']}"
                
                match_status = "✅" if record['results_match'] else "❌" if record['ai_status'] == 'SUCCESS' and record['gt_status'] == 'SUCCESS' else "N/A"
                f.write(f"| Q{record['query_id']} | {record['pattern'][:20]} | {record['gt_status']} | {record['ai_status']} | {match_status} | {issue} |\n")
            
            f.write("\n## Detailed Analysis\n\n")
            for report in self.comparison_report:
                f.write(report)
                f.write("\n---\n\n")
        
        print(f"✅ Markdown report saved to: {md_path}")
        
        return df

def main():
    print("\n" + "="*100)
    print("DETAILED FAILURE ANALYSIS: Execute AI vs Ground Truth")
    print("="*100)
    
    analyzer = DetailedFailureAnalyzer()
    
    # Analyze each failed query
    for query_id, info in FAILED_QUERIES.items():
        analyzer.analyze_query(
            query_id,
            info['question'],
            info['ground_truth'],
            info['complexity'],
            info['pattern']
        )
    
    # Save results
    results_df = analyzer.save_results()
    
    # Print summary
    print(f"\n" + "="*100)
    print("ANALYSIS SUMMARY")
    print("="*100)
    
    print(f"\nTotal Queries Analyzed: {len(results_df)}")
    print(f"Ground Truth Success Rate: {(results_df['gt_status'] == 'SUCCESS').sum()}/{len(results_df)}")
    print(f"AI Generation Success Rate: {(results_df['ai_status'] == 'SUCCESS').sum()}/{len(results_df)}")
    print(f"Result Match Rate: {results_df['results_match'].sum()}/{(results_df['results_match'].notna().sum())}")
    
    print(f"\n✅ Full results available in:")
    print(f"   - detailed_failure_comparison.csv")
    print(f"   - DETAILED_FAILURE_COMPARISON.md (for whitepaper)")

if __name__ == "__main__":
    main()
