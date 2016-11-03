=====
Django_rest_apitest
=====

Djano_rest_apitest aim to simpler api back_end test.

Quick start
-----------

1. How to install in yourself project::

  pip install -e git://github.com/tmacjx/django_rest_apitest.git@master#egg=django_rest_apitest


2. Add "rest_apitest" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'rest_apitest',
    ]

3. Manual generate an api-schema.json file used for check request and corresponding response.
   The format style of json file refer to api-schema-1.0.json.

4. Add 'API_SCHEMA' to your project's setting file which value is api-schema.json's absolute file path like this::

   API_SCHEMA = os.path.join(PROJECT_ROOT, 'demo.json')


5. Which we supply::

  from rest_apitest.main import SchemaTestCase
  from rest_apitest.util import UserBasicFactory, AdminFactory, UserFactory


6. More detail, please see test_project



Refer to: http://github.com/yeti/yak-server.git@master#egg=yak-server
