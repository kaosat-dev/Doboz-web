from distutils.core import setup,find_packages

setup(
    name='Doboz-Web',
    version='0.32',
    description='Web based remote monitoring and control for Repraps (3d printers) and other variants',
    author='Mark "ckaos" Moissette',
    author_email='kaosat.dev@gmail.com',
    url='http://github.com/kaosat-dev/Doboz',
    keywords='web remote control remote monitoring reprap repstrap',
    license='GPL',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6"
    ], 
    packages=find_packages(),   
    entry_points = {
        'console_scripts': ['doboz-web = dobozweb.run:start_server']
    },
    install_requires=[
        'pyparsing','pySerial'
      ],
    )