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
from itools.catalog import KeywordField
from itools.datatypes import Date, DateTime, Unicode
from itools.handlers import checkid
from itools.stl import stl
from itools.xml import XMLError, XMLParser

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.forms import DateWidget
from ikaaro.html import WebPage
from ikaaro.messages import *
from ikaaro.registry import register_object_class


###########################################################################
# News
###########################################################################
class News(WebPage):
    class_id = 'news'
    class_title = u'News'
    class_description = u'Create and publich News'
    class_views = [['view'],
                   ['edit_form'],
                   ['state_form'],
                   ['history_form']]


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
        namespace = {}
        namespace['action'] = ';new_resource'
        namespace['submit'] = u'Add'
        get = context.get_form_value
        namespace['title'] = get('title', type=Unicode)
        namespace['html'] = root.get_rte(context, 'html', None,
                                         template='/ui/hforge/rte.xml')
        widget = DateWidget('date')
        release_date = get('date', date.today().isoformat(), type=Date)
        namespace['date'] = widget.to_html(Date, release_date)
        namespace['class_id'] = cls.class_id
        namespace['class_title'] = cls.gettext(cls.class_title)
        namespace['timestamp'] = DateTime.encode(datetime.now())
        template = root.get_object('/ui/hforge/News_edit.xml')
        return stl(template, namespace)


    @staticmethod
    def new_instance(cls, container, context):
        get = context.get_form_value
        title = get('title', type=Unicode)
        html = get('html')
        release_date = get('date', type=Date)

        # Check the name
        name = title.strip()
        if not name:
            return context.come_back(MSG_NAME_MISSING)

        name = checkid(name)
        if name is None:
            return context.come_back(MSG_BAD_NAME)

        # Check the name is free
        if container.has_object(name):
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


    view__access__ = 'is_allowed_to_view'
    view__label__ = u'View'
    view__title__ = u'View'
    def view(self, context):
        language = self.get_content_language(context)
        namespace = {}
        namespace['title'] = self.get_property('title', language=language)
        namespace['html'] = self.handler.events
        namespace['date'] = self.get_property('date')
        template = self.get_object('/ui/hforge/News_view.xml')
        return stl(template, namespace)


    edit_form__access__ = 'is_allowed_to_edit'
    edit_form__label__ = u'Edit'
    edit_form__icon__ = 'edit.png'
    def edit_form(self, context):
        language = self.get_content_language(context)
        namespace = {}
        namespace['action'] = ';edit'
        namespace['submit'] = u'Change'
        namespace['title'] = self.get_property('title', language=language)
        widget = DateWidget('date')
        release_date = self.get_property('date')
        namespace['date'] = widget.to_html(Date, release_date)
        namespace['html'] = \
            self.get_rte(context, 'html',
                         self.handler.events,
                         template='/ui/hforge/rte.xml')
        namespace['class_id'] = self.class_id
        namespace['class_title'] = self.class_title
        namespace['timestamp'] = DateTime.encode(datetime.now())

        template = self.get_object('/ui/hforge/News_edit.xml')
        return stl(template, namespace)


    edit__access__ = 'is_allowed_to_edit'
    def edit(self, context, sanitize=False):
        get = context.get_form_value
        # Timestamp
        timestamp = get('timestamp', type=DateTime)
        if timestamp is None:
            return context.come_back(MSG_EDIT_CONFLICT)
        document = self.get_epoz_document()
        if document.timestamp is not None and timestamp < document.timestamp:
            return context.come_back(MSG_EDIT_CONFLICT)
        # Metadata
        title = get('title', type=Unicode)
        if not title.strip():
            return context.come_back(MSG_NAME_MISSING)
        release_date = get('date', type=Date)
        html = get('html')
        language = self.get_content_language(context)
        self.set_property('title', title, language=language)
        self.set_property('date', release_date)
        # Body
        try:
            self.handler.events = list(XMLParser(html))
        except XMLError:
            return context.come_back(u'Invalid HTML code.')
        return context.come_back(MSG_CHANGES_SAVED)



###########################################################################
# Register
###########################################################################
register_object_class(News)
Folder.register_document_type(News)
