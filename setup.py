from setuptools import setup, find_packages

# Package metadata
name = 'pyper'
version = '0.9.0'
description = 'A simple (yet sophisticated) pipeline implementation for Python.'

# Package dependencies
dependencies = []

# Package setup
setup(
    name=name,
    version=version,
    description=description,
    packages=find_packages(),
    install_requires=dependencies,
    download_url="https://github.com/guynir/pyper/archive/refs/tags/0.9.0.tar.gz",
    license='MIT',
    author='Guy Raz Nir',
    classifiers=[
        'Development Status :: Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)
