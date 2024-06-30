from setuptools import setup, find_packages

setup(
       name='howdoai',
       version='1.0.0',
       description='A command-line tool to get answers to "how-to" questions using an AI endpoint',
       author='Donko Dimov',
       author_email='your@email.com',
       packages=find_packages(),
       install_requires=[
           'requests',
           'rich',
           'python-dotenv'
       ],
       entry_points={
           'console_scripts': [
               'howdoai = howdoai:main_cli',
           ],
       },
   )