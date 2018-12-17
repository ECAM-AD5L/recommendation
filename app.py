from flask import Flask
from flask_restful import Resource, Api, reqparse
import collections
import os
from neo4j.v1 import GraphDatabase

app = Flask(__name__)
api = Api(app)

uri = os.environ['NEO4J_URL']
driver = GraphDatabase.driver(uri, auth=("neo4j", "1234"))

post_parser = reqparse.RequestParser()
post_parser.add_argument('user_id', type=int, required=True, location=['json'])
post_parser.add_argument('item_id', type=int, required=True, location=['json'])
post_parser.add_argument('order_id', type=int, required=True, location=['json'])

get_parser = reqparse.RequestParser()
get_parser.add_argument('item_id', type=int, required=True, location=['json'])
get_parser.add_argument('n', type=int, required=False, default=1, location=['json'])

class Recommendation(Resource):
    def post(self):
        args = post_parser.parse_args()
        user_id = args['user_id']
        item_id = args['item_id']
        order_id = args['order_id']

        with driver.session() as session:
            # Check if the user already exists. If doesn't, create it
            cql_query = "MATCH (u:User) "\
                        "WHERE u.user_id = '%s' "\
                        "RETURN u" % (user_id)
            result = session.run(cql_query)

            if result.peek() is None:
                cql_query = "CREATE (u:User {user_id: '%s'})" % (user_id)
                session.run(cql_query)
            
            # Check if the item already exists. If doesn't, create it
            cql_query = "MATCH (i:Item) "\
                        "WHERE i.item_id = '%s' "\
                        "RETURN i" % (item_id)
            result = session.run(cql_query)
            
            if result.peek() is None:
                cql_query = "CREATE (i:Item {item_id: '%s'})" % (item_id)
                session.run(cql_query)
            
            # Create the relation between the user and the item
            cql_query = "MATCH (u:User), (i:Item) "\
                        "WHERE u.user_id = '%s' AND i.item_id = '%s' "\
                        "CREATE (u)-[b:BUY {order_id: '%s'}]->(i)" % (user_id,
                                                                      item_id,
                                                                      order_id)
            session.run(cql_query)

            return {"message" : "(User: '%s')-[BUY: '%s']->(Item: '%s') added" % (user_id,
                                                                                  order_id,
                                                                                  item_id)}

    def get(self):
        args = get_parser.parse_args()
        item_id = args['item_id']
        n = args['n']
        
        with driver.session() as session:
            # Find the linked items in the graph
            cql_query = "MATCH (i1:Item)<-[b1:BUY]-(u:User)-[b2:BUY]->(i2:Item) "\
                        "WHERE i1.item_id = '%s' AND b1.order_id = b2.order_id "\
                        "RETURN i2.item_id AS item_id" % (item_id)
                                              
            result = session.run(cql_query) 
            items = []      
            for record in result:
                items.append(record['item_id'])
            
            # Take the n most frequent items
            counter = collections.Counter(items)
            maximums = []
            for i in range(n):
                maximum = max(counter, key=counter.get)
                maximums.append(maximum)
                del(counter[maximum])
            
            return {'items_id' : maximums}
 
api.add_resource(Recommendation, '/api')

if __name__ == '__main__':
    app.run(debug=True)
