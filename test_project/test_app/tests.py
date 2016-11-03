# coding=utf-8
from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_apitest.main import SchemaTestCase
from rest_apitest.util import UserBasicFactory
User = get_user_model()

# session认证情况下
# 如果需要模拟用户登出，则需要自行添加
# self.client.logout()


class UserTests(SchemaTestCase):
    def setUp(self):
        # 指定测试采用的认证方式
        # basic_credential   >> basic
        # session_credential  >> session
        # oauth_credential   >> oauth2 token

        # 默认为basic_credential
        super(UserTests, self).setUp()

        # 其他需要以关键字传入
        # auth_type = session_credential
        # super(UserTests, self).setUp(auth_type=session_credential)

        self.user = UserBasicFactory()

    def test_info(self):
        url = reverse('user-info')
        parameters = {}
        response_object_name = "$infoResponse"
        response = self.assertSchemaGet(url, parameters=parameters, user=self.user, response_object_name=
                                        response_object_name)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
