from flask import Flask, jsonify, request, render_template
import cx_Oracle
import redis
from redisearch import Client, TextField, IndexDefinition, Query
import time

from redisearch.client import IndexType

app = Flask(__name__)

# Initialize Oracle client with the updated library directory
#cx_Oracle.init_oracle_client(lib_dir="/root/something/instantclient_19_24")
cx_Oracle.init_oracle_client(lib_dir="/Users/gabriel.cerioni/instantclient")

# Oracle connection setup
oracle_dsn = cx_Oracle.makedsn("34.198.15.233", "1521", service_name="ORCLPDB1")
oracle_conn = cx_Oracle.connect(user="c##dbzuser", password="dbz", dsn=oracle_dsn)
oracle_cursor = oracle_conn.cursor()

# Redis connection setup
redis_client = redis.StrictRedis(host='34.198.15.233', port=19419, password='secret42')
redis_search_client = Client('estab_sus', conn=redis_client)
index_prefix = 'tb_estabelecimento_saude:'

def create_redis_index():
    """
    Creates the index in Redis if it doesn't exist.
    """
    try:
        redis_search_client.info()
    except Exception as e:
        print(f"Creating index because: {str(e)}")
        schema = (TextField("$.NM_LOGR", as_name="NM_LOGR"),)
        definition = IndexDefinition(prefix=[index_prefix], index_type=IndexType.JSON)
        redis_search_client.create_index(schema, definition=definition)

create_redis_index()

@app.route('/query', methods=['GET'])
def query():
    search_term = request.args.get('search_term', '').upper()  # Convert search term to upper case
    oracle_search_term = search_term.replace('*', '')  # Remove '*' for Oracle query

    # Oracle query with UPPER function for case-insensitive comparison
    oracle_query = """
    SELECT ID_ESTABELECIMENTO_SAUDE_PK, NM_RAZ_SOC, NM_FANTS, NM_LOGR, NM_NUMERO, NM_BAIRRO, CD_CEP
    FROM CHINOOK.TB_ESTABELECIMENTO_SAUDE
    WHERE UPPER(NM_LOGR) LIKE :search_term
    """
    oracle_start_time = time.time()
    oracle_cursor.execute(oracle_query, search_term=f'%{oracle_search_term}%')
    oracle_results = oracle_cursor.fetchall()
    oracle_latency_ms = (time.time() - oracle_start_time) * 1000  # Convert to milliseconds

    # Redis search remains unchanged
    redis_query = Query(f'@NM_LOGR:{search_term}').return_fields("$.ID_ESTABELECIMENTO_SAUDE_PK", "$.NM_RAZ_SOC", "$.NM_FANTS", "$.NM_LOGR", "$.NM_NUMERO", "$.NM_BAIRRO", "$.CD_CEP")
    redis_start_time = time.time()
    redis_results = redis_search_client.search(redis_query)
    redis_latency_ms = (time.time() - redis_start_time) * 1000  # Convert to milliseconds

    return jsonify({
        "oracle_results": oracle_results,
        "oracle_latency_ms": oracle_latency_ms,
        "redis_results": [doc.__dict__ for doc in redis_results.docs],  # Directly pass document data
        "redis_latency_ms": redis_latency_ms
    })



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
