from setuptools import setup, find_packages

setup(

    name="summer_admin",
    version="1.0",
    keywords=("test", "xxx"),
    description="summer admin",
    long_description="summer adminfor python",
    license="MIT Licence",

    url="url",
    author="test",
    author_email="test@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'pymysql>=0.7.11',
        'django>=1.10.3',
        'django-cors-headers>=2.1.0',
        'thrift>=0.10.0',
        'configparser>=3.5.0'
    ],

    scripts=[],
    entry_points={
        'console_scripts': [
            'test = test.help:main'
        ]
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    # 此项需要，否则卸载时报windows error
    zip_safe=False

)
