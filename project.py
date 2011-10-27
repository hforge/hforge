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
from ikaaro.blog import Blog
from ikaaro.website import WebSite
from ikaaro.website_views import UpdateDocs as Project_UpdateDocs


class Project(WebSite):

    class_id = 'project'
    class_title = MSG(u'Project')
    class_views = WebSite.class_views + ['update_docs']
    __fixed_handlers__ = WebSite.__fixed_handlers__ + ['news']


    def init_resource(self, **kw):
        super(Project, self).init_resource(**kw)
        self.make_resource('news', Blog)

    update_docs = Project_UpdateDocs()
