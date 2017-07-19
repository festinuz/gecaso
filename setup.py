from distutils.core import setup

version = '0.2.1'
url = 'https://github.com/festinuz/gecaso'
download_url = url + '/archive/' + version + '.tar.gz'

setup(
  name='gecaso',
  packages=['gecaso'],
  version=version,
  description='Generalized Caching Solution',
  author='Michael Toporkov',
  author_email='festinuz@gmail.com',
  url=url,
  download_url=download_url,
  keywords=['cache', 'caching'],
  license='MIT',
  classifiers=[],
  python_requires='>=3.5, <4'
)
