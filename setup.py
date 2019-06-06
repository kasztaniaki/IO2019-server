from setuptools import setup, find_packages

PACKAGES = find_packages()

opts = dict(
    name="IO2019-server",
    maintainer="revanjjp",
    maintainer_email="nick@email.com",
    description="Virtual Machine manager",
    long_description="Virtual Machine manager for Software Engineering classes (IET 2019)",
    url="https://github.com/kasztaniaki/IO2019-server",
    download_url="https://github.com/kasztaniaki/IO2019-server",
    license="MIT",
    packages=PACKAGES,
)


if __name__ == "__main__":
    setup(**opts)
