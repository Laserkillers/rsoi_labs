import functools


import requests
from os import getenv as env

from typing import Callable, ClassVar, Dict, Optional


class _AuthorizationInformation:
    _instance=None

    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(_AuthorizationInformation, cls).__new__(cls)
            cls.__auth_host = env("KEYCLOAK_URL")
            cls.__auth_path = env("KEYCLOAK_AUTH_PATH")
            cls.__auth_client_id = env("KEYCLOAK_CLIENT_ID")
            cls.__auth_client_user = env("KEYCLOAK_CLIENT_USER")
            cls.__auth_password = env("KEYCLOAK_CLIENT_PASSWORD")
            cls.__auth_client_secret = env("KEYCLOAK_CLIENT_SECRET")
            cls.__grant_type = env("KEYCLOAK_GRANT_TYPE")
            cls.__introspect_url = env("KEYCLOAK_TOKEN_INTROSPECT_PATH")
            cls.__headers_token = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        return cls._instance

    @property
    def auth_host(self):
        return self.__auth_host

    @property
    def auth_path(self):
        return self.__auth_path

    @property
    def auth_client_id(self):
        return self.__auth_client_id

    @property
    def auth_client_user(self):
        return self.__auth_client_user

    @property
    def auth_password(self):
        return self.__auth_password

    @property
    def auth_client_secret(self):
        return self.__auth_client_secret

    @property
    def grant_type(self):
        return self.__grant_type

    @property
    def headers_token(self):
        return self.__headers_token

    @property
    def introspect_url(self):
        return self.__introspect_url

    def __init__(self):
        return


class AuthorizationAPI(_AuthorizationInformation):
    _instance = None
    _first_init = False

    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(AuthorizationAPI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._first_init:
            return
        super().__init__()
        self._first_init = True
        self.__url_to_auth = f"{self.auth_host}{self.auth_path}"
        self.__url_introspect_path = f"{self.auth_host}{self.introspect_url}"
        self.__payload_token = (
            f'client_id={self.auth_client_id}&'
            'username={0}&'
            'password={1}&'
            f'grant_type={self.grant_type}&'
            f'client_secret={self.auth_client_secret}'
        )
        self.__access_token = None
        self.__refresh_token = None
        self.__access_type = None
        self.__time_token_expire = -1.
        self.__time_refresh_token_expire = -1.
        return

    def authorize_client(self, username: str, password: str):
        print(self.__payload_token.format(username, password))
        result_request = requests.post(
            self.__url_to_auth,
            headers=self.headers_token,
            data=self.__payload_token.format(username, password)
        )

        if not result_request.ok:
            raise ConnectionError(f'Unable to connect to Auth service. Report = {result_request.content}')

        result_request = result_request.json()

        self.__access_type = result_request['token_type']

        self.__access_token = result_request['access_token']
        self.__time_token_expire = result_request['expires_in']

        self.__refresh_token = result_request['refresh_token']
        self.__time_refresh_token_expire = result_request['refresh_expires_in']
        return {
            # 'access_token': f'{self.__access_type} {self.__access_token}',
            'access_token': f'{self.__access_token}',
            'refresh_token': f'{self.__refresh_token}',
            'expires_in': f'{self.__time_token_expire} seconds',
        }

    def check_token(self, token: str):
        payload_token = (
            f'token={token}&'
            f'client_id={self.auth_client_id}&'
            f'client_secret={self.auth_client_secret}'
        )

        result_request = requests.post(
            self.__url_introspect_path,
            headers=self.headers_token,
            data=payload_token
        )

        if not result_request.ok:
            raise ConnectionError(result_request.content)
        result_request = result_request.json()
        active_flag = result_request['active']

        if active_flag:
            response = f"Token is active"
        else:
            response = f"Token is inactive. Client unauthorized"

        return {
            'success': active_flag,
            'message': response
        }

    def required_login(self, request, make_response_func):
        def inner_decorator(func: Callable):
            @functools.wraps(func)
            def check_login(*args, **kwargs):
                try:
                    user_token = request.headers.get('Authorization')
                    if user_token is None:
                        return make_response_func({'status': 401, 'message': 'User token is not entered'}, 401)
                    check_status = self.check_token(user_token.replace('Bearer ', ''))
                except ConnectionError:
                    return make_response_func({'status': 504, 'message': 'Server authorization is unavailable'}, 504)
                if not check_status['success']:
                    return make_response_func({'status': 401, 'message': 'Invalid user token. Please authorize'}, 401)
                return func(*args, **kwargs)
            return check_login
        return inner_decorator


# class CheckLoginForRequest:




