from setuptools import setup, find_packages

setup(
    name='KInstaller',
    version='1.0.0',  
    description='An Arch Linux Package Assister',
    # long_description=open('README.md').read(),  
    # long_description_content_type='text/markdown',  
    author='KornineQ',  
    url='https://github.com/KornineQ/KInstaller',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kinstaller=kinstaller:main',
        ],
    },
    install_requires=[
        'termcolor',
        'distro',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
)
