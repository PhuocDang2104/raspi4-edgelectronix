import psycopg2
import time
import json
import redis

# ⚙️ Cấu hình kết nối PostgreSQL
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin'
}

