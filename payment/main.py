from  multiprocessing import allow_connection_pickling
from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware 
from redis_om import get_redis_connection, HashModel #redis om is a redis orm for python
from starlette.requests import Request
import requests,time




app = FastAPI()

#middleware 
app.add_middleware(
    CORSMiddleware, #when a running frontend js code communicates with the backend(python code ) of differnent origins 
    allow_origins=["http://localhost:3000"], #the js frontend port
    #allowing the front end to request our api's
    allow_methods=["*"],# allows all methods 
    allow_headers=["*"]
)

#This should be a different database 
redis = get_redis_connection(
     host="redis-16743.c261.us-east-1-4.ec2.cloud.redislabs.com",
     port =16743,
     password="B66qs1VguhaVR7h9vDUX98A83vnWmNjn",
     decode_responses=True 
 )

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # shows if its pending, completed, refunded

    class Meta:
        database = redis




@app.get('/get-orders/{pk}')
def get(pk: str):
    order = Order.get(pk)
    redis.xadd("refund_order",order.dict(),"*")
    return order


@app.post('/post-orders')
async def create(request: Request, background_tasks: BackgroundTasks):  # id, quantity
    body = await request.json()

 #sending the products we want to the inventory microservice and also retrieving 
    req = requests.get('http://localhost:8000/products/%s' % body['id'])#products will be coverted into the body value 
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save() #returns status  completed 

    #when completed it changes the status in the background 
    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5) #the time to confirm our order 
    order.status = 'completed'
    order.save()
    #sending an event to a redis stream, xadd adds data to a stream  when the payment is made 
    redis.xadd('order_completed', order.dict(), '*') #  * respresents the id of the  order




#used uvicorn main:app --reload --port=8001 to test and communicate with inventory port during development stage 