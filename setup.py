from setuptools import setup, find_packages

setup(
    name="wcferry-windows",
    version="39.3.2.0",
    packages=find_packages(),
    install_requires=[
        "wcferry",
        "grpcio-tools",
        "pynng"
    ],
    entry_points={
        'console_scripts': [
            'wcferry=wcferry.main:main',
        ],
    },
    author="原作者",
    description="WeChatFerry Windows安装包",
    long_description=open("README.MD").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
) 