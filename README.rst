=====
Django_rest_apitest
=====

Djano_rest_apitest aim to simpler api back_end test.

Quick start
-----------

1. Add "" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'rest_apitest',
    ]

2.Make sure you have installed 'oauth2_provider', 'rest_framework',

3.How To Use
  from rest_apitest.main import SchemaTestCase
  from rest_apitest.util import UserBasicFactory, UserAdminFactory, UserFactory
