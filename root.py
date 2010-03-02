# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from the Standard Library
from datetime import date

# Import from itools
from itools.datatypes import Email, String
from itools.gettext import MSG
from itools.stl import stl
from itools.web import FormError, STLView, BaseForm
from itools.xapian import AndQuery, PhraseQuery

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.root import Root as BaseRoot
from ikaaro.website import WebSite

# Import from hforge
from news import News, NewsFolder
from project import Project


###########################################################################
# Views
###########################################################################
def format_date(day):
    if day > 3 and day < 14:
        return '%b %dth %Y'
    indicator = day % 10
    if indicator == 1:
        return '%b %dst %Y'
    elif indicator == 2:
        return '%b %dnd %Y'
    elif indicator == 3:
        return '%b %drd %Y'
    else:
        return '%b %dth %Y'


class Root_View(STLView):

    access = True
    title = MSG(u'View')
    template = '/ui/hforge/Root_view.xml'

    n_news = 3

    def get_namespace(self, resource, context):
        # Search news
        query = AndQuery(
            PhraseQuery('format', News.class_id),
            PhraseQuery('workflow_state', 'public'))
        results = resource.search(query)
        documents = results.get_documents(sort_by='date', reverse=True,
                                          size=self.n_news)
        # Browse metadatas
        lines = []
        for news in documents:
            year, month, day = news.date.split('-')
            date_object = date(int(year), int(month), int(day))
            format = format_date(date_object.day)
            formated_date = date_object.strftime(format)
            html = resource.get_resource(news.abspath).handler.events
            lines.append({
                'title': news.title, 'date': formated_date, 'html': html})
        # Ok
        return {'objects': lines}



class Root_News(Root_View):

    title = MSG(u'News')
    template = '/ui/hforge/Root_news.xml'

    n_news = 0



class Root_Projects(STLView):

    access = True
    title = MSG(u'Projects')
    template = '/ui/hforge/Root_projects.xml'


    def get_page_title(self, resource, context):
        return self.title


    def get_namespace(self, resource, context):
        # Search
        projects = [
            {'url': x.name,
             'title': x.get_property('title'),
             'description': x.get_property('description')}
            for x in resource.search_resources(cls=WebSite)
        ]
        # Sort
        projects.sort(lambda x, y: cmp(x['title'].lower(), y['title'].lower()))
        # Ok
        return {'projects': projects}



class Root_Subscribe(BaseForm):

    access = True
    schema = {
        'email': Email(mandatory=True),
        'list': String(mandatory=True)}


    def GET(self, resource, context):
        # FIXME
        if context.message:
            return context.come_back(context.message)

        # Ok
        template = '/ui/hforge/subscribe_ok.xml'
        handler = resource.get_resource(template)
        return stl(handler)


    def action(self, resource, context, form):
        email = form['email']

        to_addr = '%s-subscribe-%s@hforge.org'
        to_addr = to_addr % (form['list'], email.replace('@', '='))

        root = resource
        root.send_email(to_addr, u'Subscribe', email, subject_with_host=False)



###########################################################################
# Resource
###########################################################################
class Root(Project, BaseRoot):

    class_id = 'hforge.org'
    class_version = '20090116'
    class_title = MSG(u'HForge')
    class_skin = 'ui/hforge'
    __fixed_handlers__ = BaseRoot.__fixed_handlers__ + ['news']


    @staticmethod
    def _make_resource(cls, folder, email, password):
        root = BaseRoot._make_resource(cls, folder, email, password)
        # Add the news folder
        metadata = NewsFolder.build_metadata()
        folder.set_handler('news.metadata', metadata)
        return root


    def get_page_title(self):
        return None

    # Restrict access to the folder's views
    browse_content = Folder_BrowseContent(access='is_allowed_to_edit')

    # Custom Views
    view = Root_View()
    news = Root_News()
    projects = Root_Projects()
    subscribe = Root_Subscribe()

