from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from UserDict import UserDict
import ExtensionClass
from Acquisition import Implicit
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from Persistence import Persistent

class FakeRequestSession(ExtensionClass.Base, UserDict):
    """Dummy dict like object with set method for SESSION and REQUEST
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    security.declareObjectPublic()
    
    def __init__(self):
        UserDict.__init__(self)
        # add a dummy because request mustn't be empty for test
        # like 'if REQUEST:'
        self['__dummy__'] = None
    
    def __nonzero__(self):
        return True
    
    def set(self, key, value):
        self[key] = value

InitializeClass(FakeRequestSession)
FakeRequestSession()

class DummySessionDataManager(Implicit):
    """Dummy sdm for sessioning
    
    Uses traversal hooks to add the SESSION object as lazy item to the request
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    security.declareObjectPublic()
    
    id = 'session_data_manager'
    
    def __init__(self):
        self.session = FakeRequestSession()
        
    def manage_afterAdd(self, item, container):
        """Register traversal hooks to add SESSION to request
        """
        parent = self.aq_inner.aq_parent
        hook = DummySDMTraverseHook()
        registerBeforeTraverse(parent, hook, 'SessionDataManager', 50)

    def getSessionData(self, create=1):
        """ """
        return self.session
    
    def hasSessionData(self):
        """ """
        return True
    
    def getSessionDataByKey(self, key):
        """ """
        return self.session
    
    def getBrowserIdManager(self):
        """ """
        # dummy
        return self

InitializeClass(DummySessionDataManager)

class DummySDMTraverseHook(Persistent):
    """Traversal hook for dummy sessions
    
    See Products.Sessions.SessionDataManager.SessionDataManagerTraverser
    """
    
    def __call__(self, container, request):
        id = DummySessionDataManager.id
        sdm = getattr(container, id)
        getSessionData = sdm.getSessionData
        request.set_lazy('SESSION', getSessionData)

def Xprint(s):
    """print helper

    print data via print is not possible, you have to use
    ZopeTestCase._print or this function
    """
    ZopeTestCase._print(str(s)+'\n')

def dcEdit(obj):
    """dublin core edit (inplace)
    """
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    # XXX more
    
from Products.validation import ValidationChain
EmptyValidator = ValidationChain('isEmpty')
EmptyValidator.appendSufficient('isEmpty')
idValidator = ValidationChain('isValidId')
idValidator.appendSufficient('isEmptyNoError')
idValidator.appendRequired('isValidId')
TidyHTMLValidator = ValidationChain('isTidyHtmlChain')
#TidyHTMLValidator.appendSufficient('isEmpty')
TidyHTMLValidator.appendRequired('isTidyHtmlWithCleanup')
URLValidator = ValidationChain('isURL')
URLValidator.appendSufficient('isEmptyNoError')
URLValidator.appendRequired('isURL')
RequiredURLValidator = ValidationChain('isRequiredURL')
RequiredURLValidator.appendRequired('isURL')
EmailValidator = ValidationChain('isEmailChain')
EmailValidator.appendSufficient('isEmptyNoError')
EmailValidator.appendRequired('isEmail')
PhoneValidator = ValidationChain('isPhoneChain')
PhoneValidator.appendSufficient('isEmptyNoError')
PhoneValidator.appendRequired('isInternationalPhoneNumber')
