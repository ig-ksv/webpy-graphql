import json
import web
import unittest
from functools import wraps

from paste.fixture import TestApp
from app import create_app

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

j = lambda **kwargs: json.dumps(kwargs)
jl = lambda **kwargs: json.dumps([kwargs])


def _set_params(**params):
        def decorator(func):
            @wraps(func)
            def wrapper(self):
                app = create_app(**params)
                self.middleware = []
                self.testApp = TestApp(app.wsgifunc(*self.middleware))
                func(self)
            return wrapper
        return decorator

class WebPyGraphqlTests(unittest.TestCase):

    def setUp(self):
        app = create_app()
        self.middleware = []
        self.testApp = TestApp(app.wsgifunc(*self.middleware))

    def test_main_page(self):
        r = self.testApp.get('/graphql', params={'query': '{test}'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test":"Hello World"}}')

    def test_with_query_para(self):
        r = self.testApp.get('/graphql', params={'query': '{test}'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test":"Hello World"}}')

    def test_with_operation_name(self):
        r = self.testApp.get('/graphql',
                             params={'query': '''
                                    query helloYou { test_args(name: "You"), ...shared }
                                    query helloWorld { test_args(name: "World"), ...shared }
                                    query helloDolly { test_args(name: "Dolly"), ...shared }
                                    fragment shared on QueryRoot {
                                      shared: test_args(name: "Everyone")
                                    }
                                     ''',
                                    'operationName': 'helloWorld'
                                    })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('data'),
                         {"test_args":"Hello World","shared":"Hello Everyone"})


    def test_validation_errors(self):
        r = self.testApp.get('/graphql',
                             params={'query': '{ test, unknownOne, unknownTwo }'})
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors'),
                         [
                         {
                          u'message': u'Cannot query field "unknownOne" on type "QueryRoot".',
                          u'locations': [{u'column': 9, u'line': 1}]},
                         {
                          u'message': u'Cannot query field "unknownTwo" on type "QueryRoot".',
                          u'locations': [{u'column': 21, u'line': 1}]}
                         ])


    def test_with_variable_values(self):
        r = self.testApp.get('/graphql',
                             params={ 'query': '''query Test($name: String)
                                               {test_args(name: $name)}''',
                                      'variables': json.dumps({"name": "John"})})
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('data'),
                         {"test_args":"Hello John"})

    def test_with_missing_variable_values(self):
        r = self.testApp.get('/graphql',
                             params={ 'query': '''query Test($name: String)
                                               {test_args(name: $name)}'''})
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('data'),
                         {"test_args":"Hello None"})

    def test_with_default_variable_values(self):
        r = self.testApp.get('/graphql',
                             params={ 'query': '''query Test($name: String)
                                               {test_def_args (name: $name)}'''
                                    })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('data'),
                         {"test_def_args":"Hello World"})

    def test_with_default_without_variable_values(self):
        r = self.testApp.get('/graphql',
                             params={ 'query': 'query{test_def_args}'})
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('data'),
                         {"test_def_args":"Hello World"})

    def test_when_missing_operation_name(self):
        r = self.testApp.get('/graphql',
                             params={'query':
                                '''
                                query TestQuery { test }
                                mutation TestMutation { writeTest { test } }
                                '''
                                })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                         'Must provide operation name if query contains multiple operations.')

    def test_errors_when_sending_a_mutation_via_get(self):
        r = self.testApp.get('/graphql',
                             params={'query':
                                '''
                                mutation TestMutation { writeTest { test } }
                                '''
                                })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                         'Can only perform a mutation operation from a POST request.')

    def test_errors_when_selecting_a_mutation_within_a_get(self):
        r = self.testApp.get('/graphql',
                             params={'query':
                                '''
                                query TestQuery { test }
                                mutation TestMutation { writeTest { test } }
                                ''',
                                'operationName': 'TestMutation'
                                })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                         'Can only perform a mutation operation from a POST request.')

    def test_allows_mutation_to_exist_within_a_get(self):
        r = self.testApp.get('/graphql',
                             params={'query':
                                '''
                                query TestQuery { test }
                                mutation TestMutation { writeTest { test } }
                                ''',
                                'operationName': 'TestQuery'
                                })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('data'),
                         {'test': "Hello World"})

    def test_allows_post_with_json_encoding(self):
        r = self.testApp.post('/graphql',
                              params=j(query='{test}'),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test":"Hello World"}}')

    def test_allows_sending_a_mutation_via_post(self):
        r = self.testApp.post('/graphql',
                              params=j(query='mutation TestMutation { writeTest { test } }'),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"writeTest":{"test":"Hello World"}}}')

    def test_allows_post_with_url_encoding(self):
        r = self.testApp.post('/graphql',
                              params=urlencode(dict(query='{test}')),
                              headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test":"Hello World"}}')

    def test_supports_post_with_string_variables(self):
        r = self.testApp.post('/graphql',
                              params=j(query='''query helloWorld($name: String)
                                             { test_args (name: $name) }''',
                                       variables={'name': 'John'}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test_args":"Hello John"}}')

    def test_supports_post_json_query_with_json_variables(self):
        r = self.testApp.post('/graphql',
                              params=j(query='''query helloWorld($name: String)
                                             { test_args (name: $name) }''',
                                       variables={'name': 'John'}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test_args":"Hello John"}}')

    def test_supports_post_url_encoded_query_with_string_variables(self):
        r = self.testApp.post('/graphql',
                              urlencode(dict(query='query helloWorld($name: String){ test_args(name: $name) }',
                                             variables=j(name="John"))),
                              headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test_args":"Hello John"}}')


    def test_supports_post_json_query_with_get_variable_values(self):
        r = self.testApp.post('/graphql?variables={"name": "John"}',
                              params=j(query='query helloWorld($name: String){ test_args(name: $name) }'),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test_args":"Hello John"}}')

    def test_supports_post_url_encoded_with_get_variable_values(self):
        r = self.testApp.post('/graphql?variables={"name": "John"}',
                              urlencode(dict(query='query helloWorld($name: String){ test_args(name: $name) }')),
                              headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test_args":"Hello John"}}')

    def test_supports_post_raw_with_get_variable_values(self):
        r = self.testApp.post('/graphql?variables={"name": "John"}',
                              params='query=query helloWorld($name: String){ test_args(name: $name) }',
                              headers={'Content-Type': 'application/graphql'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test_args":"Hello John"}}')

    def test_allows_post_with_operation_name(self):
        r = self.testApp.post('/graphql',
                              params=j(query= '''
                              query helloYou { test_args(name: "You"), ...shared }
                              query helloWorld { test_args(name: "World"), ...shared }
                              query helloDolly { test_args(name: "Dolly"), ...shared }
                              fragment shared on QueryRoot {
                                shared: test_args(name: "Everyone")
                              }
                              ''',
                              operationName='helloWorld'),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body,
                         '{"data":{"test_args":"Hello World","shared":"Hello Everyone"}}')

    def test_allows_post_with_get_operation_name(self):
        r = self.testApp.post('/graphql?operationName=helloWorld',
                              params=j(query='''
                              query helloYou { test_args(name: "You"), ...shared }
                              query helloWorld { test_args(name: "World"), ...shared }
                              query helloDolly { test_args(name: "Dolly"), ...shared }
                              fragment shared on QueryRoot {
                                shared: test_args(name: "Everyone")
                              }
                              '''),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body,
                         '{"data":{"test_args":"Hello World","shared":"Hello Everyone"}}')

    def test_not_pretty_by_default(self):
        app = create_app(pretty=False)
        self.middleware = []
        self.testApp = TestApp(app.wsgifunc(*self.middleware))

        r = self.testApp.get('/graphql', params={ 'query': 'query{test}'})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"test":"Hello World"}}')

    def test_supports_pretty_printing_by_test(self):
        app = create_app(pretty=True)
        self.middleware = []
        self.testApp = TestApp(app.wsgifunc(*self.middleware))

        r = self.testApp.get('/graphql', params={ 'query': 'query{test}' })
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{\n  "data": {\n    "test": "Hello World"\n  }\n}')

    def test_handles_field_errors_caught_by_graphql(self):
        r = self.testApp.get('/graphql', params={ 'query': '{thrower}' })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                        "Throws!")

    def test_handles_syntax_errors_caught_by_graphql(self):
        r = self.testApp.get('/graphql', params={ 'query': 'syntaxerror' })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body),
                     { 'errors': [{'locations': [{'column': 1, 'line': 1}],
                           'message': 'Syntax Error GraphQL request (1:1) '
                               'Unexpected Name "syntaxerror"\n\n1: syntaxerror\n   ^\n'}]
                              })
    def test_handles_errors_caused_by_a_lack_of_query(self):
        r = self.testApp.get('/graphql')
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                         'Must provide query string.')

    def test_handles_batch_correctly_if_is_disabled(self):
        r = self.testApp.post('/graphql',
                              params={'query': "{}"},
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                        'POST body sent invalid JSON.')

    def test_handles_plain_post_text(self):
        r = self.testApp.post('/graphql?variables={"name": "John"}',
                              params='query helloWorld($name: String){ test_args(name: $name) }',
                              headers={'Content-Type': 'text/plain'})
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                         'Must provide query string.')

    def test_handles_poorly_formed_variables(self):
        r = self.testApp.get('/graphql',
                             params={ 'query': 'query helloWorld($name: String){ test_args(name: $name) }',
                                      'variables': "name: John" })
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body).get('errors')[0].get('message'),
                         "Variables are invalid JSON.")

    def test_handles_unsupported_http_methods(self):
        # need to improve
        r = self.testApp.put('/graphql',
                             params={ 'query': 'query{test}'}, expect_errors=True)
        self.assertEqual(r.status, 405)
        self.assertEqual(r.header_dict.get('allow'), 'GET, POST')

    @_set_params(context="CUSTOM CONTEXT")
    def test_supports_custom_context(self):
        r = self.testApp.get('/graphql', params={ 'query': 'query{context}' })
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"data":{"context":"CUSTOM CONTEXT"}}')

    def test_post_multipart_data(self):
        query = 'mutation TestMutation { writeTest { test } }'

        r = self.testApp.post('/graphql',
                              params={'query': query},
                              upload_files=[("Test", "text1.txt", "Guido")])
        self.assertEqual(r.status, 200)
        self.assertEqual(json.loads(r.body),
                         {u'data': {u'writeTest': {u'test': u'Hello World'}}})

    @_set_params(batch=True)
    def test_batch_allows_post_with_json_encoding(self):
        r = self.testApp.post('/graphql',
                              params=jl(query='{test}'),
                              headers={'Content-Type': 'application/json'})
        body = json.loads(r.body)[0]
        self.assertEqual(r.status, 200)
        self.assertEqual(body.get('id'), None)
        self.assertEqual(body.get('payload'), {"data":{"test":"Hello World"}})

    @_set_params(batch=True)
    def test_batch_supports_post_json_query_with_json_variables(self):
        r = self.testApp.post('/graphql',
                              params=jl(
                                  # id=1,
                                  query='query helloWorld($name: String){ test_args(name: $name) }',
                                  variables=j(name="John")),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)

        body = json.loads(r.body)[0]
        self.assertEqual(body.get('id'), None) # id=1
        self.assertEqual(body.get('payload'), {"data":{"test_args":"Hello John"}})

    @_set_params(batch=True)
    def test_batch_allows_post_with_operation_name(self):
        r = self.testApp.post('/graphql',
                              params=jl(
                              # id=1
                              query='''
                              query helloYou { test_args(name: "You"), ...shared }
                              query helloWorld { test_args(name: "World"), ...shared }
                              query helloDolly { test_args(name: "Dolly"), ...shared }
                              fragment shared on QueryRoot {
                                shared: test_args(name: "Everyone")
                              }
                              ''',
                              operationName='helloWorld'),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(r.status, 200)

        body = json.loads(r.body)[0]
        self.assertEqual(body.get('id'), None) # id=1
        self.assertEqual(body.get('payload'),
                         {"data":{"test_args":"Hello World","shared":"Hello Everyone"}})

    @_set_params(graphiql=True, graphiql_temp_title="TestTitle")
    def test_template_title(self):
        r = self.testApp.get('/graphql',
                             params={ 'query': 'query { test }' },
                             headers={'Accept': 'text/html'})
        self.assertEqual(r.status, 200)
        self.assertIn("<title>TestTitle</title>", r.body)


if __name__ == '__main__':
    unittest.main()
