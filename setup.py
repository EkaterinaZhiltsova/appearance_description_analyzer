from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()
    
 
setup(name='appearance_description_analyzer',
      version='0.16',
      description='Аppearance description analyzer',
      long_description=readme,
      long_description_content_type="text/markdown",
      url="https://github.com/EkaterinaZhiltsova/appearance_description_analyzer",
      packages=find_packages(),
      package_data = { '': ['*.txt', '*.csv', '*.md'] },
      include_pacage_data=True,
      author_email='kathymai30521@gmail.com',
      install_requires=[line.strip() for line in open("requirements.txt").readlines()]
)