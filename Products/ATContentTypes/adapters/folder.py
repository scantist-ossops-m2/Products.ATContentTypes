from zope.interface import implements
from Products.ATContentTypes.interface.folder import IFilterFolder
from cStringIO import StringIO
from zipfile import ZipFile
from Acquisition import aq_parent

class FolderFilter(object):
    """
    """
    implements(IFilterFolder)

    def __init__(self, context):
        self.context = context

    def listObjects(self):
        return self.context.objectValues()
