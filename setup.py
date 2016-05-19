from setuptools import setup

setup(
    name="bsn-autoupdate",

    author="Nemanja Tosic",
    author_email="nemanja@bluesensenetworks.com",

    platforms=["arm"],

    packages=["bsnautoupdate"],

    entry_points={
        'console_scripts': [
            'bsn-autoupdate = bsnautoupdate.__main__:main'
        ],
    }
)
