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
from itools.catalog import EqQuery
from itools.datatypes import Email, String
from itools.stl import stl
from itools.web import FormError

# Import from ikaaro
from ikaaro.registry import register_object_class
from ikaaro.root import Root as BaseRoot
from ikaaro.website import WebSite

# Import from hforge
from news import News


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



class Root(BaseRoot):
    class_id = 'hforge.org'
    class_title = 'HForge'
    class_skin = 'ui/hforge'

    browse_content__access__ = 'is_allowed_to_edit'
    last_changes__access__ = 'is_allowed_to_edit'


    GET__access__ = True
    def GET(self, context):
        return context.uri.resolve2(';view')


    view__access__ = True
    view__label__ = u'View'
    view__title__ = u'View'
    def view(self, context):
        root = context.root
        # Find documents
        query = EqQuery('format', News.class_id)
        results = context.root.search(query)
        documents = results.get_documents(sort_by='date', reverse=True)
        # Browse metadatas
        lines = []
        for news in documents:
            if news.workflow_state == 'public':
                line = {}
                line['title'] = news.title
                year, month, day = news.date.split('-')
                date_object = date(int(year), int(month), int(day))
                format = format_date(date_object.day)
                formated_date = date_object.strftime(format)
                line['date'] = formated_date
                handler = root.get_object(news.abspath).handler
                html = handler.events
                line['html'] = html
                lines.append(line)
        namespace = {'objects': lines}
        template = self.get_object('/ui/hforge/Root_view.xml')
        return stl(template, namespace)


    projects__access__ = True
    projects__label__ = u'Projects'
    projects__title__ = u'Projects'
    def projects(self, context):
        # Search
        projects = [
            {'url': x.name,
             'title': x.get_property('title'),
             'description': x.get_property('description')}
            for x in self.search_objects(object_class=WebSite)
        ]

        # Sort
        projects.sort(lambda x, y: cmp(x['title'].lower(), y['title'].lower()))

        namespace = {}
        namespace['projects'] = projects

        template = self.get_object('/ui/hforge/Root_projects.xml')
        return stl(template, namespace)


    subscribe__access__ = True
    def subscribe(self, context):
        # Check form data
        schema = {'email': Email(mandatory=True),
                  'list': String(mandatory=True)}
        try:
            form = context.check_form_input(schema)
        except FormError, error:
            messages = []
            if 'email' in error.missing:
                messages.append('Please type your email address.')
            elif 'email' in error.invalid:
                messages.append('Please type a valid email address.')
            if 'list' in error.missing:
                message = 'Please select the mailing list you want to join.'
                messages.append(message)

            namespace = {'messages': messages}

            handler = self.get_object('/ui/hforge/subscribe_error.xml')
            return stl(handler, namespace)

        # Subscribe
        email = form['email']
        to_addr = '%s-subscribe-%s@hforge.org' % (form['list'],
                                                  email.replace('@', '='))
        context.root.send_email(to_addr, u'Subscribe', email,
                                subject_with_host=False)

        handler = self.get_object('/ui/hforge/subscribe_ok.xml')
        return stl(handler)



###########################################################################
# Register
###########################################################################
register_object_class(Root)
