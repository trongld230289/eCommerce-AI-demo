"""
Neo4j Database Configuration for BEv2
"""

import os
from typing import Optional
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jDatabase:
    def __init__(self):
        """Initialize Neo4j database connection using environment variables"""
        # Load Neo4j configuration from environment variables
        self.uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
        self.username = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Test the connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise

    def get_driver(self):
        """Get Neo4j driver instance"""
        if self.driver is None:
            self._connect()
        return self.driver
    
    def close_connection(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

# Global database instance
neo4j_db = Neo4jDatabase()

def get_neo4j_driver():
    """Get Neo4j driver - main function to use in services"""
    return neo4j_db.get_driver()

def close_neo4j_connection():
    """Close Neo4j connection"""
    neo4j_db.close_connection()
