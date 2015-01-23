import random
random = random.SystemRandom()


def generate_secret_key(filename):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    length = 50
    secret = ''.join([random.choice(chars) for i in range(length)])
    if filename:
        with open(filename, 'w') as f:
            f.write('SECRET_KEY = "%s"\n' % secret)
    return secret


if __name__ == '__main__':
    print(generate_secret_key(None))
