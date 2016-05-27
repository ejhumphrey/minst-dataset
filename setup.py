from setuptools import setup

__desc__ = 'Python library for wrangling instrument datasets.'

if __name__ == "__main__":
    setup(
        name='minst',
        version='0.1',
        description=__desc__,
        author='Eric J. Humphrey',
        author_email='humphrey.eric@gmail.com',
        url='',
        download_url='',
        packages=['minst'],
        package_data={},
        long_description=__desc__,
        classifiers=[
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            'Intended Audience :: Science/Research',
            'Environment :: Console',
            'Environment :: Plugins'
        ],
        keywords='',
        license='',
        install_requires=[
            'numpy',
            'pandas',
            'joblib',
            'claudio',
            'pytest'
        ],
        extras_require={}
    )
