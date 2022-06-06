from multiprocessing import allow_connection_pickling
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from redis_om import get_redis_connection, HashModel #redis om is a redis orm for python

app = FastAPI()

#middleware 
app.add_middleware(
    CORSMiddleware, #when a running frontend js code communicates with the backend(python code ) of differnent origins 
    allow_origins=["http://localhost:3000"], #the js frontend port
    #allowing the front end to request our api's
    allow_methods=["*"],# allows all methods 
    allow_headers=["*"]
)


redis = get_redis_connection(
     host="redis-16743.c261.us-east-1-4.ec2.cloud.redislabs.com",
     port =16743,
     password="B66qs1VguhaVR7h9vDUX98A83vnWmNjn",
     decode_responses=True 
 )

#hash models store data as hashes in the redis db
class Product(HashModel):
    name: str 
    price: float
    quantity: int

    class Meta: #meta connects the Product model  to redis database 
        database=redis


@app.get('/products')
def all():
    return [format(pk) for  pk in Product.all_pks()]         
def format(pk:str):
    product = Product.get(pk)
    return {
        'id':product.pk,
        'name':product.name,
        'price':product.price,
        'quantity':product.quantity
        }


@app.post("/products")
def create(product:Product):
    return product.save()  
    
@app.get("products/{pk}")
def get(pk:str):
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete(pk:str):
    return Product.delete(pk)    