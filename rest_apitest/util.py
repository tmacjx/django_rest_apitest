# coding=utf-8
import sys
import factory
import datetime
import oauth2_provider
from base64 import b64encode
from django.utils.timezone import now
from rest_framework.test import APITestCase
from oauth2_provider.models import AccessToken
from django.contrib.auth import get_user_model


User = get_user_model()

_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)


if is_py2:
    builtin_str = str
elif is_py3:
    builtin_str = str


def to_native_string(string, encoding='ascii'):
    """Given a string object, regardless of type, returns a representation of
    that string in the native string type, encoding and decoding where
    necessary. This assumes ASCII unless told otherwise.
    """
    if isinstance(string, builtin_str):
        out = string
    else:
        if is_py2:
            out = string.encode(encoding)
        else:
            out = string.decode(encoding)

    return out


def basic_auth_str(username, password):
    """Returns a Basic Auth string."""

    authstr = 'Basic ' + to_native_string(
        b64encode(('%s:%s' % (username, password)).encode('latin1')).strip()
    )
    return authstr


def get_package_version(package):
    """
    Return the version number of a Python package as a list of integers
    e.g., 1.7.2 will return [1, 7, 2]
    """
    return [int(num) for num in package.__version__.split('.')]


class APITestCaseWithAssertions(APITestCase):
    """
    Taken from Tastypie's tests to improve readability
    """
    def assertHttpOK(self, resp):
        """
        Ensures the response is returning a HTTP 200.
        """
        return self.assertEqual(resp.status_code, 200, resp)

    def assertHttpCreated(self, resp):
        """
        Ensures the response is returning a HTTP 201.
        """
        return self.assertEqual(resp.status_code, 201, resp)

    def assertHttpAccepted(self, resp):
        """
        Ensures the response is returning either a HTTP 202 or a HTTP 204.
        """
        return self.assertIn(resp.status_code, [202, 204], resp)

    def assertHttpMultipleChoices(self, resp):
        """
        Ensures the response is returning a HTTP 300.
        """
        return self.assertEqual(resp.status_code, 300, resp)

    def assertHttpSeeOther(self, resp):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(resp.status_code, 303, resp)

    def assertHttpNotModified(self, resp):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(resp.status_code, 304, resp)

    def assertHttpBadRequest(self, resp):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(resp.status_code, 400, resp)

    def assertHttpUnauthorized(self, resp):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(resp.status_code, 401, resp)

    def assertHttpForbidden(self, resp):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(resp.status_code, 403, resp)

    def assertHttpNotFound(self, resp):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(resp.status_code, 404, resp)

    def assertHttpMethodNotAllowed(self, resp):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(resp.status_code, 405, resp)

    def assertHttpNotAllowed(self, resp):
        """
        Depending on how we purposefully reject a call (e.g., limiting
        methods, using permission classes, etc.), we may have a few different
        HTTP response codes. Bundling these together into a single assertion
        so that schema tests can be more flexible.
        """
        return self.assertIn(resp.status_code, [401, 403, 404, 405], resp)

    def assertHttpConflict(self, resp):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(resp.status_code, 409, resp)

    def assertHttpGone(self, resp):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(resp.status_code, 410, resp)

    def assertHttpUnprocessableEntity(self, resp):
        """
        Ensures the response is returning a HTTP 422.
        """
        return self.assertEqual(resp.status_code, 422, resp)

    def assertHttpTooManyRequests(self, resp):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(resp.status_code, 429, resp)

    def assertHttpApplicationError(self, resp):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(resp.status_code, 500, resp)

    def assertHttpNotImplemented(self, resp):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(resp.status_code, 501, resp)

    def assertValidJSONResponse(self, resp):
        """
        Given a ``HttpResponse`` coming back from using the ``client``, assert that
        you get back:

        * An HTTP 200
        * The correct content-type (``application/json``)
        """
        self.assertHttpOK(resp)
        self.assertTrue(resp['Content-Type'].startswith('application/json'))


# 模拟user 适用oauth
class UserOAuthFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    username = factory.Sequence(lambda n: 'person{0}'.format(n))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super(UserOAuthFactory, cls)._create(model_class, *args, **kwargs)
        # Force save for post_save signal to create auth client
        user.save()
        oauth_toolkit_version = get_package_version(oauth2_provider)
        # If we're using version 0.8.0 or higher
        if oauth_toolkit_version[0] >= 0 and oauth_toolkit_version[1] >= 8:
            application = user.oauth2_provider_application.first()
        else:
            application = user.application_set.first()

        AccessToken.objects.create(user=user,
                                   application=application,
                                   token='token{}'.format(user.id),
                                   expires=now() + datetime.timedelta(days=1)
                                   )
        return user


# 模拟user 适用basic / session

class UserBasicFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    username = factory.Sequence(lambda n: 'person{0}'.format(n))
    # 密码默认长度 > 8  不能全为数字，不能与username相似
    password = factory.Sequence(lambda n: 'testuser{0}'.format(n))
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super(UserBasicFactory, cls)._create(model_class, *args, **kwargs)
        raw_password = user.password
        # Databases下密码加密保存
        user.set_password(user.password)
        # Force save for post_save signal to create auth client
        user.save()
        # 缓存user的raw_password，用于测试
        user.cached_raw_password = raw_password
        return user


# 模拟admin
class UserAdminFactory(UserBasicFactory):
    is_superuser = True
    is_staff = True



