WebPy-GraphQL
=============

.. image:: https://travis-ci.org/Igor-britecore/webpy-graphql.svg?branch=master :target: https://travis-ci.org/Igor-britecore/webpy-graphql .. image:: https://coveralls.io/repos/github/Igor-britecore/webpy-graphql/badge.svg?branch=master    :target: https://coveralls.io/github/Igor-britecore/webpy-graphql?branch=master .. image:: https://badge.fury.io/py/WebPy-GraphQL.svg  :target: https://badge.fury.io/py/WebPy-GraphQL


Adds GraphQL support to your WebPy application.

Usage
-----

Just use the ``GraphQLView`` view from ``webpy_graphql``

.. code:: python

    from webpy_graphql import GraphQLView

    urls = ("/graphql", "GQLGateway")

    app = web.application(urls, globals())

    class GQLGateway(GraphQLView):
        class GraphQLMeta:
            schema=Schema

This will add ``/graphql``  endpoints to your app (GET and POST methods implemented in the class GraphQLView).

Supported options
~~~~~~~~~~~~~~~~~

-  ``schema``: The ``GraphQLSchema`` object that you want the view to
   execute when it gets a valid request.
-  ``context``: A value to pass as the ``context`` to the ``graphql()``
   function.
-  ``root_value``: The ``root_value`` you want to provide to
   ``executor.execute``.
-  ``pretty``: Whether or not you want the response to be pretty printed
   JSON.
-  ``executor``: The ``Executor`` that you want to use to execute
   queries.
-  ``graphiql``: If ``True``, may present
   `GraphiQL <https://github.com/graphql/graphiql>`__ when loaded
   directly from a browser (a useful tool for debugging and
   exploration).
-  ``batch``: Set the GraphQL view as batch (for using in
   `Apollo-Client <http://dev.apollodata.com/core/network.html#query-batching>`__
   or
   `ReactRelayNetworkLayer <https://github.com/nodkz/react-relay-network-layer>`__)
-  ``graphiql_temp_title``: Set template title for GraphiQL
