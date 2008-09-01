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

# Import from the Standard Library
from datetime import date, datetime

# Import from itools
from itools.datatypes import Date, DateTime, String, Unicode
from itools.handlers import checkid
from itools.gettext import MSG
from itools.stl import stl
from itools.web import STLView, STLForm
from itools.xapian import KeywordField
from itools.xml import XMLError, XMLParser

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.forms import DateWidget
from ikaaro.html import WebPage
from ikaaro.messages import *
from ikaaro.registry import register_object_class



###########################################################################
# Views
###########################################################################
class NewsView(STLView):

    access = 'is_allowed_to_view'
    title = MSG(u'View')
    template = '/ui/hforge/News_view.xml'

    def get_namespace(self, resource, context):
        language = resource.get_content_language(context)
        return {
            'title': resource.get_property('title', language=language),
            'html': resource.handler.events,
            'date': resource.get_property('date'),
        }



class NewsEdit(STLForm):

    access = 'is_allowed_to_edit'
    title = MSG(u'Edit')
    template = '/ui/hforge/News_edit.xml'
    schema = {
        'timestamp': DateTime,
        'title': Unicode(mandatory=True),
        'date': Date,
        'html': String,
    }

    def get_namespace(self, resource, context):
        language = resource.get_content_language(context)
        widget = DateWidget('date')
        release_date = resource.get_property('date')

        return {
            'action': ';edit',
            'submit': MSG(u'Change'),
            'title': resource.get_property('title', language=language),
            'date': widget.to_html(Date, release_date),
            'html': resource.get_rte(context, 'html', resource.handler.events,
                                     template='/ui/hforge/rte.xml'),
            'class_id': resource.class_id,
            'class_title': resource.class_title,
            'timestamp': DateTime.encode(datetime.now()),
        }


    def action(self, resource, context, form):
        # Check the timestamp
        timestamp = form['timestamp']
        if timestamp is None:
            context.message = MSG_EDIT_CONFLICT
            return
        document = resource.get_epoz_document()
        if document.timestamp is not None and timestamp < document.timestamp:
            context.message = MSG_EDIT_CONFLICT
            return
        # Check the html is good
        html = form['html']
        try:
            html = list(XMLParser(html))
        except XMLError:
            context.message = MSG(u'Invalid HTML code.')
            return

        # Title
        title = form['title']
        language = resource.get_content_language(context)
        resource.set_property('title', title, language=language)
        # Date
        release_date = form['date']
        resource.set_property('date', release_date)
        # Body
        resource.handler.events = html

        # Ok
        context.message = MSG_CHANGES_SAVED


###########################################################################
# Resource
###########################################################################
class News(WebPage):

    class_id = 'news'
    class_title = MSG(u'News')
    class_description = MSG(u'Create and publich News')
    class_views = ['view', 'edit', 'state_form', 'history_form']


    @classmethod
    def get_metadata_schema(cls):
        schema = WebPage.get_metadata_schema()
        schema['date'] = Date
        return schema


    def get_catalog_fields(self):
        base_fields = WebPage.get_catalog_fields(self)
        field = KeywordField('date', is_stored=True)
        base_fields.append(field)
        return base_fields


    def get_catalog_values(self):
        indexes = WebPage.get_catalog_values(self)
        indexes['date'] = self.get_property('date').isoformat()
        return indexes


    @staticmethod
    def new_instance_form(cls, context):
        root = context.root
        # Build the namespace
        default = date.today().isoformat()
        release_date = context.get_form_value('date', Date, default=default)
        namespace = {
            'action': ';new_resource',
            'submit': MSG(u'Add'),
            'title': context.get_form_value('title', Unicode),
            'html': root.get_rte(context, 'html', None,
                                 template='/ui/hforge/rte.xml'),
            'date': DateWidget('date').to_html(Date, release_date),
            'class_id': cls.class_id,
            'class_title': cls.class_title.gettext(),
            'timestamp': DateTime.encode(datetime.now()),
        }

        template = root.get_resource('/ui/hforge/News_edit.xml')
        return stl(template, namespace)


    @staticmethod
    def new_instance(cls, container, context):
        title = context.get_form_value('title', Unicode)
        html = context.get_form_value('html')
        release_date = context.get_form_value('date', Date)

        # Check the name
        name = title.strip()
        if not name:
            return context.come_back(MSG_NAME_MISSING)

        name = checkid(name)
        if name is None:
            return context.come_back(MSG_BAD_NAME)

        # Check the name is free
        if container.has_resource(name):
            return context.come_back(MSG_NAME_CLASH)

        # Make Object
        language = container.get_content_language(context)
        object = cls.make_object(cls, container, name, body=html,
                                 language=language)
        metadata = object.metadata
        metadata.set_property('title', title, language=language)
        metadata.set_property('date', release_date)

        goto = './%s/;%s' % (name, object.get_firstview())
        return context.come_back(MSG_NEW_RESOURCE, goto=goto)


    view = NewsView()
    edit = NewsEdit()


###########################################################################
# Register
###########################################################################
register_object_class(News)
Folder.register_document_type(News)
