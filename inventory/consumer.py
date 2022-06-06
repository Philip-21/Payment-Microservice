from main import redis, Product

import time

key = 'order_completed'
group = 'inventory-group'


#creating a redis consumer group to consume  based on the key and group
try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists!')

#the actual consumption logic
while True:
    try:
        #gets the results from the redis stremas using xread()
        results = redis.xreadgroup(group, key, {key: '>'}, None)

        if results != []:
            for result in results:
                obj = result[1][0][1] #getting the values of the list in index format
                try:
                    #decreasing the quantity when a consumer buys a product
                    product = Product.get(obj['product_id'])
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()
                except:
                    redis.xadd('refund_order', obj, '*')

    except Exception as e:
        print(str(e))
    time.sleep(1)