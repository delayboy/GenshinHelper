from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='addPartnerHelper',
    ext_modules=cythonize("PartnerHelper.py",language_level="3"),
)
