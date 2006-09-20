##############################################################################
#
# ATContentTypes http://plone.org/products/atcontenttypes/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2006 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Topic:

"""

__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATSimpleIntCriterion'

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import DisplayList

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import LIST_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

DirectionOperations = DisplayList((
                    ('', 'Equal to')
                  , ('min', 'Greater than')
                  , ('max', 'Less than')
                  , ('min:max', 'Between')
    ))

ATSimpleIntCriterionSchema = ATBaseCriterionSchema + Schema((
    IntegerField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default=None,
                widget=IntegerWidget(
                    label="Value",
                    label_msgid="label_int_criteria_value",
                    description="An integer number.",
                    description_msgid="help_int_criteria_value",
                    i18n_domain="atcontenttypes"),
                ),
    IntegerField('value2',
                required=0,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value2",
                mutator="setValue2",
                default=None,
                widget=IntegerWidget(
                    label="Second Value",
                    label_msgid="label_int_criteria_value2",
                    description="An integer number used as the maximum value if the between direction is selected.",
                    description_msgid="help_int_criteria_value2",
                    i18n_domain="atcontenttypes"),
                ),
    StringField('direction',
                required=0,
                mode="rw",
                write_permission=ChangeTopics,
                default='',
                vocabulary=DirectionOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                    label="Direction",
                    label_msgid="label_int_criteria_direction",
                    description="Specify whether you want to find values lesser than, greater than, equal to, or between the chosen value(s).",
                    description_msgid="help_int_criteria_direction",
                    i18n_domain="atcontenttypes"),
                ),
    ))

class ATSimpleIntCriterion(ATBaseCriterion):
    """A simple int criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSimpleIntCriterionSchema
    meta_type      = 'ATSimpleIntCriterion'
    archetype_name = 'Simple Int Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'Integer value or range'

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        val = self.Value()
        direction = self.getDirection()
        if val or val == 0:
            if direction == 'min:max':
                val = tuple([int(val), int(self.Value2())])
            else:
                val = int(val)
            if direction:
                result.append((self.Field(), {'query': val,  'range': direction}))
            else:
                result.append((self.Field(), {'query': val}))

        return tuple(result)

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST, errors):
        """Check that Value2 is set if range is set to min:max"""
        direction = REQUEST.get('direction', self.getDirection())
        val2 = REQUEST.get('value2', self.Value2())
        if direction == 'min:max' and not val2 and not val2 == 0:
            errors['value2']='You must enter a second value to do a "Between" search.'
        errors['value2']='You must enter a second value to do a "Between" search.'
        return errors
        

registerCriterion(ATSimpleIntCriterion, LIST_INDICES)
