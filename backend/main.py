import asyncio
import os
import logging
import json
from typing import Dict, Any, List, Optional, TypedDict
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END
from cachetools import TTLCache
from sentence_transformers import SentenceTransformer, util
from langchain_openai import ChatOpenAI
import uuid
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class EventType(str, Enum):
    VIEW = "view"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    ADD_TO_WISHLIST = "add_to_wishlist"
    REMOVE_FROM_WISHLIST = "remove_from_wishlist"
    PURCHASE = "purchase"

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    original_price: Optional[float] = None
    imageUrl: str
    category: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    discount: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductCreate(BaseModel):
    name: str
    price: float
    original_price: Optional[float] = None
    imageUrl: str
    category: str
    description: Optional[str] = None
    rating: Optional[float] = None
    discount: Optional[float] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    imageUrl: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    discount: Optional[float] = None

class SearchFilters(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    keywords: Optional[str] = None
    tags: Optional[List[str]] = None

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class UserEvent(BaseModel):
    event_type: EventType
    user_id: str
    product_id: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class UserEventCreate(BaseModel):
    event_type: EventType
    user_id: str
    product_id: str
    metadata: Optional[Dict[str, Any]] = None

class UserEventResponse(BaseModel):
    success: bool
    message: str
    event_id: Optional[str] = None

class ChatbotRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str
    products: List[Product] = Field(default_factory=list)
    search_params: Dict[str, Any] = Field(default_factory=dict)
    redirect_url: Optional[str] = None
    page_code: Optional[str] = None
    smart_search_used: Optional[bool] = False
    parsed_filters: Dict[str, Any] = Field(default_factory=dict)

class SmartSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class SmartSearchResponse(BaseModel):
    query: str
    results: List[Product] = Field(default_factory=list)
    parsed_filters: Dict[str, Any] = Field(default_factory=dict)
    total_found: int
    search_type: str
    timestamp: str

class WishlistItem(BaseModel):
    product_id: int
    added_at: float

class WishlistItemWithDetails(BaseModel):
    product_id: int
    added_at: float
    product_details: Optional[Dict[str, Any]] = None

class Wishlist(BaseModel):
    id: str
    user_id: str
    name: str
    note: Optional[str] = None
    products: List[WishlistItemWithDetails] = Field(default_factory=list)
    item_count: int = 0
    created_at: float
    updated_at: float

class WishlistCreate(BaseModel):
    name: str
    user_id: str
    note: Optional[str] = None

class WishlistUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None

class WishlistAddProduct(BaseModel):
    product_id: int

class WishlistRemoveProduct(BaseModel):
    product_id: int

# Cart Models
class CartItem(BaseModel):
    product_id: int
    quantity: int
    added_at: float
    product_details: Optional[Dict[str, Any]] = None

class Cart(BaseModel):
    id: str
    user_id: str
    items: List[CartItem] = Field(default_factory=list)
    item_count: int = 0
    total_amount: float = 0.0
    created_at: float
    updated_at: float

class CartCreate(BaseModel):
    user_id: str

class CartAddItem(BaseModel):
    product_id: int
    quantity: int = 1

class CartUpdateItem(BaseModel):
    product_id: int
    quantity: int

class CartRemoveItem(BaseModel):
    product_id: int

# User Event Models for Recommendation System
class UserEvent(BaseModel):
    user_id: str
    event_type: EventType
    product_id: int
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class UserEventCreate(BaseModel):
    user_id: str
    event_type: EventType
    product_id: int
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Recommendation Models
class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
    category: Optional[str] = None
    context: Optional[str] = None  # "homepage", "product_detail", "cart", etc.

class AlgoRecommendationRequest(BaseModel):
    product_ids: List[int]
    user_id: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    user_id: Optional[str] = None
    source: str  # "personalized", "trending", "category_based", "fallback"
    context: Optional[str] = None
    total_count: int
    timestamp: datetime

# Gifting Recommendation
class GiftingRecommendationRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class GiftingRecommendationResponse(BaseModel):
    products: List[Dict[str, Any]]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

# Add CORS middleware to allow React frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"],  # Adjust to match your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for user query
class UserQuery(BaseModel):
    query: str
    user_id: str

# Pydantic model for user registration
class Neo4jUser(BaseModel):
    userId: str
    name: str
    email: str

# Neo4j connection parameters
class ConnectionParams:
    def __init__(self):
        self.env = {
            "NEO4J_URI": os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME", "neo4j"),
            "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", "password")
        }

# Initialize ChatOpenAI client for LangChain
def initialize_openai() -> Optional[ChatOpenAI]:
    """Initialize and return ChatOpenAI client"""
    try:
        endpoint = os.getenv("OPENAI_ENDPOINT", "https://aiportalapi.stu-platform.live/jpe")
        api_key = os.getenv("OPENAI_API_KEY", "sk-82_4lHOVbs5TtCsLP1ZJOA")
        logger.info(f"Initializing ChatOpenAI with endpoint: {endpoint}")
        if not endpoint or not api_key:
            raise ValueError("OPENAI_ENDPOINT or OPENAI_API_KEY not set in environment variables")
        client = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=endpoint,
            model="GPT-4o-mini",
            temperature=0.7
        )
        logger.info("ChatOpenAI client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Error initializing ChatOpenAI client: {e}", exc_info=True)
        return None

# MCPToolset with cached schema using SchemaMetadata
class MCPToolset:
    def __init__(self, connection_params: ConnectionParams):
        self.driver = GraphDatabase.driver(
            connection_params.env["NEO4J_URI"],
            auth=(connection_params.env["NEO4J_USERNAME"], connection_params.env["NEO4J_PASSWORD"])
        )
        self.cache = TTLCache(maxsize=1, ttl=3600)  # Cache schema for 1 hour

    def get_neo4j_schema_cached(self) -> Dict[str, Any]:
        if "schema" in self.cache:
            logger.info("Returning cached schema")
            return self.cache["schema"]
        
        try:
            with self.driver.session() as session:
                # Get node labels and properties
                node_result = session.run("""
                    CALL db.schema.nodeTypeProperties()
                    YIELD nodeType, propertyName, propertyTypes
                    RETURN nodeType, collect({name: propertyName, types: propertyTypes}) AS properties
                """)
                node_schema = [
                    {"label": r["nodeType"].lstrip(":").replace("`", ""), "properties": r["properties"]}
                    for r in node_result
                ]

                # Get relationship types and properties
                rel_result = session.run("""
                    CALL db.schema.relTypeProperties()
                    YIELD relType, propertyName, propertyTypes
                    RETURN relType, collect({name: propertyName, types: propertyTypes}) AS properties
                """)
                rel_schema = [
                    {"type": r["relType"].lstrip(":-").strip("-:").replace("`", ""), "properties": r["properties"]}
                    for r in rel_result
                ]

                # Get detailed descriptions from SchemaMetadata
                desc_result = session.run("""
                    MATCH (m:SchemaMetadata)
                    RETURN m.type AS type, m.label AS label, m.property AS property, m.description AS description
                """)
                descriptions = {}
                for r in desc_result:
                    if r["type"] == "NodeLabel":
                        descriptions.setdefault("nodes", {})[r["label"]] = r["description"]
                    elif r["type"] == "Property":
                        key = f"{r['label']}.{r['property']}" if r["property"] else r["label"]
                        descriptions.setdefault("properties", {})[key] = r["description"]

                # Combine schema with descriptions
                for node in node_schema:
                    node["description"] = descriptions.get("nodes", {}).get(node["label"], "")
                    for prop in node["properties"]:
                        prop_key = f"{node['label']}.{prop['name']}"
                        prop["description"] = descriptions.get("properties", {}).get(prop_key, "")
                for rel in rel_schema:
                    rel["description"] = descriptions.get("relationships", {}).get(rel["type"], "")
                    for prop in rel["properties"]:
                        prop_key = f"{rel['type']}.{prop['name']}"
                        prop["description"] = descriptions.get("properties", {}).get(prop_key, "")

                schema = {
                    "nodes": node_schema,
                    "relationships": rel_schema
                }
                self.cache["schema"] = schema
                logger.info("Schema retrieved and cached successfully")
                return schema
        except Exception as e:
            logger.error(f"Error retrieving schema: {str(e)}")
            return {}

    def run_cypher_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error running Cypher query: {str(e)}")
            return []

    def close(self):
        """Close the Neo4j driver"""
        self.driver.close()

# Semantic similarity tool
class SemanticTool:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_tag_combinations(self, tags: List[str], query: str, top_k: int = 50) -> List[List[str]]:
        mcp = MCPToolset(ConnectionParams())
        result = mcp.run_cypher_query("""
            MATCH (p:Product)
            WHERE p.tags IS NOT NULL
            RETURN DISTINCT p.tags AS tags
        """)
        tag_combinations = [r["tags"] for r in result if r["tags"]]

        query_embedding = self.model.encode(query, convert_to_tensor=True)
        similarities = []
        for tags in tag_combinations:
            tag_str = " ".join(tags)
            tag_embedding = self.model.encode(tag_str, convert_to_tensor=True)
            similarity = util.cos_sim(query_embedding, tag_embedding).item()
            similarities.append((tags, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return [tags for tags, _ in similarities[:top_k]]

# LangGraph state
class WorkflowState(TypedDict):
    query: str
    user_id: str
    schema: Dict[str, Any]
    relevant_nodes: List[str]
    relevant_rels: List[str]
    product_ids: List[str]
    cypher_query: str
    parameters: Dict[str, Any]
    results: List[Dict[str, Any]]
    response: str
    can_process: bool
    inferred_tags: List[str]

# Gifting Workflow State
class GiftingWorkflowState(TypedDict):
    query: str
    user_id: Optional[str]
    step1_product_ids: List[int]
    step2_product_ids: List[int]
    distinct_combined_product_ids: List[int]
    wishlist_top5: List[int]
    purchase_top5: List[int]
    final_products: List[Dict[str, Any]]

# LangChain LLM setup
llm = initialize_openai()

# LangGraph workflow
def create_workflow():
    graph = StateGraph(WorkflowState)

    def fetch_schema(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Fetching schema for query: {state['query']}, state: {state}")
        mcp = MCPToolset(ConnectionParams())
        schema = mcp.get_neo4j_schema_cached()
        logger.info(f"Schema fetched: {schema}")
        return {"schema": schema, "relevant_nodes": [], "relevant_rels": []}

    def analyze_query(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Analyzing query: {state['query']}, state: {state}")
        prompt = PromptTemplate(
            input_variables=["query", "schema"],
            template="""
            Given the user query: {query}
            And the Neo4j schema: {schema}

            Determine which nodes and relationships are relevant to answer the query.
            Return a JSON object wrapped in ```json\n...\n``` with:
            - nodes: List of relevant node labels
            - relationships: List of relevant relationship types
            - can_process: Boolean indicating if Neo4j can process the query
            - message: String, if can_process is False, explaining why (e.g., query too vague like "Arena")
            """
        )
        schema_str = json.dumps(state["schema"])
        if llm:
            try:
                response = llm.invoke(prompt.format(query=state["query"], schema=schema_str))
                raw_content = response.content
                logger.info(f"Raw LLM response: {raw_content}")
                
                # Strip markdown code block markers if present
                content = raw_content.strip()
                if content.startswith("```json\n") and content.endswith("\n```"):
                    content = content[8:-4].strip()
                elif content.startswith("```") and content.endswith("```"):
                    content = content[3:-3].strip()
                
                # Check if content is empty
                if not content:
                    logger.error("LLM response is empty after stripping")
                    return {
                        "relevant_nodes": [],
                        "relevant_rels": [],
                        "can_process": False,
                        "response": "Query analysis failed: Empty LLM response"
                    }
                
                # Attempt to parse JSON
                result = json.loads(content)
                logger.info(f"Query analysis result: {result}")
                
                # Clean up node labels (remove backticks if present)
                nodes = [node.strip("`") for node in result.get("nodes", [])]
                
                # Prepare state update
                state_update = {
                    "relevant_nodes": nodes,
                    "relevant_rels": result.get("relationships", []),
                    "can_process": result.get("can_process", False),
                    "response": result.get("message", "")
                }
                logger.info(f"State update from analyze_query: {state_update}")
                
                return state_update
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}, content: {content}")
                return {
                    "relevant_nodes": [],
                    "relevant_rels": [],
                    "can_process": False,
                    "response": f"Query analysis failed due to invalid LLM response: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Error during query analysis: {e}")
                return {
                    "relevant_nodes": [],
                    "relevant_rels": [],
                    "can_process": False,
                    "response": f"Query analysis failed: {str(e)}"
                }
        logger.warning("LLM not available for query analysis")
        return {
            "relevant_nodes": [],
            "relevant_rels": [],
            "can_process": False,
            "response": "LLM not available for query analysis"
        }

    def semantic_filter(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Applying semantic filter for query: {state['query']}, state: {state}")
        
        # Initialize can_process and inferred_tags
        state["can_process"] = False
        state["inferred_tags"] = []  # Store inferred tags for Product queries
        
        # Check if relevant nodes are identified
        if not state.get("relevant_nodes"):
            logger.warning("No relevant nodes identified, cannot process query")
            state["response"] = (
                f"No relevant entities found for query '{state['query']}'. "
                "Please check the query or schema."
            )
            return state

        # Step 1: Check if product tags can be inferred for Product-related queries
        if "Product" in state["relevant_nodes"] and llm:
            tag_inference_prompt = PromptTemplate(
                input_variables=["query"],
                template="""
                Given the user query: {query}
                
                Determine if the query implies specific product tags or categories that can be used to search for products in a Neo4j database. Product tags are labels or categories (e.g., 'electronics', 'clothing', 'mobile phone', 'musical instrument') that describe products. Tags can be inferred even if the query does not explicitly mention 'tag', 'category', or similar terms, based on the query's intent (e.g., 'mobile phones' implies the tag 'mobile phone', 'gadgets' implies 'electronics').
                
                Return a JSON object wrapped in ```json\n...\n``` with:
                - can_infer_tags: boolean (true if tags can be inferred, false otherwise)
                - reason: string (explanation for the decision)
                """
            )
            try:
                response = llm.invoke(tag_inference_prompt.format(query=state["query"]))
                content = response.content.strip()
                if content.startswith("```json\n") and content.endswith("\n```"):
                    content = content[8:-4].strip()
                elif content.startswith("```") and content.endswith("```"):
                    content = content[3:-3].strip()
                
                tag_inference_result = json.loads(content)
                logger.info(f"Tag inference result: {tag_inference_result}")
                
                if tag_inference_result.get("can_infer_tags", False):
                    # Step 2: Collect distinct product tags from Neo4j
                    mcp = MCPToolset(ConnectionParams())
                    try:
                        tag_query = """
                        MATCH (p:Product)
                        WHERE p.tags IS NOT NULL
                        RETURN DISTINCT p.tags AS tags
                        """
                        tag_results = mcp.run_cypher_query(tag_query)
                        all_tags = []
                        for record in tag_results:
                            if record["tags"]:
                                all_tags.extend(record["tags"])  # Flatten the list of tags
                        all_tags = list(set(all_tags))  # Remove duplicates
                        logger.info(f"Collected distinct tags: {all_tags}")
                    finally:
                        mcp.close()

                    if not all_tags:
                        logger.warning("No product tags found in Neo4j")
                        state["response"] = (
                            f"No product tags available in the database for query '{state['query']}'."
                        )
                        # Proceed to general validation instead of returning
                    else:
                        # Step 3: Determine which tags are relevant to the user query
                        tag_matching_prompt = PromptTemplate(
                            input_variables=["query", "tags"],
                            template="""
                            Given the user query and a list of available product tags from a Neo4j database:
                            - Query: {query}
                            - Available Tags: {tags}
                            
                            Identify which tags from the provided list are relevant to the user's query based on their intent. For example, a query about 'mobile phones' may match the tag 'mobile phone', or 'gadgets' may match 'electronics'. Return a JSON object wrapped in ```json\n...\n``` with:
                            - relevant_tags: list of strings (tags that match the query's intent)
                            - reason: string (explanation for the selection)
                            """
                        )
                        try:
                            response = llm.invoke(
                                tag_matching_prompt.format(
                                    query=state["query"],
                                    tags=json.dumps(all_tags)
                                )
                            )
                            content = response.content.strip()
                            if content.startswith("```json\n") and content.endswith("\n```"):
                                content = content[8:-4].strip()
                            elif content.startswith("```") and content.endswith("```"):
                                content = content[3:-3].strip()
                            
                            tag_matching_result = json.loads(content)
                            state["inferred_tags"] = tag_matching_result.get("relevant_tags", [])
                            logger.info(f"Tag matching result: {tag_matching_result}")
                            
                            if not state["inferred_tags"]:
                                logger.info(f"No relevant tags matched: {tag_matching_result.get('reason', 'No matching tags found.')}")
                                # Proceed to general validation
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse tag matching LLM response: {e}, content: {content}")
                            # Proceed to general validation
                        except Exception as e:
                            logger.error(f"Tag matching LLM call failed: {e}")
                            # Proceed to general validation
                else:
                    logger.info(f"Cannot infer tags: {tag_inference_result.get('reason', 'Unknown reason')}")
                    # Proceed to general validation
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tag inference LLM response: {e}, content: {content}")
                # Proceed to general validation
            except Exception as e:
                logger.error(f"Tag inference LLM call failed: {e}")
                # Proceed to general validation
        else:
            logger.info("No Product node or LLM unavailable, skipping tag inference")

        # Step 4: General validation for query feasibility using LLM
        if llm:
            validation_prompt = PromptTemplate(
                input_variables=["query", "schema", "relevant_nodes", "relevant_rels", "inferred_tags"],
                template="""
                Given the user query, schema, identified relevant nodes and relationships, and any inferred product tags:
                - Query: {query}
                - Schema: {schema}
                - Relevant Nodes: {relevant_nodes}
                - Relevant Relationships: {relevant_rels}
                - Inferred Product Tags (if any): {inferred_tags}
                
                Generate the Cypher query to process the user query. The output of the query should be the list of product_ids in the format RETURN p.productId AS product_id.
                If inferred tags are provided and the query involves Product nodes, use them for filtering products by checking for overlap between p.tags and the inferred tags.
                Use the parameter name $filter_tags for the list of inferred tags, and filter using: WHERE ANY(tag IN $filter_tags WHERE tag IN p.tags)
                Ensure the Cypher query is valid and uses parameters correctly.
                Return a JSON object wrapped in ```json\n...\n``` with:
                - can_process: boolean (true if the Cypher can be generated, false otherwise)
                - reason: string (explanation for the decision)
                - cypher: string (the generated Cypher query)
                - parameters: object (key-value pairs for query parameters, e.g., {{"filter_tags": ["electronics"]}})
                """
            )
            try:
                response = llm.invoke(
                    validation_prompt.format(
                        query=state["query"],
                        schema=json.dumps(state["schema"], indent=2),
                        relevant_nodes=json.dumps(state["relevant_nodes"]),
                        relevant_rels=json.dumps(state["relevant_rels"]),
                        inferred_tags=json.dumps(state["inferred_tags"])
                    )
                )
                content = response.content.strip()
                if content.startswith("```json\n") and content.endswith("\n```"):
                    content = content[8:-4].strip()
                elif content.startswith("```") and content.endswith("```"):
                    content = content[3:-3].strip()
                
                validation_result = json.loads(content)
                if not isinstance(validation_result, dict):
                    raise ValueError(f"LLM returned non-dictionary JSON: {validation_result}")
                logger.info(f"Query validation result: {validation_result}")
                
                state["can_process"] = validation_result.get("can_process", False)
                
                if state["can_process"]:
                    cypher = validation_result.get("cypher", "")
                    parameters = validation_result.get("parameters", {})
                    if not isinstance(parameters, dict):
                        raise ValueError(f"Parameters is not a dictionary: {parameters}")
                    if cypher:
                        mcp = MCPToolset(ConnectionParams())
                        try:
                            product_results = mcp.run_cypher_query(cypher, parameters)
                            state['product_ids'] = [r['product_id'] for r in product_results if 'product_id' in r]
                        finally:
                            mcp.close()
                    else:
                        state['product_ids'] = []
                        state["can_process"] = False
                        state["response"] = (
                            f"Cannot process query '{state['query']}': No Cypher query generated."
                        )
                else:
                    state["response"] = (
                        f"Cannot process query '{state['query']}': {validation_result.get('reason', 'Unknown reason')}"
                    )
                    return state
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse validation LLM response: {e}, content: {content}")
                state["response"] = (
                    f"Failed to validate query '{state['query']}': Invalid LLM response."
                )
                return state
            except Exception as e:
                logger.error(f"Query validation LLM call failed: {e}")
                state["response"] = (
                    f"Failed to validate query '{state['query']}': {str(e)}."
                )
                return state
        else:
            logger.warning("LLM not available for query validation")
            # Fallback: Allow tag-based queries if inferred_tags exist
            if state["inferred_tags"]:
                state["can_process"] = True
                logger.info("Falling back to can_process=True for tag-based Product query")
            else:
                state["response"] = (
                    f"Cannot process query '{state['query']}': LLM not available."
                )
                return state

        # Step 5: Set can_process to True if validation passes
        state["can_process"] = True
        logger.info(f"Query validated, inferred_tags: {state['inferred_tags']}, setting can_process=True")
        return state

    def validate_results(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Validating results for query: {state['query']}, state: {state}")
        if not state.get("product_ids", []):
            logger.info("No product_ids found, attempting RAG search")
            if llm:
                try:
                    rag_result = llm.invoke(f"Perform RAG search for query: {state['query']} and return a JSON object wrapped in ```json\n...\n``` with a 'product_ids' key containing a list of product IDs.")
                    raw_content = rag_result.content
                    logger.info(f"Raw RAG response: {raw_content}")
                    
                    # Strip markdown code block markers if present
                    content = raw_content.strip()
                    if content.startswith("```json\n") and content.endswith("\n```"):
                        content = content[8:-4].strip()
                    elif content.startswith("```") and content.endswith("```"):
                        content = content[3:-3].strip()
                    
                    # Check if content is empty
                    if not content:
                        logger.error("RAG response is empty after stripping")
                        return {"product_ids": []}
                    
                    # Attempt to parse JSON
                    result = json.loads(content)
                    product_ids = result.get("product_ids", [])
                    logger.info(f"RAG search found product_ids: {product_ids}")
                    return {"product_ids": product_ids}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse RAG response as JSON: {e}, content: {content}")
                    return {"product_ids": []}
                except Exception as e:
                    logger.error(f"Error during RAG search: {e}")
                    return {"product_ids": []}
            logger.warning("LLM not available for RAG search")
            return {"product_ids": []}
        logger.info("Results validated, using existing product_ids")
        return {"product_ids": state.get("product_ids", [])}

    def generate_cypher(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Generating Cypher for fetching product details: {state['query']}, state: {state}")
        product_ids = state.get("product_ids", [])
        if not product_ids:
            logger.info("No product_ids, skipping Cypher generation")
            return {"cypher_query": "", "parameters": {}}
        
        cypher = """
        MATCH (p:Product)
        WHERE p.productId IN $product_ids
        RETURN p.productId, p.name, p.description, p.price
        """
        # Attempt to convert product_ids to integers if possible
        try:
            product_ids = [int(pid) for pid in product_ids if pid.isdigit()]
        except:
            pass
        parameters = {"product_ids": product_ids}
        logger.info(f"Generated Cypher for details: {cypher}, params: {parameters}")
        return {"cypher_query": cypher, "parameters": parameters}

    def execute_cypher(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Executing Cypher query: {state['cypher_query']}, state: {state}")
        if state.get("cypher_query"):
            mcp = MCPToolset(ConnectionParams())
            results = mcp.run_cypher_query(state["cypher_query"], state.get("parameters", {}))
            logger.info(f"Execution results: {results}")
            return {"results": results}
        logger.info("No Cypher query to execute")
        return {"results": []}

    def format_response(state: WorkflowState) -> Dict[str, Any]:
        logger.info(f"Formatting response for query: {state['query']}, state: {state}")
        
        # Check if a response is already set
        if state.get("response"):
            logger.info(f"Returning existing response: {state['response']}")
            return {"response": state["response"]}
        
        # Check if results are empty
        if not state.get("results", []):
            logger.info("No results found for query")
            default_response = (
                f"No products found for query '{state['query']}'. Please try a different query."
            )
            return {"response": default_response}
        
        # Format results using LLM
        if llm:
            prompt = PromptTemplate(
                input_variables=["query", "results"],
                template="""
                Format the results for the user query: {query}
                Results: {results}
                Return a user-friendly response summarizing the products, including productId, name, description, and price.
                Example:
                Found 2 products:
                - Product ID: 123, Name: Gadget X, Description: A high-tech gadget, Price: $99.99
                - Product ID: 456, Name: Gizmo Y, Description: A smart device, Price: $149.99
                """
            )
            try:
                response = llm.invoke(prompt.format(query=state["query"], results=json.dumps(state["results"])))
                formatted_response = response.content.strip()
                logger.info(f"Formatted response: {formatted_response}")
                if not formatted_response:
                    logger.warning("LLM returned empty response, using default")
                    return {
                        "response": (
                            f"No products found for query '{state['query']}'. Please try a different query."
                        )
                    }
                return {"response": formatted_response}
            except Exception as e:
                logger.error(f"Failed to format response: {e}")
                return {
                    "response": (
                        f"Failed to format response for '{state['query']}': {str(e)}. "
                        "Please try again or contact support."
                    )
                }
        logger.warning("LLM not available for response formatting")
        return {
            "response": (
                f"No response generated for '{state['query']}' due to missing LLM. "
                "Please try again or contact support."
            )
        }

    # Define workflow nodes
    graph.add_node("fetch_schema", fetch_schema)
    graph.add_node("analyze_query", analyze_query)
    graph.add_node("semantic_filter", semantic_filter)
    graph.add_node("validate_results", validate_results)
    graph.add_node("generate_cypher", generate_cypher)
    graph.add_node("execute_cypher", execute_cypher)
    graph.add_node("format_response", format_response)

    # Define edges
    graph.add_edge("fetch_schema", "analyze_query")
    graph.add_conditional_edges(
        "analyze_query",
        lambda state: "semantic_filter" if state.get("can_process", False) else "format_response",
        {
            "semantic_filter": "semantic_filter",
            "format_response": "format_response"
        }
    )
    graph.add_edge("semantic_filter", "validate_results")
    graph.add_edge("validate_results", "generate_cypher")
    graph.add_edge("generate_cypher", "execute_cypher")
    graph.add_edge("execute_cypher", "format_response")
    graph.add_edge("format_response", END)

    graph.set_entry_point("fetch_schema")
    return graph.compile()

# Create gifting LangGraph workflow
def create_gifting_workflow():
    graph = StateGraph(GiftingWorkflowState)

    def step1_filter_conditions(state: GiftingWorkflowState) -> Dict[str, Any]:
        logger.info(f"Entering step1_filter_conditions with state: {state}")
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Analyze the user query: {query}
            
            Determine if the query specifies exact values for these product fields. Be certain - no guessing. If not explicitly mentioned, do not include.
            Fields:
            - targetGenders (array, e.g., ['male', 'female', 'unisex'])
            - giftingSymbolicValue (string: 'high', 'medium', 'low')
            - giftingUtilitarianScore (float 0-1)
            - giftingPriceRange (string: 'low', 'mid', 'high')
            - giftingNoveltyScore (float 0-1)
            - giftingAltruismSuitability (string: 'high', 'medium', 'low')
            - giftingReciprocityFit (string: 'high', 'medium', 'low')
            - giftingSelfGiftingSuitability (string: 'high', 'medium', 'low')
            - giftingPowerSignaling (string: 'high', 'medium', 'low')
            
            For each field that has an exact value in the query, provide a Cypher condition snippet, e.g., "p.giftingSymbolicValue = 'high'" or "ANY(g IN ['male'] WHERE g IN p.targetGenders)".
            
            Respond with only the JSON object and nothing else: {{"conditions": ["cypher_condition1", "cypher_condition2", ...]}}
            """
        )
        logger.info("Invoking LLM for main conditions prompt")
        response = llm.invoke(prompt.format(query=state["query"]))
        content = response.content.strip()
        logger.info(f"Raw LLM response for conditions: {content}")
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            logger.info(f"Matched JSON string: {json_str}")
            try:
                result = json.loads(json_str)
                logger.info(f"Successfully parsed conditions: {result}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON for conditions: {e}, json_str: {json_str}")
                result = {"conditions": []}
        else:
            logger.warning("No valid JSON found in LLM response for conditions")
            result = {"conditions": []}  # Fallback to empty conditions if no JSON found
        conditions = result.get("conditions", [])
        logger.info(f"Extracted conditions: {conditions}")

        # Get distinct categories
        logger.info("Executing Cypher query to get distinct categories")
        mcp = MCPToolset(ConnectionParams())
        categories_query = """
        MATCH (p:Product)
        UNWIND p.giftingCategories AS cat
        RETURN DISTINCT cat AS category
        """
        categories_results = mcp.run_cypher_query(categories_query)
        logger.info(f"Raw results from categories query: {categories_results}")
        all_categories = [r['category'] for r in categories_results]
        logger.info(f"Distinct categories: {all_categories}")

        categories_prompt = PromptTemplate(
            input_variables=["query", "categories"],
            template="""
            User query: {query}
            Available categories: {categories}
            
            Determine if the query implies specific categories from the available list. Be certain - no guessing. If not explicitly or clearly implied, return empty list.
            
            Respond with only the JSON object and nothing else: {{"categories": ["implied_cat1", "implied_cat2", ...]}}
            """
        )
        logger.info("Invoking LLM for categories prompt")
        response = llm.invoke(categories_prompt.format(query=state["query"], categories=json.dumps(all_categories)))
        content = response.content.strip()
        logger.info(f"Raw LLM response for categories: {content}")
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            logger.info(f"Matched JSON string for categories: {json_str}")
            try:
                result = json.loads(json_str)
                logger.info(f"Successfully parsed categories: {result}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON for categories: {e}, json_str: {json_str}")
                result = {"categories": []}
        else:
            logger.warning("No valid JSON found in LLM response for categories")
            result = {"categories": []}
        implied_categories = result.get("categories", [])
        logger.info(f"Implied categories: {implied_categories}")
        categories_cypher = "ANY(cat IN $categories WHERE cat IN p.giftingCategories)" if implied_categories else ""
        logger.info(f"Categories cypher condition: {categories_cypher}")

        # Get distinct giftingRelationshipTypes
        logger.info("Executing Cypher query to get distinct relationship types")
        rel_types_query = """
        MATCH (p:Product)
        UNWIND p.giftingRelationshipTypes AS rel
        RETURN DISTINCT rel AS relType
        """
        rel_types_results = mcp.run_cypher_query(rel_types_query)
        logger.info(f"Raw results from rel_types query: {rel_types_results}")
        all_rel_types = [r['relType'] for r in rel_types_results]
        logger.info(f"Distinct relationship types: {all_rel_types}")

        rel_types_prompt = PromptTemplate(
            input_variables=["query", "rel_types"],
            template="""
            User query: {query}
            Available relationship types: {rel_types}
            
            Determine if the query implies specific relationship types from the available list. Be certain - no guessing. If not explicitly or clearly implied, return empty list.
            
            Respond with only the JSON object and nothing else: {{"rel_types": ["implied_rel1", "implied_rel2", ...]}}
            """
        )
        logger.info("Invoking LLM for rel_types prompt")
        response = llm.invoke(rel_types_prompt.format(query=state["query"], rel_types=json.dumps(all_rel_types)))
        content = response.content.strip()
        logger.info(f"Raw LLM response for rel_types: {content}")
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            logger.info(f"Matched JSON string for rel_types: {json_str}")
            try:
                result = json.loads(json_str)
                logger.info(f"Successfully parsed rel_types: {result}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON for rel_types: {e}, json_str: {json_str}")
                result = {"rel_types": []}
        else:
            logger.warning("No valid JSON found in LLM response for rel_types")
            result = {"rel_types": []}
        implied_rel_types = result.get("rel_types", [])
        logger.info(f"Implied rel_types: {implied_rel_types}")
        rel_types_cypher = "ANY(rel IN $rel_types WHERE rel IN p.giftingRelationshipTypes)" if implied_rel_types else ""
        logger.info(f"Rel types cypher condition: {rel_types_cypher}")

        mcp.close()
        logger.info("Closed MCP connection after fetching categories and rel_types")

        # Merge cyphers
        where_clauses = conditions
        if categories_cypher:
            where_clauses.append(categories_cypher)
        if rel_types_cypher:
            where_clauses.append(rel_types_cypher)
        logger.info(f"Merged where clauses: {where_clauses}")

        product_ids = []
        if where_clauses:
            merged_cypher = "MATCH (p:Product)\nWHERE " + " AND ".join(where_clauses) + "\nRETURN p.productId AS product_id"
            logger.info(f"Generated merged Cypher query: {merged_cypher}")
            parameters = {}
            if categories_cypher:
                parameters["categories"] = implied_categories
                logger.info(f"Added categories parameter: {parameters['categories']}")
            if rel_types_cypher:
                parameters["rel_types"] = implied_rel_types
                logger.info(f"Added rel_types parameter: {parameters['rel_types']}")
            logger.info(f"Full parameters for merged query: {parameters}")
            mcp = MCPToolset(ConnectionParams())
            try:
                logger.info("Executing merged Cypher query")
                results = mcp.run_cypher_query(merged_cypher, parameters)
                logger.info(f"Raw results from merged query: {results}")
                product_ids = [r['product_id'] for r in results]
                logger.info(f"Extracted product_ids: {product_ids}")
            finally:
                mcp.close()
                logger.info("Closed MCP connection after executing merged query")
        else:
            logger.info("No where clauses present, skipping merged query execution. product_ids remains empty.")

        logger.info(f"Returning from step1_filter_conditions with step1_product_ids: {product_ids}")
        return {"step1_product_ids": product_ids}

    def step2_rag(state: GiftingWorkflowState) -> Dict[str, Any]:
        logger.info(f"Entering step2_rag with state: {state}")
        refine_prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Refine the user query for product search based on description. Exclude gifting-related info, focus on the product itself as if the user is buying for themselves.
            
            Original query: {query}
            
            Return the refined query as string.
            """
        )
        logger.info("Invoking LLM for query refinement")
        response = llm.invoke(refine_prompt.format(query=state["query"]))
        refined_query = response.content.strip()
        logger.info(f"Refined query from LLM: {refined_query}")

        # Perform RAG
        # Update to have the RAG in the main BE as the BE on the refined query

        similarities = []
        logger.info("Similarities list is empty (placeholder for actual RAG implementation)")

        similarities.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Sorted similarities: {similarities}")
        rag_product_ids = [pid for pid, _ in similarities[:10]]  # Top 10 from RAG
        logger.info(f"Extracted rag_product_ids (top 10): {rag_product_ids}")

        logger.info(f"Returning from step2_rag with step2_product_ids: {rag_product_ids}")
        return {"step2_product_ids": rag_product_ids}

    def step3_combine_and_rank(state: GiftingWorkflowState) -> Dict[str, Any]:
        logger.info(f"Entering step3_combine_and_rank with state: {state}")
        step1_ids = state.get("step1_product_ids", [])
        step2_ids = state.get("step2_product_ids", [])
        logger.info(f"step1_product_ids: {step1_ids}, step2_product_ids: {step2_ids}")
        combined_ids = list(set(step1_ids + step2_ids))
        logger.info(f"Combined unique product ids: {combined_ids}")

        # Count distinct wishlists
        logger.info("Executing Cypher query for wishlist counts")
        mcp = MCPToolset(ConnectionParams())
        wishlist_count_query = """
        UNWIND $product_ids AS pid
        MATCH (w:Wishlist)-[:CONTAINS]->(p:Product {productId: pid})
        WITH pid, COUNT(DISTINCT w) AS wishlist_count
        RETURN pid, wishlist_count
        ORDER BY wishlist_count DESC
        LIMIT 5
        """
        logger.info(f"Wishlist count query parameters: {{'product_ids': {combined_ids}}}")
        wishlist_results = mcp.run_cypher_query(wishlist_count_query, {"product_ids": combined_ids})
        logger.info(f"Raw wishlist results: {wishlist_results}")
        wishlist_top5 = [r['pid'] for r in wishlist_results]
        logger.info(f"wishlist_top5: {wishlist_top5}")

        # Count purchase quantity
        logger.info("Executing Cypher query for purchase counts")
        purchase_count_query = """
        UNWIND $product_ids AS pid
        MATCH (e:InteractionEvent {eventType: 'purchase'})-[:TARGETS]->(p:Product {productId: pid})
        WITH pid, SUM(e.value) AS purchase_quantity
        RETURN pid, purchase_quantity
        ORDER BY purchase_quantity DESC
        LIMIT 5
        """
        logger.info(f"Purchase count query parameters: {{'product_ids': {combined_ids}}}")
        purchase_results = mcp.run_cypher_query(purchase_count_query, {"product_ids": combined_ids})
        logger.info(f"Raw purchase results: {purchase_results}")
        purchase_top5 = [r['pid'] for r in purchase_results]
        logger.info(f"purchase_top5: {purchase_top5}")

        mcp.close()
        logger.info("Closed MCP connection after wishlist and purchase queries")

        logger.info(f"Returning from step3_combine_and_rank with distinct_combined_product_ids: {combined_ids}, wishlist_top5: {wishlist_top5}, purchase_top5: {purchase_top5}")
        return {"distinct_combined_product_ids": combined_ids, "wishlist_top5": wishlist_top5, "purchase_top5": purchase_top5}

    def step4_final_products(state: GiftingWorkflowState) -> Dict[str, Any]:
        logger.info(f"Entering step4_final_products with state: {state}")
        combined_ids = state.get("distinct_combined_product_ids", [])[:15]
        logger.info(f"Limited combined_ids (top 15): {combined_ids}")
        wishlist_top5 = state.get("wishlist_top5", [])
        purchase_top5 = state.get("purchase_top5", [])
        logger.info(f"wishlist_top5: {wishlist_top5}, purchase_top5: {purchase_top5}")

        logger.info("Executing Cypher query to fetch final products")
        mcp = MCPToolset(ConnectionParams())
        products_query = """
        MATCH (p:Product)
        WHERE p.productId IN $product_ids
        RETURN p.productId AS id, p.name AS name, p.description AS description, p.price AS price
        """
        logger.info(f"Products query parameters: {{'product_ids': {combined_ids}}}")
        results = mcp.run_cypher_query(products_query, {"product_ids": combined_ids})
        logger.info(f"Raw results from products query: {results}")
        mcp.close()
        logger.info("Closed MCP connection after products query")

        final_products = []
        for r in results:
            product = {
                "id": r["id"],
                "name": r["name"],
                "description": r["description"],
                "price": r["price"],
                "tags": []
            }
            if r["id"] in wishlist_top5:
                product["tags"].append("most_added_to_wishlist")
                logger.info(f"Added 'most_added_to_wishlist' tag to product {r['id']}")
            if r["id"] in purchase_top5:
                product["tags"].append("most_purchased")
                logger.info(f"Added 'most_purchased' tag to product {r['id']}")
            final_products.append(product)
        logger.info(f"Constructed final_products: {final_products}")

        logger.info(f"Returning from step4_final_products with final_products: {final_products}")
        return {"final_products": final_products}

    graph.add_node("step1_filter_conditions", step1_filter_conditions)
    graph.add_node("step2_rag", step2_rag)
    graph.add_node("step3_combine_and_rank", step3_combine_and_rank)
    graph.add_node("step4_final_products", step4_final_products)

    graph.set_entry_point("step1_filter_conditions")
    graph.add_edge("step1_filter_conditions", "step2_rag")
    graph.add_edge("step2_rag", "step3_combine_and_rank")
    graph.add_edge("step3_combine_and_rank", "step4_final_products")
    graph.add_edge("step4_final_products", END)

    return graph.compile()

# New endpoint to register user in Neo4j
@app.post("/register-user")
async def register_user(user: Neo4jUser):
    logger.info(f"Registering user in Neo4j: {user.userId}, {user.name}, {user.email}")
    mcp = MCPToolset(ConnectionParams())
    
    try:
        # Check if user exists
        check_query = """
        MATCH (u:User {userId: $userId})
        RETURN u;
        """
        result = mcp.run_cypher_query(check_query, {"userId": user.userId})
        
        if result:
            logger.info(f"User {user.userId} already exists in Neo4j")
            return {"message": f"User {user.userId} already exists in Neo4j"}
        
        # Create new user if not exists
        create_query = """
        CREATE (u:User)
        SET u.userId = $userId,
            u.name = $name,
            u.email = $email,
            u.hedonicBias = $hedonicBias,
            u.surprisePreference = $surprisePreference,
            u.altruismLevel = $altruismLevel,
            u.reciprocityExpectation = $reciprocityExpectation
        RETURN u;
        """
        params = {
            "userId": user.userId,
            "name": user.name,
            "email": user.email,
            "hedonicBias": 0.7,  # Default from schema
            "surprisePreference": 0.5,  # Neutral initial value
            "altruismLevel": 0.3,  # Low to moderate initial value
            "reciprocityExpectation": 0.2  # Low initial value
        }
        result = mcp.run_cypher_query(create_query, params)
        
        if result:
            logger.info(f"User registered successfully: {result[0]['u']}")
            return {"message": f"User {user.userId} registered successfully in Neo4j"}
        else:
            logger.error("Failed to create user node in Neo4j")
            raise HTTPException(status_code=500, detail="Failed to register user in Neo4j")
    except Exception as e:
        logger.error(f"Error registering user in Neo4j: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")
    finally:
        mcp.close()

# FastAPI endpoint
@app.post("/query")
async def handle_query(query: SmartSearchRequest):
    logger.info(f"Received query: {query.query}")
    workflow = create_workflow()
    state = {
        "query": query.query,
        "schema": {},  # Assume schema is populated elsewhere
        "relevant_nodes": [],
        "relevant_rels": [],
        "product_ids": [],
        "cypher_query": "",
        "parameters": {},
        "results": [],
        "response": "",
        "can_process": False
    }
    try:
        result = workflow.invoke(state)  # Synchronous call
        logger.info(f"Workflow completed with response: {result['response']}")
        if not result["response"]:
            logger.warning("Workflow returned empty response")
            result["response"] = (
                f"No results found for '{query.query}'. "
                "Please try a different query or provide more details."
            )
        return {"response": result["response"]}
    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}", exc_info=True)
        fallback_response = (
            f"An error occurred while processing the query '{query.query}': {str(e)}. "
            "Please try again or contact support."
        )
        return {"response": fallback_response}

# FastAPI endpoint for query gifting
@app.post("/gift")
async def handle_query(query: SmartSearchRequest):
    logger.info(f"Received query: {query.query}")
    
    workflow = create_gifting_workflow()
    state = {
        "query": query.query,
        "step1_product_ids": [],
        "step2_product_ids": [],
        "distinct_combined_product_ids": [],
        "wishlist_top5": [],
        "purchase_top5": [],
        "final_products": []
    }
    try:
        result = workflow.invoke(state)
        products = result["final_products"]
        return {"response": json.dumps(products, default=str)}  # Serialize to JSON string
    except Exception as e:
        logger.error(f"Error in gifting workflow: {str(e)}")
        fallback_response = (
            f"An error occurred while processing the gifting query '{query.query}': {str(e)}. "
            "Please try again or contact support."
        )
        return {"response": fallback_response}

# Root and health endpoints
@app.get("/")
async def root():
    return {"message": "eCommerce Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Product endpoints
@app.get("/products", response_model=List[Product])
async def get_products(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (p:Product)
        RETURN p.productId AS id, p.name AS name, p.price AS price, p.image AS imageUrl,
               CASE 
                   WHEN p.tags IS NOT NULL AND size(p.tags) > 0 
                   THEN reduce(s = head(p.tags), t IN tail(p.tags) | s + ', ' + t) 
                   ELSE 'uncategorized' 
               END AS category, p.description AS description,
               (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END) AS rating,
               (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END) AS discount,
               (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END) AS created_at,
               (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END) AS updated_at
        SKIP $skip LIMIT $limit
        """
        results = mcp.run_cypher_query(query, {"skip": skip, "limit": limit})
        logger.info(f"Raw query results: {results}")
        return [
            Product(
                id=result["id"],
                name=result["name"],
                price=result["price"],
                imageUrl=result["imageUrl"],
                category=result["category"],
                description=result["description"],
                rating=result["rating"],
                discount=result["discount"],
                created_at=datetime.fromtimestamp(result["created_at"] / 1000) if result["created_at"] else None,
                updated_at=datetime.fromtimestamp(result["updated_at"] / 1000) if result["updated_at"] else None
            )
            for result in results
        ]
    finally:
        mcp.close()

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (p:Product {productId: $product_id})
        RETURN p.productId AS id, p.name AS name, p.price AS price, p.image AS imageUrl,
               CASE 
                   WHEN p.tags IS NOT NULL AND size(p.tags) > 0 
                   THEN reduce(s = head(p.tags), t IN tail(p.tags) | s + ', ' + t) 
                   ELSE 'uncategorized' 
               END AS category, p.description AS description,
               (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END) AS rating,
               (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END) AS discount,
               (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END) AS created_at,
               (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END) AS updated_at
        """
        result = mcp.run_cypher_query(query, {"product_id": product_id})
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        r = result[0]
        return Product(
            id=r["id"],
            name=r["name"],
            price=r["price"],
            imageUrl=r["imageUrl"],
            category=r["category"],
            description=r["description"],
            rating=r["rating"],
            discount=r["discount"],
            created_at=datetime.fromtimestamp(r["created_at"] / 1000) if r["created_at"] else None,
            updated_at=datetime.fromtimestamp(r["updated_at"] / 1000) if r["updated_at"] else None
        )
    finally:
        mcp.close()

@app.get("/search", response_model=List[Product])
async def search_products(
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    keywords: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (p:Product)
        WHERE ($category IS NULL OR $category IN p.tags)
        AND ($brand IS NULL OR $brand IN p.tags)
        AND ($min_price IS NULL OR p.price >= $min_price)
        AND ($max_price IS NULL OR p.price <= $max_price)
        AND ($keywords_regex IS NULL OR p.name =~ $keywords_regex OR p.description =~ $keywords_regex)
        RETURN p.productId AS id, p.name AS name, p.price AS price, p.image AS imageUrl,
               CASE 
                   WHEN p.tags IS NOT NULL AND size(p.tags) > 0 
                   THEN reduce(s = head(p.tags), t IN tail(p.tags) | s + ', ' + t) 
                   ELSE 'uncategorized' 
               END AS category, p.description AS description,
               (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END) AS rating,
               (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END) AS discount,
               (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END) AS created_at,
               (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END) AS updated_at
        ORDER BY p.price ASC
        SKIP $skip LIMIT $limit
        """
        params = {
            "category": category,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "keywords_regex": f"(?i).*{keywords.replace(',', '|')}.*" if keywords else "(?i).*",
            "skip": skip,
            "limit": limit
        }
        results = mcp.run_cypher_query(query, params)
        logger.info(f"Raw query results: {results}")
        return [
            Product(
                id=result["id"],
                name=result["name"],
                price=result["price"],
                imageUrl=result["imageUrl"],
                category=result["category"],
                description=result["description"],
                rating=result["rating"],
                discount=result["discount"],
                created_at=datetime.fromtimestamp(result["created_at"] / 1000) if result["created_at"] else None,
                updated_at=datetime.fromtimestamp(result["updated_at"] / 1000) if result["updated_at"] else None
            )
            for result in results
        ]
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    finally:
        mcp.close()

# Wishlist endpoints
@app.get("/api/wishlist", response_model=List[Wishlist])
async def get_wishlist(user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist)
        OPTIONAL MATCH (w)-[r:CONTAINS]->(p:Product)
        RETURN w.wishlistId AS id, w.userId AS user_id, w.name AS name, w.note AS note,
               collect({
                   product_id: p.productId,
                   added_at: r.addedAt,
                   product_details: {
                       id: p.productId,
                       name: p.name,
                       price: p.price,
                       imageUrl: p.image,
                       category: (CASE WHEN 'giftingCategories' IN keys(p) AND p.giftingCategories IS NOT NULL AND size(p.giftingCategories) > 0 THEN p.giftingCategories[0] ELSE null END),
                       description: p.description,
                       rating: (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END),
                       discount: (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END),
                       created_at: (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END),
                       updated_at: (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END)
                   }
               }) AS products,
               w.createdAt AS created_at, w.updatedAt AS updated_at
        """
        results = mcp.run_cypher_query(query, {"user_id": user_id})
        wishlists = [
            Wishlist(
                id=result["id"],
                user_id=result["user_id"],
                name=result["name"],
                note=result["note"],
                products=[
                    WishlistItemWithDetails(
                        product_id=item["product_id"],
                        added_at=item["added_at"],
                        product_details=item["product_details"]
                    )
                    for item in result["products"] if item["product_id"] is not None
                ],
                item_count=len([item for item in result["products"] if item["product_id"] is not None]),
                created_at=result["created_at"],
                updated_at=result["updated_at"]
            )
            for result in results
        ]
        
        update_query = """
        MATCH (w:Wishlist {wishlistId: $wishlistId})
        OPTIONAL MATCH (w)-[:HAS_PRODUCT]->(p:Product)
        WITH w, COLLECT(p) AS products
        WITH w, products,
        [ p IN products WHERE p.giftingSymbolicValue IS NOT NULL | p.giftingSymbolicValue ] AS symbolicValues,
        REDUCE(allRel = [], p IN products | allRel + COALESCE(p.giftingRelationshipTypes, [])) AS allRelTypes,
        [ p IN products WHERE p.giftingAltruismSuitability IS NOT NULL | p.giftingAltruismSuitability ] AS altruismSuits,
        [ p IN products WHERE p.giftingReciprocityFit IS NOT NULL | p.giftingReciprocityFit ] AS reciprocityFits,
        [ p IN products WHERE p.giftingSelfGiftingSuitability IS NOT NULL | p.giftingSelfGiftingSuitability ] AS selfGiftingSuits
        WITH w, products, symbolicValues,
        [ type IN allRelTypes WHERE type IS NOT NULL | type ] AS relTypes,
        altruismSuits, reciprocityFits, selfGiftingSuits
        WITH w, products, symbolicValues, relTypes, altruismSuits, reciprocityFits, selfGiftingSuits,
        SIZE([p IN products | CASE WHEN p.giftingUtilitarianScore IS NOT NULL THEN 1 END]) AS nonNullUtil,
        SIZE([p IN products | CASE WHEN p.giftingNoveltyScore IS NOT NULL THEN 1 END]) AS nonNullNov,
        CASE WHEN SIZE(altruismSuits) > 0 THEN
        REDUCE(sumA = 0.0, s IN altruismSuits | sumA + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(altruismSuits)
        ELSE 0.0 END AS avgAltruism,
        CASE WHEN SIZE(reciprocityFits) > 0 THEN
        REDUCE(sumR = 0.0, s IN reciprocityFits | sumR + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(reciprocityFits)
        ELSE 0.0 END AS avgReciprocity,
        CASE WHEN SIZE(selfGiftingSuits) > 0 THEN
        REDUCE(sumS = 0.0, s IN selfGiftingSuits | sumS + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(selfGiftingSuits)
        ELSE 0.0 END AS avgSelfGifting
        WITH w, products, symbolicValues, relTypes, avgAltruism, avgReciprocity, avgSelfGifting,
        CASE WHEN nonNullUtil > 0 THEN
        REDUCE(sumU = 0.0, p IN products | sumU + COALESCE(p.giftingUtilitarianScore, 0.0)) / nonNullUtil
        ELSE null END AS avgUtilitarian,
        CASE WHEN nonNullNov > 0 THEN
        REDUCE(sumN = 0.0, p IN products | sumN + COALESCE(p.giftingNoveltyScore, 0.0)) / nonNullNov
        ELSE null END AS avgNovelty
        SET w.isHedonic = 
        CASE 
            WHEN COALESCE(avgUtilitarian, 0) < 0.5 OR 
                COALESCE(avgNovelty, 0) > 0.6 OR 
                'high' IN symbolicValues OR 
                'romantic' IN relTypes 
            THEN true 
            ELSE false 
        END,
        w.isAltruistic = 
        CASE 
            WHEN avgAltruism > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) < 0.5 AND 
                'high' IN symbolicValues AND 
                ('family' IN relTypes OR 'romantic' IN relTypes)) 
            THEN true 
            ELSE false 
        END,
        w.expectsReciprocity = 
        CASE 
            WHEN avgReciprocity > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) >= 0.3 AND 
                COALESCE(avgUtilitarian, 0) <= 0.7 AND 
                ('friend' IN relTypes OR 'colleague' IN relTypes)) 
            THEN true 
            ELSE false 
        END,
        w.isSurprising = 
        CASE 
            WHEN COALESCE(avgNovelty, 0) > 0.6 AND 
                ('romantic' IN relTypes OR 'family' IN relTypes) 
            THEN true 
            ELSE false 
        END,
        w.isSelfGifting = 
        CASE 
            WHEN avgSelfGifting > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) > 0.7 OR 
                'high' IN symbolicValues) 
            THEN true 
            ELSE false 
        END
        RETURN w.wishlistId
        """
        for wishlist in wishlists:
            mcp.run_cypher_query(update_query, {"wishlistId": wishlist.id})

        return wishlists
    finally:
        mcp.close()

@app.post("/api/wishlist", response_model=Wishlist)
async def create_wishlist(wishlist_data: WishlistCreate):
    mcp = MCPToolset(ConnectionParams())
    try:
        # Check if wishlist with same name exists for the user
        check_query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {name: $name})
        RETURN count(w) AS count
        """
        check_params = {
            "user_id": wishlist_data.user_id,
            "name": wishlist_data.name
        }
        check_result = mcp.run_cypher_query(check_query, check_params)
        if check_result[0]["count"] > 0:
            raise HTTPException(status_code=400, detail="Wishlist with the same name already exists")

        wishlist_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp() * 1000
        query = """
        MATCH (u:User {userId: $user_id})
        CREATE (w:Wishlist {
            wishlistId: $wishlist_id,
            userId: $user_id,
            name: $name,
            note: $note,
            preferredRelationshipTypes: $preferredRelationshipTypes,
            isHedonic: $isHedonic,
            isAltruistic: $isAltruistic,
            expectsReciprocity: $expectsReciprocity,
            isSurprising: $isSurprising,
            isSelfGifting: $isSelfGifting,
            createdAt: $timestamp,
            updatedAt: $timestamp
        })
        CREATE (u)-[:OWNS_WISHLIST {createdAt: $timestamp}]->(w)
        RETURN w.wishlistId AS id, w.userId AS user_id, w.name AS name, w.note AS note,
               w.createdAt AS created_at, w.updatedAt AS updated_at
        """
        params = {
            "user_id": wishlist_data.user_id,
            "wishlist_id": wishlist_id,
            "name": wishlist_data.name,
            "note": wishlist_data.note,
            "preferredRelationshipTypes": [],
            "isHedonic": False,
            "isAltruistic": False,
            "expectsReciprocity": False,
            "isSurprising": False,
            "isSelfGifting": False,
            "timestamp": timestamp
        }
        result = mcp.run_cypher_query(query, params)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create wishlist")
        r = result[0]
        return Wishlist(
            id=r["id"],
            user_id=r["user_id"],
            name=r["name"],
            note=r["note"],
            products=[],
            item_count=0,
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        )
    finally:
        mcp.close()

@app.put("/api/wishlist/{wishlist_id}", response_model=Wishlist)
async def update_wishlist(wishlist_id: str, update_data: WishlistUpdate, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        # Check if wishlist exists and belongs to user
        check_exists_query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {wishlistId: $wishlist_id})
        RETURN w
        """
        check_exists_params = {"user_id": user_id, "wishlist_id": wishlist_id}
        check_exists_result = mcp.run_cypher_query(check_exists_query, check_exists_params)
        if not check_exists_result:
            raise HTTPException(status_code=404, detail="Wishlist not found or not owned by user")

        # If name is being updated, check for uniqueness (excluding current wishlist)
        if update_data.name is not None:
            check_unique_query = """
            MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {name: $new_name})
            WHERE w.wishlistId <> $wishlist_id
            RETURN count(w) AS count
            """
            check_unique_params = {
                "user_id": user_id,
                "new_name": update_data.name,
                "wishlist_id": wishlist_id
            }
            check_unique_result = mcp.run_cypher_query(check_unique_query, check_unique_params)
            if check_unique_result[0]["count"] > 0:
                raise HTTPException(status_code=400, detail="Another wishlist with the same name already exists")

        timestamp = datetime.now().timestamp() * 1000
        update_query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {wishlistId: $wishlist_id})
        OPTIONAL MATCH (w)-[r:CONTAINS]->(p:Product)
        SET w.name = COALESCE($new_name, w.name),
            w.note = COALESCE($new_note, w.note),
            w.updatedAt = $timestamp
        RETURN w.wishlistId AS id, w.userId AS user_id, w.name AS name, w.note AS note, w.createdAt AS created_at, w.updatedAt AS updated_at
        """
        params = {
            "user_id": user_id,
            "wishlist_id": wishlist_id,
            "new_name": update_data.name,
            "new_note": update_data.note,
            "timestamp": timestamp
        }
        result = mcp.run_cypher_query(update_query, params)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update wishlist")
        r = result[0]
        return Wishlist(
            id=r["id"],
            user_id=r["user_id"],
            name=r["name"],
            note=r["note"],
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        )
    finally:
        mcp.close()

@app.get("/api/wishlist/{wishlist_id}", response_model=Wishlist)
async def get_wishlist_by_id(wishlist_id: str, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {wishlistId: $wishlist_id})
        OPTIONAL MATCH (w)-[r:CONTAINS]->(p:Product)
        RETURN w.wishlistId AS id, w.userId AS user_id, w.name AS name, w.note AS note,
               collect({
                   product_id: p.productId,
                   added_at: r.addedAt,
                   product_details: {
                       id: p.productId,
                       name: p.name,
                       price: p.price,
                       imageUrl: p.image,
                       category: (CASE WHEN 'giftingCategories' IN keys(p) AND p.giftingCategories IS NOT NULL AND size(p.giftingCategories) > 0 THEN p.giftingCategories[0] ELSE null END),
                       description: p.description,
                       rating: (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END),
                       discount: (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END),
                       created_at: (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END),
                       updated_at: (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END)
                   }
               }) AS products,
               w.createdAt AS created_at, w.updatedAt AS updated_at
        """
        result = mcp.run_cypher_query(query, {"user_id": user_id, "wishlist_id": wishlist_id})
        if not result:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        r = result[0]
        return Wishlist(
            id=r["id"],
            user_id=r["user_id"],
            name=r["name"],
            note=r["note"],
            products=[
                WishlistItemWithDetails(
                    product_id=item["product_id"],
                    added_at=item["added_at"],
                    product_details=item["product_details"]
                )
                for item in r["products"] if item["product_id"] is not None
            ],
            item_count=len([item for item in r["products"] if item["product_id"] is not None]),
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        )
    finally:
        mcp.close()

@app.post("/api/wishlist/{wishlist_id}/products", response_model=Wishlist)
async def add_product_to_wishlist(wishlist_id: str, product_data: WishlistAddProduct, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        timestamp = datetime.now().timestamp() * 1000
        query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {wishlistId: $wishlist_id})
        MATCH (p:Product {productId: $product_id})
        MERGE (w)-[r:CONTAINS]->(p)
        ON CREATE SET r.addedAt = $timestamp
        CREATE (u)-[:INTERACTED_WITH {timestamp: $timestamp}]->(e:InteractionEvent {
            eventId: $event_id,
            eventType: 'add_to_wishlist',
            timestamp: $timestamp,
            value: 1,
            expiresAt: $expires_at,
            noveltyRating: $noveltyRating,
            utilityRating: $utilityRating
        })-[:TARGETS]->(p)
        SET w.updatedAt = $timestamp
        RETURN w.wishlistId AS id, w.userId AS user_id, w.name AS name, w.note AS note,
               collect({
                   product_id: p.productId,
                   added_at: r.addedAt,
                   product_details: {
                       id: p.productId,
                       name: p.name,
                       price: p.price,
                       imageUrl: p.image,
                       category: (CASE WHEN 'giftingCategories' IN keys(p) AND p.giftingCategories IS NOT NULL AND size(p.giftingCategories) > 0 THEN p.giftingCategories[0] ELSE null END),
                       description: p.description,
                       rating: (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END),
                       discount: (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END),
                       created_at: (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END),
                       updated_at: (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END)
                   }
               }) AS products,
               w.createdAt AS created_at, w.updatedAt AS updated_at
        """
        params = {
            "user_id": user_id,
            "wishlist_id": wishlist_id,
            "product_id": product_data.product_id,
            "timestamp": timestamp,
            "event_id": str(uuid.uuid4()),
            "expires_at": timestamp + 30 * 24 * 60 * 60 * 1000,
            "noveltyRating": 0.0,
            "utilityRating": 0.0
        }
        result = mcp.run_cypher_query(query, params)
        if not result:
            raise HTTPException(status_code=404, detail="Wishlist or product not found")
        
        update_query = """
        MATCH (w:Wishlist {wishlistId: $wishlistId})
        OPTIONAL MATCH (w)-[:HAS_PRODUCT]->(p:Product)
        WITH w, COLLECT(p) AS products
        WITH w, products,
        [ p IN products WHERE p.giftingSymbolicValue IS NOT NULL | p.giftingSymbolicValue ] AS symbolicValues,
        REDUCE(allRel = [], p IN products | allRel + COALESCE(p.giftingRelationshipTypes, [])) AS allRelTypes,
        [ p IN products WHERE p.giftingAltruismSuitability IS NOT NULL | p.giftingAltruismSuitability ] AS altruismSuits,
        [ p IN products WHERE p.giftingReciprocityFit IS NOT NULL | p.giftingReciprocityFit ] AS reciprocityFits,
        [ p IN products WHERE p.giftingSelfGiftingSuitability IS NOT NULL | p.giftingSelfGiftingSuitability ] AS selfGiftingSuits
        WITH w, products, symbolicValues,
        [ type IN allRelTypes WHERE type IS NOT NULL | type ] AS relTypes,
        altruismSuits, reciprocityFits, selfGiftingSuits
        WITH w, products, symbolicValues, relTypes, altruismSuits, reciprocityFits, selfGiftingSuits,
        SIZE([p IN products | CASE WHEN p.giftingUtilitarianScore IS NOT NULL THEN 1 END]) AS nonNullUtil,
        SIZE([p IN products | CASE WHEN p.giftingNoveltyScore IS NOT NULL THEN 1 END]) AS nonNullNov,
        CASE WHEN SIZE(altruismSuits) > 0 THEN
        REDUCE(sumA = 0.0, s IN altruismSuits | sumA + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(altruismSuits)
        ELSE 0.0 END AS avgAltruism,
        CASE WHEN SIZE(reciprocityFits) > 0 THEN
        REDUCE(sumR = 0.0, s IN reciprocityFits | sumR + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(reciprocityFits)
        ELSE 0.0 END AS avgReciprocity,
        CASE WHEN SIZE(selfGiftingSuits) > 0 THEN
        REDUCE(sumS = 0.0, s IN selfGiftingSuits | sumS + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(selfGiftingSuits)
        ELSE 0.0 END AS avgSelfGifting
        WITH w, products, symbolicValues, relTypes, avgAltruism, avgReciprocity, avgSelfGifting,
        CASE WHEN nonNullUtil > 0 THEN
        REDUCE(sumU = 0.0, p IN products | sumU + COALESCE(p.giftingUtilitarianScore, 0.0)) / nonNullUtil
        ELSE null END AS avgUtilitarian,
        CASE WHEN nonNullNov > 0 THEN
        REDUCE(sumN = 0.0, p IN products | sumN + COALESCE(p.giftingNoveltyScore, 0.0)) / nonNullNov
        ELSE null END AS avgNovelty
        SET w.isHedonic = 
        CASE 
            WHEN COALESCE(avgUtilitarian, 0) < 0.5 OR 
                COALESCE(avgNovelty, 0) > 0.6 OR 
                'high' IN symbolicValues OR 
                'romantic' IN relTypes 
            THEN true 
            ELSE false 
        END,
        w.isAltruistic = 
        CASE 
            WHEN avgAltruism > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) < 0.5 AND 
                'high' IN symbolicValues AND 
                ('family' IN relTypes OR 'romantic' IN relTypes)) 
            THEN true 
            ELSE false 
        END,
        w.expectsReciprocity = 
        CASE 
            WHEN avgReciprocity > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) >= 0.3 AND 
                COALESCE(avgUtilitarian, 0) <= 0.7 AND 
                ('friend' IN relTypes OR 'colleague' IN relTypes)) 
            THEN true 
            ELSE false 
        END,
        w.isSurprising = 
        CASE 
            WHEN COALESCE(avgNovelty, 0) > 0.6 AND 
                ('romantic' IN relTypes OR 'family' IN relTypes) 
            THEN true 
            ELSE false 
        END,
        w.isSelfGifting = 
        CASE 
            WHEN avgSelfGifting > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) > 0.7 OR 
                'high' IN symbolicValues) 
            THEN true 
            ELSE false 
        END
        RETURN w.wishlistId
        """
        mcp.run_cypher_query(update_query, {"wishlistId": wishlist_id})

        r = result[0]
        return Wishlist(
            id=r["id"],
            user_id=r["user_id"],
            name=r["name"],
            note=r["note"],
            products=[
                WishlistItemWithDetails(
                    product_id=item["product_id"],
                    added_at=item["added_at"],
                    product_details=item["product_details"]
                )
                for item in r["products"] if item["product_id"] is not None
            ],
            item_count=len([item for item in r["products"] if item["product_id"] is not None]),
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        )
    finally:
        mcp.close()

@app.delete("/api/wishlist/{wishlist_id}/products/{product_id}", response_model=Wishlist)
async def remove_product_from_wishlist(wishlist_id: str, product_id: int, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        timestamp = datetime.now().timestamp() * 1000
        query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {wishlistId: $wishlist_id})
        MATCH (w)-[r:CONTAINS]->(p:Product {productId: $product_id})
        DELETE r
        SET w.updatedAt = $timestamp
        WITH w
        OPTIONAL MATCH (w)-[r2:CONTAINS]->(p2:Product)
        RETURN w.wishlistId AS id, w.userId AS user_id, w.name AS name, w.note AS note,
               collect({
                   product_id: p2.productId,
                   added_at: r2.addedAt,
                   product_details: {
                       id: p2.productId,
                       name: p2.name,
                       price: p2.price,
                       imageUrl: p2.image,
                       category: (CASE WHEN 'giftingCategories' IN keys(p2) AND p2.giftingCategories IS NOT NULL AND size(p2.giftingCategories) > 0 THEN p2.giftingCategories[0] ELSE null END),
                       description: p2.description,
                       rating: (CASE WHEN 'rating' IN keys(p2) THEN p2.rating ELSE null END),
                       discount: (CASE WHEN 'discount' IN keys(p2) THEN p2.discount ELSE null END),
                       created_at: (CASE WHEN 'created_at' IN keys(p2) THEN p2.created_at ELSE null END),
                       updated_at: (CASE WHEN 'updated_at' IN keys(p2) THEN p2.updated_at ELSE null END)
                   }
               }) AS products,
               w.createdAt AS created_at, w.updatedAt AS updated_at
        """
        result = mcp.run_cypher_query(query, {"user_id": user_id, "wishlist_id": wishlist_id, "product_id": product_id, "timestamp": timestamp})
        if not result:
            raise HTTPException(status_code=404, detail="Wishlist or product not found")
        
        update_query = """
        MATCH (w:Wishlist {wishlistId: $wishlistId})
        OPTIONAL MATCH (w)-[:HAS_PRODUCT]->(p:Product)
        WITH w, COLLECT(p) AS products
        WITH w, products,
        [ p IN products WHERE p.giftingSymbolicValue IS NOT NULL | p.giftingSymbolicValue ] AS symbolicValues,
        REDUCE(allRel = [], p IN products | allRel + COALESCE(p.giftingRelationshipTypes, [])) AS allRelTypes,
        [ p IN products WHERE p.giftingAltruismSuitability IS NOT NULL | p.giftingAltruismSuitability ] AS altruismSuits,
        [ p IN products WHERE p.giftingReciprocityFit IS NOT NULL | p.giftingReciprocityFit ] AS reciprocityFits,
        [ p IN products WHERE p.giftingSelfGiftingSuitability IS NOT NULL | p.giftingSelfGiftingSuitability ] AS selfGiftingSuits
        WITH w, products, symbolicValues,
        [ type IN allRelTypes WHERE type IS NOT NULL | type ] AS relTypes,
        altruismSuits, reciprocityFits, selfGiftingSuits
        WITH w, products, symbolicValues, relTypes, altruismSuits, reciprocityFits, selfGiftingSuits,
        SIZE([p IN products | CASE WHEN p.giftingUtilitarianScore IS NOT NULL THEN 1 END]) AS nonNullUtil,
        SIZE([p IN products | CASE WHEN p.giftingNoveltyScore IS NOT NULL THEN 1 END]) AS nonNullNov,
        CASE WHEN SIZE(altruismSuits) > 0 THEN
        REDUCE(sumA = 0.0, s IN altruismSuits | sumA + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(altruismSuits)
        ELSE 0.0 END AS avgAltruism,
        CASE WHEN SIZE(reciprocityFits) > 0 THEN
        REDUCE(sumR = 0.0, s IN reciprocityFits | sumR + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(reciprocityFits)
        ELSE 0.0 END AS avgReciprocity,
        CASE WHEN SIZE(selfGiftingSuits) > 0 THEN
        REDUCE(sumS = 0.0, s IN selfGiftingSuits | sumS + CASE s WHEN 'high' THEN 1.0 WHEN 'medium' THEN 0.5 ELSE 0.0 END) / SIZE(selfGiftingSuits)
        ELSE 0.0 END AS avgSelfGifting
        WITH w, products, symbolicValues, relTypes, avgAltruism, avgReciprocity, avgSelfGifting,
        CASE WHEN nonNullUtil > 0 THEN
        REDUCE(sumU = 0.0, p IN products | sumU + COALESCE(p.giftingUtilitarianScore, 0.0)) / nonNullUtil
        ELSE null END AS avgUtilitarian,
        CASE WHEN nonNullNov > 0 THEN
        REDUCE(sumN = 0.0, p IN products | sumN + COALESCE(p.giftingNoveltyScore, 0.0)) / nonNullNov
        ELSE null END AS avgNovelty
        SET w.isHedonic = 
        CASE 
            WHEN COALESCE(avgUtilitarian, 0) < 0.5 OR 
                COALESCE(avgNovelty, 0) > 0.6 OR 
                'high' IN symbolicValues OR 
                'romantic' IN relTypes 
            THEN true 
            ELSE false 
        END,
        w.isAltruistic = 
        CASE 
            WHEN avgAltruism > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) < 0.5 AND 
                'high' IN symbolicValues AND 
                ('family' IN relTypes OR 'romantic' IN relTypes)) 
            THEN true 
            ELSE false 
        END,
        w.expectsReciprocity = 
        CASE 
            WHEN avgReciprocity > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) >= 0.3 AND 
                COALESCE(avgUtilitarian, 0) <= 0.7 AND 
                ('friend' IN relTypes OR 'colleague' IN relTypes)) 
            THEN true 
            ELSE false 
        END,
        w.isSurprising = 
        CASE 
            WHEN COALESCE(avgNovelty, 0) > 0.6 AND 
                ('romantic' IN relTypes OR 'family' IN relTypes) 
            THEN true 
            ELSE false 
        END,
        w.isSelfGifting = 
        CASE 
            WHEN avgSelfGifting > 0.5 OR 
                (COALESCE(avgUtilitarian, 0) > 0.7 OR 
                'high' IN symbolicValues) 
            THEN true 
            ELSE false 
        END
        RETURN w.wishlistId
        """
        mcp.run_cypher_query(update_query, {"wishlistId": wishlist_id})

        r = result[0]
        return Wishlist(
            id=r["id"],
            user_id=r["user_id"],
            name=r["name"],
            note=r["note"],
            products=[
                WishlistItemWithDetails(
                    product_id=item["product_id"],
                    added_at=item["added_at"],
                    product_details=item["product_details"]
                )
                for item in r["products"] if item["product_id"] is not None
            ],
            item_count=len([item for item in r["products"] if item["product_id"] is not None]),
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        )
    finally:
        mcp.close()

@app.delete("/api/wishlist/{wishlist_id}")
async def delete_wishlist(wishlist_id: str, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (u:User {userId: $user_id})-[:OWNS_WISHLIST]->(w:Wishlist {wishlistId: $wishlist_id})
        DETACH DELETE w
        RETURN count(w) AS deleted
        """
        result = mcp.run_cypher_query(query, {"user_id": user_id, "wishlist_id": wishlist_id})
        if result[0]["deleted"] == 0:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        return {"success": True, "message": "Wishlist deleted successfully"}
    finally:
        mcp.close()

# Cart endpoints
@app.get("/api/cart", response_model=Cart)
async def get_cart(user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (u:User {userId: $user_id})-[:HAS_CART]->(c:Cart)
        OPTIONAL MATCH (c)-[r:CONTAINS]->(p:Product)
        RETURN c.cartId AS id, c.userId AS user_id,
               collect({
                   product_id: p.productId,
                   quantity: r.quantity,
                   added_at: r.addedAt,
                   product_details: {
                       id: p.productId,
                       name: p.name,
                       price: p.price,
                       imageUrl: p.image,
                       category: (CASE WHEN 'giftingCategories' IN keys(p) AND p.giftingCategories IS NOT NULL AND size(p.giftingCategories) > 0 THEN p.giftingCategories[0] ELSE null END),
                       description: p.description,
                       rating: (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END),
                       discount: (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END),
                       created_at: (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END),
                       updated_at: (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END)
                   }
               }) AS items
        """
        result = mcp.run_cypher_query(query, {"user_id": user_id})
        if not result:
            cart_id = f"cart-{user_id}"
            timestamp = datetime.now().timestamp() * 1000
            create_query = """
            MATCH (u:User {userId: $user_id})
            CREATE (c:Cart {cartId: $cart_id, userId: $user_id})
            CREATE (u)-[:HAS_CART {createdAt: $timestamp, updatedAt: $timestamp}]->(c)
            RETURN c.cartId AS id, c.userId AS user_id, [] AS items
            """
            result = mcp.run_cypher_query(create_query, {
                "user_id": user_id,
                "cart_id": cart_id,
                "timestamp": timestamp
            })
        
        cart = result[0]
        items = [
            CartItem(
                product_id=item["product_id"],
                quantity=item["quantity"],
                added_at=item["added_at"],
                product_details=item["product_details"]
            )
            for item in cart["items"] if item["product_id"] is not None
        ]
        total_amount = sum(
            item.quantity * (item.product_details.get("price", 0.0) or 0.0)
            for item in items
        )
        return Cart(
            id=cart["id"],
            user_id=cart["user_id"],
            items=items,
            item_count=len(items),
            total_amount=total_amount,
            created_at=0.0,
            updated_at=0.0
        )
    finally:
        mcp.close()

@app.post("/api/cart/add", response_model=Cart)
async def add_item_to_cart(cart_item: CartAddItem, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        cart_id = f"cart-{user_id}"
        timestamp = datetime.now().timestamp() * 1000
        expires_at = timestamp + 30 * 24 * 60 * 60 * 1000
        event_id = str(uuid.uuid4())

        query = """
        MERGE (u:User {userId: $user_id})
        MERGE (u)-[:HAS_CART {createdAt: $timestamp, updatedAt: $timestamp}]->(c:Cart {cartId: $cart_id, userId: $user_id})
        WITH u, c
        MATCH (p:Product {productId: $product_id})
        MERGE (c)-[r:CONTAINS]->(p)
        ON CREATE SET r.quantity = $quantity, r.addedAt = $timestamp
        ON MATCH SET r.quantity = r.quantity + $quantity, r.addedAt = $timestamp
        CREATE (u)-[:INTERACTED_WITH {timestamp: $timestamp}]->(e:InteractionEvent {
            eventId: $event_id,
            eventType: 'add_to_cart',
            timestamp: $timestamp,
            value: $quantity,
            expiresAt: $expires_at,
            noveltyRating: $noveltyRating,
            utilityRating: $utilityRating
        })-[:TARGETS]->(p)
        RETURN c.cartId AS id, c.userId AS user_id,
            collect({
                product_id: p.productId,
                quantity: r.quantity,
                added_at: r.addedAt,
                product_details: {
                    id: p.productId,
                    name: p.name,
                    price: p.price,
                    imageUrl: p.image,
                    category: (CASE WHEN 'giftingCategories' IN keys(p) AND p.giftingCategories IS NOT NULL AND size(p.giftingCategories) > 0 THEN p.giftingCategories[0] ELSE null END),
                    description: p.description,
                    rating: (CASE WHEN 'rating' IN keys(p) THEN p.rating ELSE null END),
                    discount: (CASE WHEN 'discount' IN keys(p) THEN p.discount ELSE null END),
                    created_at: (CASE WHEN 'created_at' IN keys(p) THEN p.created_at ELSE null END),
                    updated_at: (CASE WHEN 'updated_at' IN keys(p) THEN p.updated_at ELSE null END)
                }
            }) AS items
        """
        result = mcp.run_cypher_query(query, {
            "user_id": user_id,
            "cart_id": cart_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "timestamp": timestamp,
            "expires_at": expires_at,
            "event_id": event_id,
            "noveltyRating": 0.0,
            "utilityRating": 0.0
        })
        if not result:
            raise HTTPException(status_code=404, detail="User or product not found")
        
        cart = result[0]
        items = [
            CartItem(
                product_id=item["product_id"],
                quantity=item["quantity"],
                added_at=item["added_at"],
                product_details=item["product_details"]
            )
            for item in cart["items"] if item["product_id"] is not None
        ]
        total_amount = sum(
            item.quantity * (item.product_details.get("price", 0.0) or 0.0)
            for item in items
        )
        return Cart(
            id=cart["id"],
            user_id=cart["user_id"],
            items=items,
            item_count=len(items),
            total_amount=total_amount,
            created_at=0.0,
            updated_at=0.0
        )
    finally:
        mcp.close()

@app.put("/api/cart/update", response_model=Cart)
async def update_item_in_cart(cart_item: CartUpdateItem, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        cart_id = f"cart-{user_id}"
        timestamp = datetime.now().timestamp() * 1000
        expires_at = timestamp + 30 * 24 * 60 * 60 * 1000
        event_id = str(uuid.uuid4())

        query = """
        MATCH (u:User {userId: $user_id})-[:HAS_CART]->(c:Cart {cartId: $cart_id})
        OPTIONAL MATCH (c)-[r:CONTAINS]->(p:Product {productId: $product_id})
        WITH u, c, r, p
        WHERE r IS NOT NULL AND p IS NOT NULL
        SET r.quantity = $quantity, r.addedAt = $timestamp
        SET c.updatedAt = $timestamp
        CREATE (u)-[:INTERACTED_WITH {timestamp: $timestamp}]->(e:InteractionEvent {
            eventId: $event_id,
            eventType: 'update_cart',
            timestamp: $timestamp,
            value: $quantity,
            expiresAt: $expires_at,
            noveltyRating: $noveltyRating,
            utilityRating: $utilityRating
        })-[:TARGETS]->(p)
        WITH c
        OPTIONAL MATCH (c)-[r2:CONTAINS]->(p2:Product)
        RETURN c.cartId AS id, c.userId AS user_id, c.createdAt AS created_at, c.updatedAt AS updated_at,
               collect({
                   product_id: p2.productId,
                   quantity: r2.quantity,
                   added_at: r2.added_at,
                   product_details: {
                       id: p2.productId,
                       name: p2.name,
                       price: p2.price,
                       imageUrl: p2.image,
                       category: (CASE WHEN 'giftingCategories' IN keys(p2) AND p2.giftingCategories IS NOT NULL AND size(p2.giftingCategories) > 0 THEN p2.giftingCategories[0] ELSE null END),
                       description: p2.description,
                       rating: (CASE WHEN 'rating' IN keys(p2) THEN p2.rating ELSE null END),
                       discount: (CASE WHEN 'discount' IN keys(p2) THEN p2.discount ELSE null END),
                       created_at: (CASE WHEN 'created_at' IN keys(p2) THEN p2.created_at ELSE null END),
                       updated_at: (CASE WHEN 'updated_at' IN keys(p2) THEN p2.updated_at ELSE null END)
                   }
               }) AS items
        """
        result = mcp.run_cypher_query(query, {
            "user_id": user_id,
            "cart_id": cart_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "timestamp": timestamp,
            "expires_at": expires_at,
            "event_id": event_id,
            "noveltyRating": 0.0,
            "utilityRating": 0.0
        })
        if not result:
            raise HTTPException(status_code=404, detail="Cart or product not found in cart")
        
        cart = result[0]
        items = [
            CartItem(
                product_id=item["product_id"],
                quantity=item["quantity"],
                added_at=item["added_at"],
                product_details=item["product_details"]
            )
            for item in cart["items"] if item["product_id"] is not None
        ]
        total_amount = sum(
            item.quantity * (item.product_details.get("price", 0.0) or 0.0)
            for item in items
        )
        return Cart(
            id=cart["id"],
            user_id=cart["user_id"],
            items=items,
            item_count=len(items),
            total_amount=total_amount,
            created_at=cart["created_at"] or 0.0,
            updated_at=cart["updated_at"] or 0.0
        )
    finally:
        mcp.close()

@app.delete("/api/cart/remove", response_model=Cart)
async def remove_item_from_cart(cart_item: CartRemoveItem, user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        cart_id = f"cart-{user_id}"
        timestamp = datetime.now().timestamp() * 1000
        query = """
        MATCH (u:User {userId: $user_id})-[:HAS_CART]->(c:Cart {cartId: $cart_id})
        OPTIONAL MATCH (c)-[r:CONTAINS]->(p:Product {productId: $product_id})
        WITH u, c, r, p
        WHERE r IS NOT NULL AND p IS NOT NULL
        DELETE r
        SET c.updatedAt = $timestamp
        CREATE (u)-[:INTERACTED_WITH {timestamp: $timestamp}]->(e:InteractionEvent {
            eventId: $event_id,
            eventType: 'remove_from_cart',
            timestamp: $timestamp,
            value: 0,
            expiresAt: $expires_at,
            noveltyRating: $noveltyRating,
            utilityRating: $utilityRating
        })-[:TARGETS]->(p)
        WITH c
        OPTIONAL MATCH (c)-[r2:CONTAINS]->(p2:Product)
        RETURN c.cartId AS id, c.userId AS user_id, c.createdAt AS created_at, c.updatedAt AS updated_at,
            collect({
                product_id: p2.productId,
                quantity: r2.quantity,
                added_at: r2.added_at,
                product_details: {
                    id: p2.productId,
                    name: p2.name,
                    price: p2.price,
                    imageUrl: p2.image,
                    category: (CASE WHEN 'giftingCategories' IN keys(p2) AND p2.giftingCategories IS NOT NULL AND size(p2.giftingCategories) > 0 THEN p2.giftingCategories[0] ELSE null END),
                    description: p2.description,
                    rating: (CASE WHEN 'rating' IN keys(p2) THEN p2.rating ELSE null END),
                    discount: (CASE WHEN 'discount' IN keys(p2) THEN p2.discount ELSE null END),
                    created_at: (CASE WHEN 'created_at' IN keys(p2) THEN p2.created_at ELSE null END),
                    updated_at: (CASE WHEN 'updated_at' IN keys(p2) THEN p2.updated_at ELSE null END)
                }
            }) AS items
        """
        result = mcp.run_cypher_query(query, {
            "user_id": user_id,
            "cart_id": cart_id,
            "product_id": cart_item.product_id,
            "timestamp": timestamp,
            "expires_at": timestamp + 30 * 24 * 60 * 60 * 1000,
            "event_id": str(uuid.uuid4()),
            "noveltyRating": 0.0,
            "utilityRating": 0.0
        })
        if not result:
            raise HTTPException(status_code=404, detail="Cart or product not found")
        
        cart = result[0]
        items = [
            CartItem(
                product_id=item["product_id"],
                quantity=item["quantity"],
                added_at=item["added_at"],
                product_details=item["product_details"]
            )
            for item in cart["items"] if item["product_id"] is not None
        ]
        total_amount = sum(
            item.quantity * (item.product_details.get("price", 0.0) or 0.0)
            for item in items
        )
        return Cart(
            id=cart["id"],
            user_id=cart["user_id"],
            items=items,
            item_count=len(items),
            total_amount=total_amount,
            created_at=0.0,
            updated_at=0.0
        )
    finally:
        mcp.close()

@app.delete("/api/cart/clear", response_model=Cart)
async def clear_cart(user_id: str = Query(...)):
    mcp = MCPToolset(ConnectionParams())
    try:
        cart_id = f"cart-{user_id}"
        timestamp = datetime.now().timestamp() * 1000
        query = """
        MATCH (u:User {userId: $user_id})-[:HAS_CART]->(c:Cart {cartId: $cart_id})
        OPTIONAL MATCH (c)-[r:CONTAINS]->(p:Product)
        DELETE r
        CREATE (u)-[:INTERACTED_WITH {timestamp: $timestamp}]->(e:InteractionEvent {
            eventId: $event_id,
            eventType: 'clear_cart',
            timestamp: $timestamp,
            value: 0,
            expiresAt: $expires_at,
            noveltyRating: $noveltyRating,
            utilityRating: $utilityRating
        })
        RETURN c.cartId AS id, c.userId AS user_id, [] AS items
        """
        result = mcp.run_cypher_query(query, {
            "user_id": user_id,
            "cart_id": cart_id,
            "timestamp": timestamp,
            "expires_at": timestamp + 30 * 24 * 60 * 60 * 1000,
            "event_id": str(uuid.uuid4()),
            "noveltyRating": 0.0,
            "utilityRating": 0.0
        })
        if not result:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        cart = result[0]
        return Cart(
            id=cart["id"],
            user_id=cart["user_id"],
            items=[],
            item_count=0,
            total_amount=0.0,
            created_at=0.0,
            updated_at=0.0
        )
    finally:
        mcp.close()

@app.post("/api/events")
async def track_user_event(event: UserEventCreate):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (u:User {userId: $user_id})
        MATCH (p:Product {productId: $product_id})
        CREATE (u)-[:INTERACTED_WITH {timestamp: $timestamp}]->(e:InteractionEvent {
            eventId: $event_id,
            eventType: $event_type,
            timestamp: $timestamp,
            value: $value,
            expiresAt: $expires_at,
            noveltyRating: $noveltyRating,
            utilityRating: $utilityRating
        })-[:TARGETS]->(p)
        RETURN e
        """
        params = {
            "user_id": event.user_id,
            "product_id": int(event.product_id),  # Convert string to int for Neo4j
            "event_id": str(uuid.uuid4()),
            "event_type": event.event_type.value,
            "timestamp": datetime.now().timestamp() * 1000,
            "value": 1,
            "expires_at": datetime.now().timestamp() * 1000 + 30 * 24 * 60 * 60 * 1000,
            "noveltyRating": event.metadata.get("noveltyRating", 0.0) if event.metadata else 0.0,
            "utilityRating": event.metadata.get("utilityRating", 0.0) if event.metadata else 0.0
        }
        result = mcp.run_cypher_query(query, params)
        if not result:
            raise HTTPException(status_code=404, detail="User or product not found")
        
        update_user_query = """
        MATCH (u:User {userId: $user_id})-[:INTERACTED_WITH]->(e:InteractionEvent)-[:TARGETS]->(p:Product)
        WHERE e.eventType IN ['view', 'purchase'] AND e.timestamp > $timestamp_threshold
        WITH u, AVG(CASE WHEN p.giftingUtilitarianScore < 0.5 THEN 1.0 ELSE 0.0 END) AS hedonicRatio,
             AVG(CASE WHEN p.giftingNoveltyScore > 0.6 THEN 1.0 ELSE 0.0 END) AS surpriseRatio,
             AVG(CASE WHEN p.giftingAltruismSuitability = 'high' THEN 1.0 ELSE 0.0 END) AS altruismRatio
        SET u.hedonicBias = hedonicRatio,
            u.surprisePreference = surpriseRatio,
            u.altruismLevel = altruismRatio
        MATCH (u)-[:INTERACTED_WITH]->(e2:InteractionEvent {eventType: 'reciprocity_response'})
        WHERE e2.timestamp > $timestamp_threshold
        WITH u, COUNT(e2) AS reciprocityCount
        SET u.reciprocityExpectation = CASE WHEN reciprocityCount > 0 THEN reciprocityCount / 10.0 ELSE 0.0 END
        RETURN u
        """
        mcp.run_cypher_query(update_user_query, {
            "user_id": event.user_id,
            "timestamp_threshold": (datetime.now().timestamp() * 1000) - (6 * 30 * 24 * 60 * 60 * 1000)
        })

        update_product_query = """
        MATCH (p:Product {productId: $product_id})<-[:TARGETS]-(e:InteractionEvent {eventType: 'purchase'})
        WHERE e.timestamp > $timestamp_threshold
        WITH p, 
             AVG(CASE WHEN e.noveltyRating IS NOT NULL THEN toFloat(e.noveltyRating) ELSE 0.0 END) AS avgNoveltyRating,
             AVG(CASE WHEN e.utilityRating IS NOT NULL THEN toFloat(e.utilityRating) ELSE 0.0 END) AS avgUtilityRating,
             COUNT(e) AS recentCount
        WHERE recentCount > 10
        SET p.giftingUtilitarianScore = CASE WHEN avgUtilityRating IS NOT NULL THEN avgUtilityRating / 5 ELSE p.giftingUtilitarianScore END,
            p.giftingNoveltyScore = CASE WHEN avgNoveltyRating IS NOT NULL THEN avgNoveltyRating / 5 ELSE p.giftingNoveltyScore END
        MATCH (p)<-[:TARGETS]-(e2:InteractionEvent {eventType: 'purchase'})<-[:INTERACTED_WITH]-(u:User)-[r:HAS_RELATIONSHIP]->(u2:User)
        WHERE e2.timestamp > $timestamp_threshold
        WITH p, COLLECT(DISTINCT r.type) AS relTypes
        SET p.giftingRelationshipTypes = CASE WHEN SIZE(relTypes) > 0 THEN relTypes ELSE ['generic'] END
        RETURN p
        """
        mcp.run_cypher_query(update_product_query, {
            "product_id": int(event.product_id),
            "timestamp_threshold": (datetime.now().timestamp() * 1000) - (6 * 30 * 24 * 60 * 60 * 1000)
        })

        return {"status": "success", "message": "Event tracked successfully"}
    finally:
        mcp.close()

@app.get("/api/users/{user_id}/events")
async def get_user_events(user_id: str, days_back: int = Query(30, ge=1, le=90)):
    mcp = MCPToolset(ConnectionParams())
    try:
        query = """
        MATCH (u:User {userId: $user_id})-[:INTERACTED_WITH]->(e:InteractionEvent)-[:TARGETS]->(p:Product)
        WHERE e.timestamp > $timestamp_threshold
        RETURN e.eventId AS event_id, e.eventType AS event_type, e.timestamp AS timestamp,
               e.value AS value, e.noveltyRating AS noveltyRating, e.utilityRating AS utilityRating,
               p.productId AS product_id
        """
        result = mcp.run_cypher_query(query, {
            "user_id": user_id,
            "timestamp_threshold": (datetime.now().timestamp() * 1000) - (days_back * 24 * 60 * 60 * 1000)
        })
        return {
            "events": [
                {
                    "event_id": r["event_id"],
                    "event_type": r["event_type"],
                    "timestamp": datetime.fromtimestamp(r["timestamp"] / 1000) if r["timestamp"] else None,
                    "value": r["value"],
                    "metadata": {"noveltyRating": r["noveltyRating"], "utilityRating": r["utilityRating"]},
                    "product_id": str(r["product_id"])  # Convert int to str for model
                }
                for r in result
            ],
            "user_id": user_id,
            "count": len(result),
            "days_analyzed": days_back
        }
    finally:
        mcp.close()

@app.post("/get-recommendations")
async def get_recommendations(request: AlgoRecommendationRequest):
    mcp = MCPToolset(ConnectionParams())
    try:
        logger.info(f"Running recommendation query for user_id: {request.user_id}, product_ids: {request.product_ids}")
        query = """
        WITH $product_ids AS input_products, $user_id AS user_id
        // Item-to-Item Collaborative Filtering (handle empty product_ids)
        WITH input_products, user_id,
             CASE WHEN size(input_products) = 0 THEN []
             ELSE [(p1:Product)-[r:SIMILAR_TO]->(p2:Product)
                   WHERE p1.productId IN input_products AND NOT p2.productId IN input_products
                   | {productId: p2.productId, name: p2.name, score: r.score}]
             END AS item_to_item_results
        // ALS Recommendations (if user_id provided)
        WITH item_to_item_results, user_id,
             CASE WHEN user_id IS NOT NULL THEN
               [(u:User {userId: user_id})-[r:RECOMMENDED_BY_ALS]->(p:Product) | 
                {productId: p.productId, name: p.name, score: r.score}] 
             ELSE [] END AS als_results
        // PageRank Recommendations (if user_id provided)
        WITH item_to_item_results, als_results, user_id,
             CASE WHEN user_id IS NOT NULL THEN
               [(u:User {userId: user_id})-[r:RECOMMENDED_BY_PAGERANK]->(p:Product) | 
                {productId: p.productId, name: p.name, score: r.score}] 
             ELSE [] END AS pagerank_results
        // Aggregate and sort Item-to-Item results, limiting to top 5 distinct products
        UNWIND CASE WHEN size(item_to_item_results) = 0 THEN [{}] ELSE item_to_item_results END AS item
        WITH item.productId AS productId, item.name AS name, 
             max(item.score) AS max_score,
             als_results, pagerank_results
        WHERE productId IS NOT NULL
        ORDER BY max_score DESC
        WITH collect({productId: productId, name: name, score: max_score})[0..5] AS top_item_to_item,
             als_results, pagerank_results
        // Sort and limit ALS results (if any) by score DESC, top 5
        UNWIND (CASE WHEN size(als_results) = 0 THEN [null] ELSE als_results END) AS als_item
        WITH top_item_to_item, pagerank_results, als_item
        ORDER BY als_item.score DESC
        LIMIT 5
        WITH top_item_to_item, pagerank_results, 
             [x IN collect(als_item) WHERE x IS NOT NULL] AS top_als
        // Sort and limit PageRank results (if any) by score DESC, top 5
        UNWIND (CASE WHEN size(pagerank_results) = 0 THEN [null] ELSE pagerank_results END) AS pr_item
        WITH top_item_to_item, top_als, pr_item
        ORDER BY pr_item.score DESC
        LIMIT 5
        WITH top_item_to_item, top_als, 
             [x IN collect(pr_item) WHERE x IS NOT NULL] AS top_pagerank
        RETURN {
          item_to_item: top_item_to_item,
          als: top_als,
          pagerank: top_pagerank
        } AS recommendations
        """
        result = mcp.run_cypher_query(query, {
            "product_ids": request.product_ids,
            "user_id": request.user_id
        })
        logger.info(f"Recommendation query returned {len(result)} results")
        if not result:
            raise HTTPException(status_code=404, detail="No recommendations found")
        return result[0]["recommendations"]
    except Exception as e:
        logger.error(f"Error fetching recommendations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

# Close Neo4j driver on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
    mcp = MCPToolset(ConnectionParams())
    mcp.close()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8003)