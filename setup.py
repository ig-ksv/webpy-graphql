from setuptools import setup, find_packages

required_packages = [
    'web.py',
    'werkzeug',
    'graphql-server-core>=1.0.dev',
    'graphql-core>=1.0',
    'six',
    'paste'
]

setup(
    name='WebPy-GraphQL',
    version='1.2.1',
    description='Adds GraphQL support to your WebPy application',
    long_description=open('README.rst').read(),
    url='https://github.com/Igor-britecore/webpy-graphql',
    author='Igor Kozintsev',
    author_email='ig.kozintsev@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='api graphql protocol rest webpy grapene',
    packages=find_packages(exclude=['tests']),
    install_requires=required_packages,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
)
