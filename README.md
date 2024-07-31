# Redis and Oracle Query Fanout

This project demonstrates how to fan out queries across Redis and Oracle databases to fetch and aggregate data efficiently. The application is configured to interface with both Redis and Oracle databases, ensuring seamless data retrieval and management.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.12
- Redis server
- Oracle Database

## Configuration

### Environment Variables

To run the project, you need to set up environment variables. Create a `.env` file in the project root directory and add the following variables:

```shell
REDIS_DATABASE_HOST=34.198.15.233
REDIS_DATABASE_PORT=19419
REDIS_DATABASE_PASSWORD=secret42
REDIS_INDEX_NAME=estab_sus
REDIS_INDEX_PREFIX=tb_estabelecimento_saude:
ORACLE_DATABASE_HOST=34.198.15.233
ORACLE_DATABASE_PORT=1521
ORACLE_DATABASE_SERVICE_NAME=ORCLPDB1
ORACLE_DATABASE_USER=c##dbzuser
ORACLE_DATABASE_PASSWORD=dbz
```

Replace the default values with those that apply to your setup.

## Installation

Clone the repository and navigate into the project directory:

```shell
git clone https://gacerioni/redis-and-oracle-query-fanout.git
cd redis-and-oracle-query-fanout
```

Make the bootstrap script executable:

```shell
chmod +x bootstrap.sh
```

Run the bootstrap script to set up the environment:
    
```shell
./bootstrap.sh
```

### EXTRA - Running the application directly from outside the bootstrap script

To run the application directly from outside the bootstrap script, simply run:

```shell
python3.12 -m flask run --host=0.0.0.0
```

## Usage

Navigate to http://localhost:5000 in your web browser to access the application. Use the provided web interface to perform queries and view the results from both Redis and Oracle databases.