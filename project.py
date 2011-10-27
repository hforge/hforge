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
from itools.datatypes import String
from itools.fs import FileName
from itools.gettext import MSG
from itools.handlers import get_handler_class_by_mimetype
from itools.html import XHTMLFile
from itools.stl import rewrite_uris
from itools.uri import get_reference
from itools.web import FormError
from itools.xml import get_element, TEXT

# Import from ikaaro
from ikaaro.autoform import AutoForm, FileWidget, TextWidget
from ikaaro.buttons import Button
from ikaaro.blog import Blog
from ikaaro.datatypes import FileDataType
from ikaaro.folder import Folder
from ikaaro.messages import MSG_UNEXPECTED_MIMETYPE
from ikaaro.website import WebSite



class Project_UpdateDocs(AutoForm):

    access = 'is_admin'
    title = MSG(u'Update docs')

    schema = {
        'file': FileDataType(mandatory=True),
        'language': String(mandatory=True, default='en')}
    widgets = [
        FileWidget('file', title=MSG(u'File')),
        TextWidget('language', title=MSG(u'Language'),
            tip=MSG(u'"en", "fr", ...'))]

    actions = [
        Button(access='is_admin', css='button-ok', title=MSG(u'Upload'))]


    def _get_form(self, resource, context):
        form = super(Project_UpdateDocs, self)._get_form(resource, context)
        # Check the mimetype
        filename, mimetype, body = form['file']
        if mimetype not in ('application/x-tar', 'application/zip'):
            raise FormError, MSG_UNEXPECTED_MIMETYPE(mimetype=mimetype)

        return form


    def action(self, resource, context, form):
        skip = set(['application/javascript', 'application/octet-stream',
                    'text/css', 'text/plain'])
        keep = set(['application/pdf', 'image/png'])
        language = form['language']

        def rewrite(value):
            if value[0] == '#':
                return value
            ref = get_reference(value)
            if ref.scheme:
                return value
            name = ref.path.get_name()
            name, extension, langage = FileName.decode(name)
            if extension in ('png', 'pdf'):
                name = '%s/;download' % name
            ref.path[-1] = name
            return '../%s' % ref

        def filter(path, mimetype, body):
            # HTML
            if mimetype == 'text/html':
                source = XHTMLFile(string=body)
                target = XHTMLFile()
                elem = get_element(source.events, 'div', **{'class': 'body'})
                if not elem:
                    print 'E', path
                    return None
                elements = elem.get_content_elements()
                elements = rewrite_uris(elements, rewrite)
                elements = list(elements)
                target.set_body(elements)
                return target.to_str()
            # Skip
            elif mimetype in skip:
                return None
            # Keep
            elif mimetype in keep:
                return body
            # Unknown
            else:
                print 'X', path, mimetype
                return body

        def postproc(file):
            # State
            file.set_property('state', 'public')
            # Title
            if file.class_id != 'webpage':
                return
            handler = file.get_handler()
            events = handler.events
            elem = get_element(events, 'h1')
            if elem:
                title = [
                    unicode(x[1], 'utf8')
                    for x in elem.get_content_elements() if x[0] == TEXT ]
                if title[-1] == u'¶':
                    title.pop()
                title = u''.join(title)
                file.set_property('title', title, language)
                handler.events = events[:elem.start] + events[elem.end+1:]

        # 1. Make the '/docs/' folder
        docs = resource.get_resource('docs', soft=True)
        if not docs:
            docs = resource.make_resource('docs', Folder)
        # 2. Extract
        filename, mimetype, body = form['file']
        cls = get_handler_class_by_mimetype(mimetype)
        handler = cls(string=body)
        docs.extract_archive(handler, language, filter, postproc, True)

        # Ok
        message = MSG(u'Documentation updated.')
        return context.come_back(message, goto='./docs')



class Project(WebSite):

    class_id = 'project'
    class_title = MSG(u'Project')
    class_views = WebSite.class_views + ['update_docs']
    __fixed_handlers__ = WebSite.__fixed_handlers__ + ['news']


    def init_resource(self, **kw):
        super(Project, self).init_resource(**kw)
        self.make_resource('news', Blog)

    update_docs = Project_UpdateDocs()
