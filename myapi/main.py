import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Get configuration from environment variables
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:example@localhost:27017/")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

# MongoDB connection
mongo_client = AsyncIOMotorClient(MONGODB_URL)
mongo_db = mongo_client.testdb
mongo_collection = mongo_db.test_collection

# Elasticsearch connection
es_client = AsyncElasticsearch([ELASTICSEARCH_URL])

# Data models
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class SearchQuery(BaseModel):
    query: str

@app.on_event("startup")
async def startup_db_client():
    # Create index in Elasticsearch if it doesn't exist
    try:
        await es_client.indices.create(
            index="items",
            body={
                "mappings": {
                    "properties": {
                        "name": {"type": "text"},
                        "description": {"type": "text"},
                        "price": {"type": "float"}
                    }
                }
            },
            ignore=400  # ignore 400 already exists error
        )
    except Exception as e:
        print(f"Error creating index: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()
    await es_client.close()

# MongoDB endpoints
@app.post("/items/mongo")
async def create_item_mongo(item: Item):
    result = await mongo_collection.insert_one(item.dict())
    return {"id": str(result.inserted_id)}

@app.get("/items/mongo")
async def read_items_mongo():
    items = []
    cursor = mongo_collection.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        items.append(document)
    return items

# Elasticsearch endpoints
@app.post("/items/elastic")
async def create_item_elastic(item: Item):
    result = await es_client.index(index="items", document=item.dict())
    return {"result": result["result"], "id": result["_id"]}

@app.post("/items/elastic/search")
async def search_items_elastic(query: SearchQuery):
    result = await es_client.search(
        index="items",
        body={
            "query": {
                "multi_match": {
                    "query": query.query,
                    "fields": ["name", "description"]
                }
            }
        }
    )
    return result["hits"]["hits"]

@app.get("/health/elastic")
async def check_elastic_health():
    try:
        health = await es_client.cluster.health()
        return {
            "status": "healthy",
            "cluster_status": health["status"],
            "number_of_nodes": health["number_of_nodes"]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Elasticsearch is not healthy: {str(e)}")

@app.get("/health/mongo")
async def check_mongo_health():
    try:
        # Try to execute a simple command to check if MongoDB is responsive
        await mongo_db.command("ping")
        return {
            "status": "healthy",
            "message": "MongoDB connection is successful"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB is not healthy: {str(e)}")

@app.get("/constant")
async def get_constant():
    s = 0
    for i in range(1000000):
        s += i
    return {
        "value": 42,
        "message": "This is a constant value"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
