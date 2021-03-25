from setuptools import find_packages, setup

setup(
    name="saf_jsonschema",
    author="SberDevices",
    author_email="developer@sberdevices.ru",
    description="SAF JSON Schemer — это плагин для SmartApp Framework, "
                "который позволяет валидировать сообщения.",
    long_description_content_type="text/markdown",
    license="sberpl-2",
    packages=find_packages(exclude=[]),
    package_data={
        "saf_patterns": ["schemas/*.json"]
    },
    include_package_data=True,
    install_requires=[
        'smart_app_framework',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
