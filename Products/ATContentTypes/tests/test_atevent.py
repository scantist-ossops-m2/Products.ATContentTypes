#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
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

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

import transaction
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit

from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.migration.atctmigrator import EventMigrator
from Products.CMFCalendar.Event import Event
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import EmailValidator
from Products.ATContentTypes.tests.utils import NotRequiredTidyHTMLValidator
from Products.ATContentTypes.permission import ChangeEvents
from Products.ATContentTypes.utils import DT2dt
from DateTime import DateTime
from Products.ATContentTypes.interfaces import ICalendarSupport
from Products.ATContentTypes.interfaces import IATEvent
from Interface.Verify import verifyObject

# z3 imports
from Products.ATContentTypes.interface import ICalendarSupport as Z3ICalendarSupport
from Products.ATContentTypes.interface import IATEvent as Z3IATEvent
from zope.interface.verify import verifyObject as Z3verifyObject


LOCATION = 'my location'
EV_TYPE  = 'Meeting'
EV_URL   = 'http://example.org/'
S_DATE   = DateTime()
E_DATE   = DateTime()+1
C_NAME   = 'John Doe'
C_PHONE  = '+1212356789'
C_EMAIL  = 'john@example.org'
EV_ATTENDEES = ('john@doe.com',
                'john@doe.org',
                'john@example.org')
TEXT = "lorem ipsum"

def editCMF(obj):
    dcEdit(obj)
    obj.setStartDate(S_DATE)
    obj.setEndDate(E_DATE)
    obj.location=LOCATION
    obj.contact_name=C_NAME
    obj.contact_email=C_EMAIL
    obj.contact_phone=C_PHONE
    obj.event_url=EV_URL
    obj.setSubject((EV_TYPE,))

def editATCT(obj):
    dcEdit(obj)
    obj.setLocation(LOCATION)
    obj.setEventType(EV_TYPE)
    obj.setEventUrl(EV_URL)
    obj.setStartDate(S_DATE)
    obj.setEndDate(E_DATE)
    obj.setContactName(C_NAME)
    obj.setContactPhone(C_PHONE)
    obj.setContactEmail(C_EMAIL)
    obj.setAttendees(EV_ATTENDEES)
    obj.setText(TEXT)


tests = []

class TestSiteATEvent(atcttestcase.ATCTTypeTestCase):

    klass = ATEvent
    portal_type = 'Event'
    cmf_portal_type = 'CMF Event'
    cmf_klass = Event
    title = 'Event'
    meta_type = 'ATEvent'
    icon = 'event_icon.gif'

    def test_doesImplementCalendarSupport(self):
        self.failUnless(ICalendarSupport.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(ICalendarSupport, self._ATCT))

    def test_doesImplementZ3CalendarSupport(self):
        iface = Z3ICalendarSupport
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATEvent(self):
        iface = IATEvent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3ATEvent(self):
        iface = Z3IATEvent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))

        self.failUnless(old.location == new.getLocation(), 'Location mismatch: %s / %s' \
                        % (old.location, new.getLocation()))
        self.failUnless(old.Subject() == new.getEventType(), 'EventType mismatch: %s / %s' \
                        % (old.Subject(), new.getEventType()))
        self.failUnless(old.event_url == new.event_url(), 'EventUrl mismatch: %s / %s' \
                        % (old.event_url, new.event_url()))
        self.failUnless(old.start() == new.start(), 'Start mismatch: %s / %s' \
                        % (old.start(), new.start()))
        self.failUnless(old.end() == new.end(), 'End mismatch: %s / %s' \
                        % (old.end(), new.end()))
        self.failUnless(old.contact_name == new.contact_name(), 'contact_name mismatch: %s / %s' \
                        % (old.contact_name, new.contact_name()))
        self.failUnless(old.contact_phone == new.contact_phone(), 'contact_phone mismatch: %s / %s' \
                        % (old.contact_phone, new.contact_phone()))
        self.failUnless(old.contact_email == new.contact_email(), 'contact_email mismatch: %s / %s' \
                        % (old.contact_email, new.contact_email()))
        self.assertEquals(new.start_date, DT2dt(new.start()))
        self.assertEquals(new.end_date, DT2dt(new.end()))
        self.assertEquals(new.start_date, DT2dt(S_DATE))
        self.assertEquals(new.end_date, DT2dt(E_DATE))
        self.assertEquals(new.duration, new.end_date - new.start_date)

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        start = old.start()
        end   = old.end()
        location = old.location
        c_name = old.contact_name
        c_email = old.contact_email
        c_phone = old.contact_phone
        ev_url = old.event_url
        ev_type = old.Subject()

        # migrated (needs subtransaction to work)
        transaction.savepoint(optimistic=True)
        m = EventMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        self.failUnless(migrated.location == location,
                        'Location mismatch: %s / %s' %
                        (migrated.location, location))
        self.failUnless(migrated.Subject() == ev_type,
                        'EventType mismatch: %s / %s' %
                        (migrated.Subject(), ev_type))
        self.failUnless(migrated.event_url() == ev_url,
                        'EventUrl mismatch: %s / %s' %
                        (migrated.event_url(), ev_url))
        self.failUnless(migrated.start() == start,
                        'Start mismatch: %s / %s' %
                        (migrated.start(), start))
        self.failUnless(migrated.end() == end,
                        'End mismatch: %s / %s' % (migrated.end(), end))
        self.failUnless(migrated.contact_name() == c_name,
                        'contact_name mismatch: %s / %s' %
                        (migrated.contact_name(), c_name))
        self.failUnless(migrated.contact_phone() == c_phone,
                        'contact_phone mismatch: %s / %s' %
                        (migrated.contact_phone(), c_phone))
        self.failUnless(migrated.contact_email() == c_email,
                        'contact_email mismatch: %s / %s' %
                        (migrated.contact_email(), c_email))
        self.failUnless(migrated.getAttendees() == (),
                        'attendees mismatch: %s / %s' %
                        (migrated.getAttendees(), ()))

    def test_cmp(self):
        e1 = self._ATCT
        e2 = self._createType(self.folder, self.portal_type, 'e2')
        day29 = DateTime('2004-12-29 0:00:00')
        day30 = DateTime('2004-12-30 0:00:00')
        day31 = DateTime('2004-12-31 0:00:00')

        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day30, title='event')
        self.failUnlessEqual(cmp(e1, e2), 0)

        # start date
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day30, endDate=day31, title='event')
        self.failUnlessEqual(cmp(e1, e2), -1) # e1 < e2

        # duration
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day31, title='event')
        self.failUnlessEqual(cmp(e1, e2), -1)  # e1 < e2

        # title
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day30, title='evenz')
        self.failUnlessEqual(cmp(e1, e2), -1)  # e1 < e2

    def test_ical(self):
        event = self._ATCT
        event.setStartDate(DateTime('2001/01/01 12:00:00 GMT+1'))
        event.setEndDate(DateTime('2001/01/01 14:00:00 GMT+1'))
        event.setTitle('cool event')
        ical = event.getICal()
        lines = ical.split('\n')
        self.assertEqual(lines[0], "BEGIN:VEVENT")
        self.assertEqual(lines[5], "SUMMARY:%s"%event.Title())
        # times should be converted to UTC
        self.assertEqual(lines[6], "DTSTART:20010101T110000Z")
        self.assertEqual(lines[7], "DTEND:20010101T130000Z")

    def test_vcal(self):
        event = self._ATCT
        event.setStartDate(DateTime('2001/01/01 12:00:00 GMT+1'))
        event.setEndDate(DateTime('2001/01/01 14:00:00 GMT+1'))
        event.setTitle('cool event')
        vcal = event.getVCal()
        lines = vcal.split('\n')
        self.assertEqual(lines[0], "BEGIN:VEVENT")
        self.assertEqual(lines[7], "SUMMARY:%s"%event.Title())
        # times should be converted to UTC
        self.assertEqual(lines[1], "DTSTART:20010101T110000Z")
        self.assertEqual(lines[2], "DTEND:20010101T130000Z")

    def test_get_size(self):
        atct = self._ATCT
        editATCT(atct)
        self.failUnlessEqual(atct.get_size(), len(TEXT))

tests.append(TestSiteATEvent)

class TestATEventFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATEvent)

    def test_locationField(self):
        dummy = self._dummy
        field = dummy.getField('location')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getLocation',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setLocation',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_eventTypeField(self):
        dummy = self._dummy
        field = dummy.getField('eventType')
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == (), 'Value is %s' % str(str(field.default)))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getEventType',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setEventType',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'lines', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, KeywordWidget),
                        'Value is %s' % id(field.widget))


    def test_eventUrlField(self):
        dummy = self._dummy
        field = dummy.getField('eventUrl')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'event_url',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setEventUrl',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_startDateField(self):
        dummy = self._dummy
        field = dummy.getField('startDate')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == None , 'Value is %s' % str(field.default))
        self.failUnless(field.default_method == DateTime , 'Value is %s' % str(field.default_method))
        self.failUnless(field.searchable == False, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'start',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setStartDate',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'datetime', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, CalendarWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))


    def test_endDateField(self):
        dummy = self._dummy
        field = dummy.getField('endDate')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == None , 'Value is %s' % str(field.default))
        self.failUnless(field.default_method == DateTime , 'Value is %s' % str(field.default_method))
        self.failUnless(field.searchable == False, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'end',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setEndDate',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'datetime', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, CalendarWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactNameField(self):
        dummy = self._dummy
        field = dummy.getField('contactName')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'contact_name',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setContactName',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactEmailField(self):
        dummy = self._dummy
        field = dummy.getField('contactEmail')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'contact_email',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setContactEmail',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == EmailValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactPhoneField(self):
        dummy = self._dummy
        field = dummy.getField('contactPhone')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'contact_phone',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setContactPhone',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_attendeesField(self):
        dummy = self._dummy
        field = dummy.getField('attendees')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == (), 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getAttendees',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setAttendees',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ChangeEvents,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'lines', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(isinstance(field.widget, LinesWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_textField(self):
        dummy = self._dummy
        field = dummy.getField('text')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getText',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setText',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'text', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == NotRequiredTidyHTMLValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)
        self.failUnless(field.default_content_type == 'text/html',
                        'Value is %s' % field.default_content_type)
        self.failUnless(field.default_output_type == 'text/x-html-safe',
                        'Value is %s' % field.default_output_type)
        self.failUnless('text/html' in field.allowable_content_types)
        self.failUnless('text/structured'  in field.allowable_content_types)

    def beforeTearDown(self):
        # more
        atcttestcase.ATCTFieldTestCase.beforeTearDown(self)

tests.append(TestATEventFields)

class TestATEventFunctional(atctftestcase.ATCTIntegrationTestCase):

    portal_type = 'Event'
    views = ('event_view', 'vcs_view', 'ics_view', )

tests.append(TestATEventFunctional)


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
