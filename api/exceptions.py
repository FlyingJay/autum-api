from rest_framework.exceptions import ValidationError


class DuplicateEmailError(ValidationError):
    status_code = 400
    default_detail = 'Looks like you\'ve already made an account with that email. Please try another.'
    default_code = 'duplicate_email'

