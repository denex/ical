from fabric.api import run, env, cd, sudo

env.hosts = ['denex@rpi']


def update_rpi():
    with cd('/home/denex/ical/'):
        run('git pull origin production')
        sudo('pip install -r requirements.txt')
        run('./manage.py syncdb')
        run('./manage.py test ical')
        sudo('supervisorctl restart django_ical')
