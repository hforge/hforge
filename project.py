# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from itools
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_document_type
from ikaaro.website import WebSite

# Import from hforge
from news import NewsFolder


class Project(WebSite):

    class_id = 'project'
    class_title = MSG(u'Project')
    __fixed_handlers__ = WebSite.__fixed_handlers__ + ['news']

    @staticmethod
    def _make_resource(cls, folder, name, **kw):
        WebSite._make_resource(cls, folder, name, **kw)
        # Add the news folder
        metadata = NewsFolder.build_metadata()
        folder.set_handler('%s/news.metadata' % name, metadata)



# Register
register_resource_class(Project)
register_document_type(Project, WebSite.class_id)
