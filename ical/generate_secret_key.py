from __future__ import with_statement

from django.utils.crypto import get_random_string


def generate_secret_key(filename):
    print filename
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret = get_random_string(50, chars)
    with open(filename, 'w') as f:
        f.write('SECRET_KEY="%s"' % secret)
    return True
