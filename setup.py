from setuptools import setup, find_packages

setup(name='appearance_description_analyzer',
      version='0.0',
      description='Аppearance description analyzer',
      packages=find_packages(),
      author_email='kathymai30521@gmail.com',
      install_requires=[line.strip() for line in open("requirements.txt").readlines()])