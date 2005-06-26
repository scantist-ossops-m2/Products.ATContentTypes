#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""AT Content Types general interface


"""
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Interface import Interface, Attribute

class IATContentType(Interface):
    """Marker interface for AT Content Types
    """

    default_view = Attribute('''Default view template - used for TemplateMixin''')
    suppl_views = Attribute('''Supplementary views - used for TemplateMixin''')

    _atct_newTypeFor = Attribute('''Used to get the meta type of the original implementation''')

    typeDescription = Attribute('''A short description used for the edit screen''')
    typeDescMsgId = Attribute('''The i18n msgid of the type description''')

    assocMimetypes = Attribute('''A tuple of mimetypes that are associated
                                  with this type. Format: ('bar/foo', 'foo/*',)
                               ''')

    assocFileExt = Attribute('''A tuple of file extensions that are associated
                                with this type. Format: ('jpeg', 'png',)
                             ''')

    cmf_edit_kws = Attribute('''List of keyword names.
    
    If one of this kw names is used with edit() then the cmf_edit method is
    called.
    ''')

    def getLayout(**kw):
        """Get the current layout or the default layout if the current one is None
        """

    def getDefaultLayout():
        """Get the default layout used for TemplateMixin
        """