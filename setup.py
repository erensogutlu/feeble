# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="feeble",
    version="1.0.0",
    description="Web Güvenlik Açığı Tarayıcı - SQL Injection, XSS, LFI ve daha fazlası",
    author="erensogutlu",
    packages=["moduller"],
    py_modules=[
        "ana", "tarayici", "surungan", "istek",
        "rapor", "yapilandirma", "yardimci",
    ],
    include_package_data=True,
    package_data={
        "": ["payloadlar/*.txt"],
    },
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "colorama>=0.4.5",
        "urllib3>=1.26.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "feeble=ana:ana_fonksiyon",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Security",
    ],
)
