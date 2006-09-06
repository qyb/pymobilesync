#distutils script for Win32 Build.
from distutils.core import setup, Extension
setup(name='irda',
      version='0.1',
      description='IrDA networking socket support',
      author='Yingbo Qiu',
      author_email='qiuyingbo@gmail.com',
      url='http://qyb.blogspot.com/',
      ext_modules=[Extension('_irsocket',
                             ['irsocket.c'],
                             define_macros=[('_WIN32_WINNT', None),
                                            ('MS_WINDOWS', None)
                                           ],
                             libraries=['ws2_32']
                            )
                  ],
      py_modules=['irda'],
      #data_files=[('',['_irsocket.pyd'])]
      )