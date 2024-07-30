from flask import Flask, jsonify, request
import cx_Oracle
import redis
from redisearch import Client, TextField, NumericField, IndexDefinition, Query
import json
import time

from redisearch.client import IndexType

app = Flask(__name__)

# Initialize Oracle client
cx_Oracle.init_oracle_client(lib_dir="/Users/gabriel.cerioni/instantclient")

# Oracle connection setup
oracle_dsn = cx_Oracle.makedsn("34.198.15.233", "1521", service_name="ORCLPDB1")
oracle_conn = cx_Oracle.connect(user="c##dbzuser", password="nada", dsn=oracle_dsn)
oracle_cursor = oracle_conn.cursor()

# Redis connection setup
redis_client = redis.StrictRedis(host='34.198.15.233', port=19419, password='nada')
redis_search_client = Client('track_index', conn=redis_client)


def create_redis_index():
    """
    Creates the index in Redis if it doesn't exist.
    """
    try:
        # Check if the index exists by attempting to get its info
        redis_search_client.info()
    except Exception as e:
        print(f"Creating index because: {str(e)}")

        # Index does not exist, create it
        schema = (
            TextField("$.NAME", as_name="NAME"),  # JSON path with an alias
            TextField("$.COMPOSER", as_name="COMPOSER")
        )
        definition = IndexDefinition(prefix=['track:'], index_type=IndexType.JSON)
        redis_search_client.create_index(schema, definition=definition)


create_redis_index()


@app.route('/query', methods=['GET'])
def query():
    search_term = request.args.get('search_term', '')

    # Query Oracle
    oracle_query = """
    SELECT TRACKID, NAME, ALBUMID, MEDIATYPEID, GENREID, COMPOSER, MILLISECONDS, BYTES, UNITPRICE
    FROM CHINOOK.TRACK
    WHERE NAME LIKE :search_term
    """
    oracle_start_time = time.time()
    oracle_cursor.execute(oracle_query, search_term=f'%{search_term}%')
    oracle_results = oracle_cursor.fetchall()
    oracle_latency = time.time() - oracle_start_time

    # Query Redis
    full_search_term = f'@NAME:{search_term}'
    redis_query = Query(full_search_term)
    redis_start_time = time.time()
    redis_results = redis_search_client.search(redis_query)
    redis_latency = time.time() - redis_start_time

    # Format Redis results
    formatted_redis_results = []
    for doc in redis_results.docs:
        try:
            # Parse the JSON string into a Python dictionary
            redis_data = json.loads(doc.json)

            # Append formatted result
            formatted_redis_results.append({
                "id": doc.id,
                "NAME": redis_data["NAME"],
                "TRACKID": redis_data["TRACKID"],
                "ALBUMID": redis_data["ALBUMID"],
                "MEDIATYPEID": redis_data["MEDIATYPEID"],
                "GENREID": redis_data["GENREID"],
                "COMPOSER": redis_data["COMPOSER"],
                "MILLISECONDS": redis_data["MILLISECONDS"],
                "BYTES": redis_data["BYTES"],
                "UNITPRICE": redis_data["UNITPRICE"]
            })
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing Redis JSON: {e}")
            # Print the whole JSON for debugging
            print(f"Raw JSON: {doc.json}")

    return jsonify({
        "oracle_results": oracle_results,
        "oracle_latency": oracle_latency,
        "redis_results": formatted_redis_results,
        "redis_latency": redis_latency
    })


if __name__ == "__main__":
    app.run(debug=True)
