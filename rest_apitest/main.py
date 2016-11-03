# coding=utf-8
from util import APITestCaseWithAssertions
from django.conf import settings
import json
from util import basic_auth_str


class SchemaTestCase(APITestCaseWithAssertions):

    ACTION_TYPE = ['get', 'post', 'put', 'patch', 'delete', 'photo_upload', 'video_upload']

    AUTH_TYPE = ['basic_credential', 'session_credential', 'oauth_credential']

    def setUp(self, **kwargs):
        super(SchemaTestCase, self).setUp()
        self.schema_objects = {}

        user_settings = getattr(settings, 'API_SCHEMA', None)
        assert user_settings is not None, u"please set an variable what's name is API_SCHEMA in your project's " \
                                          u"and it's value must be a absolute file path"
        self.auth_type = kwargs.pop('AUTH_TYPE', 'basic_credential')
        assert self.auth_type in self.AUTH_TYPE, u"auth_type's value must be one of basic_credential, " \
                                                 u"session_credential or oauth_credential"
        if hasattr(self, self.auth_type):
            handler = getattr(self, self.auth_type)
            setattr(self, 'add_credentials', handler)

        with open(user_settings) as file:
            schema_data = json.loads(file.read())
            self.schema_objects = schema_data['objects']

    def check_schema_keys(self, data_object, schema_fields):
        """
        `data_object` is the actual JSON being sent or received
        `schema_fields` is the expected JSON based on the schema file
        """
        required_fields = []

        for schema_field, schema_type in schema_fields.items():
            # If this field is actually another related object, then check that object's fields as well
            schema_parts = schema_type.split(',')
            is_list = False
            is_optional = False
            new_schema_object = None
            for part in schema_parts:
                # Parse through all parts, regardless of ordering
                if part in ["array", "O2M", "M2M"]:
                    is_list = True
                elif part == "optional":
                    is_optional = True
                elif part.startswith('$'):
                    new_schema_object = part

            if not is_optional:
                required_fields.append(schema_field)

            if new_schema_object:
                if schema_field not in data_object or data_object[schema_field] is None:
                    # If our new object to check is None and optional then continue, else raise an error
                    if is_optional:
                        continue
                    else:
                        raise self.failureException("No data for object {0}".format(new_schema_object))

                new_data_object = data_object[schema_field]
                if is_list:
                    # If our new object to check is a list of these objects, continue if we don't have any data
                    # Else grab the first one in the list
                    if len(new_data_object) == 0:
                        continue
                    new_data_object = new_data_object[0]

                self.check_schema_keys(new_data_object, self.schema_objects[new_schema_object])

        set_required_fields = set(required_fields)
        set_data_object = set(data_object)
        set_schema_fields = set(schema_fields)
        # The actual `data_object` contains every required field
        self.assertTrue(set_required_fields.issubset(set_data_object),
                        "Data did not match schema.\nMissing fields: {}".format(
                            set_required_fields.difference(set_data_object)))

        # The actual `data_object` contains no extraneous fields not found in the schema
        self.assertTrue(set_data_object.issubset(set_schema_fields),
                        "Data did not match schema.\nExtra fields: {}".format(
                            set_data_object.difference(set_schema_fields)))

    def session_credential(self, user):
        """
        采用session认证
        The login method functions exactly as it does with Django's regular Client class.
        This allows you to authenticate requests against any views which include SessionAuthentication.
        """
        # credentials = {'username': user.username, 'password': user.username}
        credentials = {'username': user.username, 'password': user.cached_raw_password}

        # Make all requests in the context of a logged in session.
        self.client.login(**credentials)

    def oauth_credential(self, user):
        """
        采用oauth2认证
        Adds OAuth2.0 authentication as specified in `rest_user`
        If no user is specified, clear any existing credentials (allows us to
        check unauthorized requests)
        """
        if user:
            token = user.accesstoken_set.first()
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.token)
        else:
            self.client.credentials()

    def basic_credential(self, user):
        """
        采用BasicAuthentication
        """
        if user:
            self.client.credentials(HTTP_AUTHORIZATION=basic_auth_str(user.username, user.cached_raw_password))

    def check_response_data(self, response, response_object_name):
        results_data = response.data

        if "results" in response.data or isinstance(response.data, list):  # If multiple objects returned
            if "results" in response.data:
                results_data = response.data["results"]
            else:  # A plain list is returned, i.e. from a bulk update request
                results_data = response.data

            if len(results_data) == 0:
                raise self.failureException("No data to compare response")
            results_data = results_data[0]

        self.check_schema_keys(results_data, self.schema_objects[response_object_name])

    def assertSchemaGet(
            self,
            url,
            parameters,
            response_object_name,
            user,
            unauthorized=False):
        """
        Checks GET parameters and results match the schema
        """
        self.add_credentials(user)
        response = self.client.get(url, parameters)
        if unauthorized:
            self.assertHttpNotAllowed(response)
        else:
            self.assertValidJSONResponse(response)
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaPost(
            self,
            url,
            request_object_name,
            response_object_name,
            data,
            user,
            format="json",
            unauthorized=False,
            status_OK=False):
        """
        Checks POST data and results match schema

        status_OK: used for non-standard POST requests that do not return 201,
            e.g. if creating a custom route that uses POST
        """
        if isinstance(data, list):  # Check first object if this is a bulk create
            self.check_schema_keys(data[0], self.schema_objects[request_object_name])
        else:
            self.check_schema_keys(data, self.schema_objects[request_object_name])

        self.add_credentials(user)
        response = self.client.post(url, data, format=format)
        if unauthorized:
            self.assertHttpNotAllowed(response)
        elif status_OK:
            self.assertHttpOK(response)
            self.assertTrue(response['Content-Type'].startswith('application/json'))
            self.check_response_data(response, response_object_name)
        else:
            self.assertHttpCreated(response)
            self.assertTrue(response['Content-Type'].startswith('application/json'))
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaPatch(
            self,
            url,
            request_object_name,
            response_object_name,
            data,
            user,
            format="json",
            unauthorized=False):
        """
        Checks PATCH data and results match schema
        """
        self.check_schema_keys(data, self.schema_objects[request_object_name])

        self.add_credentials(user)
        response = self.client.patch(url, data, format=format)
        if unauthorized:
            self.assertHttpNotAllowed(response)
        else:
            self.assertValidJSONResponse(response)
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaPut(
            self,
            url,
            request_object_name,
            response_object_name,
            data,
            user,
            format="json",
            unauthorized=False,
            forbidden=False):
        """
        Assumes PUT is used for bulk updates, not single updates.
        Runs a PUT request and checks the PUT data and results match the
        schema for bulk updates. Assumes that all objects sent in a bulk
        update are identical, and hence only checks that the first one
        matches the schema.
        """
        self.check_schema_keys(data[0], self.schema_objects[request_object_name])

        self.add_credentials(user)
        response = self.client.put(url, data, format=format)
        if forbidden:
            # Attempting to update an object that isn't yours means it isn't in the queryset. DRF reads this as
            # creating, not updating. Since we have the `allow_add_remove` option set to False, creating isn't
            # allowed. So, instead of being rejected with a 403, server returns a 400 Bad Request.
            self.assertHttpBadRequest(response)
        elif unauthorized:
            self.assertHttpUnauthorized(response)
        else:
            self.assertValidJSONResponse(response)
            self.check_response_data(response, response_object_name)

        return response

    def assertSchemaDelete(
            self,
            url,
            user,
            unauthorized=False):
        """
        Checks DELETE
        """
        self.add_credentials(user)
        response = self.client.delete(url)

        if unauthorized:
            self.assertHttpNotAllowed(response)
        else:
            self.assertHttpAccepted(response)

        return response

    def assertPhotoUpload(self):
        pass

    def assertVideoUpload(
            self,
            url,
            obj_to_update,
            user,
            path_to_video,
            path_to_thumbnail,
            related_media_model=None,
            related_name=None,
            unauthorized=False,
            **kwargs
    ):
        """
        Checks that the video is uploaded and saved
        If the model being 'updated' is not the model that actually stores
        files (e.g., there is a Media model that has a relation to the model
        being updated), pass that model and the keyword field on that model
        that relates to the model being updated
        """
        self.add_credentials(user)
        kwargs = {
            "data": {
                'video_file': open(settings.PROJECT_ROOT + path_to_video, 'rb')
            },
            'format': 'multipart'
        }
        response = self.client.post(url, **kwargs)

        if unauthorized:
            self.assertHttpForbidden(response)
        else:
            self.assertHttpCreated(response)
            self.assertTrue(response['Content-Type'].startswith('application/json'))

            # Check the video and thumbnail are saved
            if related_media_model and related_name:
                filters = {
                    related_name: obj_to_update
                }
                obj_to_update = related_media_model.objects.filter(**filters)[0]
            else:
                obj_to_update = obj_to_update.__class__.objects.get(pk=obj_to_update.pk)
            original_file_field_name = getattr(obj_to_update, "original_file_name", "original_file")
            original_file = getattr(obj_to_update, original_file_field_name)
            self.assertEqual(
                original_file.file.read(),
                open(settings.PROJECT_ROOT + path_to_video, 'r').read()
            )
            self.assertEqual(
                obj_to_update.thumbnail.file.read(),
                open(settings.PROJECT_ROOT + path_to_thumbnail, 'r').read()
            )








