# neo4j_client.py
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"  # Default local port
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "123456789"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_driver():
    return driver
