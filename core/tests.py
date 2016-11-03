# coding=utf-8
from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
# from core.util import UserBasicFactory
from django_rest_apitest import UserBasicFactory, SchemaTestCase
User = get_user_model()

# session认证情况下
# 如果需要模拟用户登出，则需要自行添加
# self.client.logout()


class UserTests(SchemaTestCase):
    def setUp(self):
        # 指定测试采用的认证方式
        # basic_credential  基于basic
        # session_credentia 基于session
        # oauth_credential  基于oauth2 token
        auth_type = 'basic_credential'
        super(UserTests, self).setUp(AUTH_TYPE=auth_type)
        self.user = UserBasicFactory()

    def test_info(self):
        url = reverse('user-info')
        parameters = {}
        response_object_name = "$infoResponse"
        response = self.assertSchemaGet(url, parameters=parameters, user=self.user, response_object_name=
                                        response_object_name)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)