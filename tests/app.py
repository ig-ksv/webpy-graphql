import web
import os
import sys

from webpy_graphql import GraphQLView
from schema import Schema

graphql_view = GraphQLView('graphql', schema=Schema)

def create_app(**kwargs):
    global graphql_view
    urls = ('/graphql', 'index')
    graphql_view = GraphQLView('graphql', schema=Schema, **kwargs) # graphiql=True, context='CUSTOM CONTEXT')
    return web.application(urls, globals())

class index:
    def GET(self):
        return graphql_view.dispatch()

    def POST(self):
        return graphql_view.dispatch()

def is_test():
    if 'TEST_ENV' in os.environ:
        return os.environ['TEST_ENV'] == 'webpy-graphql'

if __name__ == "__main__":
    app = create_app(graphiql=True)
    app.run()
