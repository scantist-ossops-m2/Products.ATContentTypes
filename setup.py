from setuptools import setup, find_packages

version = '2.3.5.dev0'

setup(name='Products.ATContentTypes',
      version=version,
      description="Default Content Types for Plone 2.1-4.3",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Framework :: Plone",
          "Framework :: Plone :: 5.1",
      ],
      keywords='Plone Content Types',
      author='AT Content Types development team',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
              'zope.annotation',
              'zope.testing',
              'plone.app.testing',
          ]
      ),
      install_requires=[
          'setuptools',
          'plone.i18n',
          'plone.memoize',
          'plone.app.blob',
          'plone.app.collection',
          'plone.app.folder',
          'plone.app.imaging',
          'plone.app.layout',
          'plone.app.widgets>=1.4.0dev',
          'zope.component',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher',
          'zope.tal',
          'Products.CMFPlone',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFFormController',
          'Products.GenericSetup',
          'Products.MimetypesRegistry',
          'Products.PortalTransforms',
          'Products.validation',
          'Acquisition',
          'DateTime',
          'ExtensionClass',
          'transaction',
          'ZConfig',
          'ZODB3',
          'Zope2',
      ],
      )
