#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
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
"""


"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from DateTime import DateTime

from Products.ATContentTypes.config import HAS_PLONE2

from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import MetadataSchema
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget

from Products.CMFCore import CMFCorePermissions

from Products.ATContentTypes import permission as ATCTPermissions

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

# for ATContentTypes we want to have the description in the edit view
# just like CMF
ATContentTypeSchema = BaseSchema.copy() + Schema((
    ReferenceField('relatedItems',
        relationship = 'relatesTo', 
        multiValued = True,
        isMetadata = True,
        languageIndependent = False,
        index = 'KeywordIndex',
        write_permission = CMFCorePermissions.ModifyPortalContent,
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = True,

            label = "Related Item(s)",
            label_msgid = "label_related_items",
            description = " ",
            description_msgid = "help_related_items",
            i18n_domain = "plone",
            visible={'view' : 'hidden',
                     #'edit' : ENABLE_RELATED_ITEMS and 'visible' or 'hidden'
                    },
            )
        ),
    ),) + MetadataSchema((
    BooleanField('excludeFromNav',
        required = False,
        languageIndependent = True,
        schemata = 'metadata', # moved to 'default' for folders
        widget = BooleanWidget(
            description="If selected, this item will not appear in the navigation tree",
            description_msgid = "help_exclude_from_nav",
            label = "Exclude from navigation",
            label_msgid = "label_exclude_from_nav",
            i18n_domain = "plone",
            visible={'view' : 'hidden',
                     'edit' : 'visible'},
            ),
        ),
    ),)
    
ATContentTypeSchema['id'].validators = ('isValidId',)
ATContentTypeSchema['id'].searchable = True
ATContentTypeSchema['id'].widget.macro = 'zid'
ATContentTypeSchema['description'].schemata = 'default'

# BBB
ATContentTypeBaseSchema = ATContentTypeSchema

urlUploadField = StringField('urlUpload',
        required = False,
        mode = 'w', # write only field
        languageIndependent = True,
        validators = ('isURL',),
        write_permission = ATCTPermissions.UploadViaURL,
        widget = StringWidget(
            description="Upload a file from another server by url.",
            description_msgid = "help_upload_url",
            label = "Upload from server",
            label_msgid = "label_upload_url",
            i18n_domain = "plone",
            visible={'view' : 'hidden',
                     'edit' : 'hidden'},
            ),
        )
        
def finalizeATCTSchema(schema, folderish=False, moveDiscussion=True):
    """Finalizes an ATCT type schema to alter some fields
    """
    schema.moveField('relatedItems', pos='bottom')
    #if not HAS_PLONE2:
    #    del schema['excludeFromNav']
    
    if folderish:
        schema['excludeFromNav'].schemata = 'default'
        schema.moveField('excludeFromNav', after='relatedItems')
    else:
        schema.moveField('excludeFromNav', after='allowDiscussion')
    if moveDiscussion:
        schema['allowDiscussion'].schemata = 'default'
        schema.moveField('allowDiscussion', pos='bottom')
    return schema


__all__ = ('ATContentTypeSchema', 'relatedItemsField',)