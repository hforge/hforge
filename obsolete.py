# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Matthieu France <matthieu.france@itaapy.com>
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

# Import from ikaaro
from ikaaro.blog.blog import Blog, Post


class News(Post):

    class_id = 'news'
    class_version = '20100708'


    def update_20100708(self):
        self.metadata.set_changed()
        self.metadata.format = 'blog-post'



class NewsFolder(Blog):

    class_id = 'news-folder'
    class_version = '20100708'


    def update_20100708(self):
        self.metadata.set_changed()
        self.metadata.format = 'blog'
