# __recommendation_service__
A python service that offers an Amazon-like recommendation system for e-commerce
 
## Dependencies
 
Python package :
 
* flask
* flask_restful
* neo4j-driver
 
use pip install

## Run

```shell
export FLASK_APP=recommendation.py
flask run
```

## API Documentation
 
### Add a purchase
 
```shell
curl http://example.com/api --request POST -d '{"user_id":124, "order_id":238, "item_id":159}' -H "Content-Type: application/json"
```

> The above command returns JSON structured like this:

```json
{
    "message": "(User: '124')-[BUY: '238']->(Item: '159') added"
}
```

#### Parameters

Parameter | Description
--------- | -----------
user_id | the id of the user who placed the order (required)
order_id | the order id that contains the item (required)
item_id | the id of the item purchased (required)

### Get recommendations
 
 ```shell
curl http://example.com/api --request GET -d '{"item_id":139, "n":2}' -H "Content-Type: application/json"
```

> The above command returns JSON structured like this:

```json
{
    "items_id": [
        "159",
        "170"
    ]
}
```

#### Parameters

Parameter | Description
--------- | -----------
item_id | the id of the item purchased (required)
n | the number of recommendations desired (not required, default : 1)
