import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rest-apitest',
    version='0.1',
    packages=['rest_apitest'],
    install_requires=[
        'Django>=1.8',
        'factory-boy==2.4.1',
        'django-oauth-toolkit>=0.10.0',
        'djangorestframework>=3.1.0',
    ],
    include_package_data=True,
    license='BSD License',  # example license
    description='Djano-rest-apitest aim to simpler api back_end test.',
    long_description=README,
    url='https://github.com/tmacjx/django_rest_apitest',
    author='WangKan',
    author_email='kan49733110@163.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)