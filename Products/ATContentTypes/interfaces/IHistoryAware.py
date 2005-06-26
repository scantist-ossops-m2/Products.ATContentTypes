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
"""History awareness marker interface


"""
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Interface import Interface

class IHistoryAware(Interface):
    """History awareness marker interface
    """

    def getHistorySource():
        """get source for HistoryAwareMixin

        Must return a (raw) string
        """

    def getHistories(max=10):
        """Get a list of historic revisions.

        Returns metadata as well
        (object, time, transaction_note, user)
        """

    def getLastEditor():
        """Returns the user name of the last editor.

        Returns None if no last editor is known.
        """

    def getDocumentComparisons(max=10, filterComment=0):
        """Get history as unified diff
        """