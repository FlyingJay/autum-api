from rest_framework.exceptions import APIException, ValidationError


class BadRequest(APIException):
    status_code = 400
    default_detail = 'We were unable to process your request'
    default_code = 'bad_request'

class TokenInvalidException(Exception):
    pass

