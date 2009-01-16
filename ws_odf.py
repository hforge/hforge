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
from os.path import expanduser

# Import from itools
import itools.odf
from itools import vfs
from itools.datatypes import String, PathDataType
from itools.gettext import MSG, POFile
from itools.handlers import ConfigFile, Folder, get_handler_class_by_mimetype
from itools.handlers import get_handler, Database
from itools.srx import SRXFile
from itools.stl import stl
from itools.uri import Path
from itools.web import BaseView, STLView, STLForm, MSG_MISSING_OR_INVALID
from itools.web import ERROR
from itools.xliff import XLFFile
from itools.xml import XMLParser, XMLError

# Import from ikaaro
from ikaaro.datatypes import FileDataType
from ikaaro.registry import register_resource_class, register_website

# Import from hforge
from project import Project


# ODF i18n Testsuite location
test_suite = expanduser('~/sandboxes/odf-i18n-tests/documents')
test_suite = get_handler(test_suite)
test_suite.database = Database()



class ODFWSDownload(BaseView):

    access = True
    query_schema = {
        'path': PathDataType}

    def GET(self, resource, context):
        path = context.query['path']
        if path is None:
            return context.come_back(MSG_MISSING_OR_INVALID)

        # Get the desired handler
        if path.startswith_slash:
            path.startswith_slash = False
        handler = test_suite.get_handler(path)

        # Ok
        response = context.response
        response.set_header('Content-Disposition',
                            'inline; filename="%s"' % path.get_name())

        response.set_header('Content-Type', handler.get_mimetype())
        return handler.to_str()



class ODFWSBrowseTests(STLView):

    access = True
    title = MSG(u'View')
    template = '/ui/odf-i18n/template.xml'
    query_schema = {
        'path': PathDataType}


    def get_namespace(self, resource, context):
        path = context.query['path']
        if path is None:
            path = Path('.')

        if path.startswith_slash:
            path.startswith_slash = False

        # Namespace: the location
        base = '/%s/;browse_tests' % context.site_root.get_pathto(resource)
        link = base + '?path=%s'
        location = [{'name': MSG(u'Test Suite'), 'link': link % '.'}]
        for i, name in enumerate(path):
            p = path[:i+1]
            try:
                test_suite.get_handler(p)
            except LookupError:
                location.append({'name': name, 'link': None})
                body = MSG(u'The "$path" resource has not been found')
                body = body.gettext(path=p)
                return {'location': location, 'body': body}
            else:
                location.append({'name': name, 'link': link % p})

        # Get the handler
        handler = test_suite.get_handler(path)

        # (1) View PO file
        root = context.root
        if isinstance(handler, POFile):
            msgs = [ {'id': '" "'.join(item.source),
                      'str': '" "'.join(item.target)}
                        for item in handler.get_units() ]

            namespace = {'messages': msgs}
            template = root.get_resource('/ui/odf-i18n/view_po.xml')
            body = stl(template, namespace)
            return {'location': location, 'body': body}

        # Load setup file
        if handler.has_handler('setup.conf'):
            setup = handler.get_handler('setup.conf', cls=ConfigFile)
        else:
            setup = None

        # (2) Browse Folders
        children = handler.get_handler_names()
        children.sort()
        a_handler = handler.get_handler(children[0])
        if isinstance(a_handler, Folder):
            files = []
            for child in children:
                child_handler = handler.get_handler(child)
                number = 0
                for x in vfs.traverse(child_handler.uri):
                    if x.path[-1].endswith('.po'):
                        number += 1
                files.append({'child_name': child,
                              'to_child': link % ('%s/%s' % (path, child)),
                              'number': number})

            namespace = {'content': files}
            template = root.get_resource('/ui/odf-i18n/browse_folder.xml')
            body = stl(template, namespace)
            return {'location': location, 'body': body}

        # (3) Test Folder
        if setup is None:
            title = description = reference = url_reference = None
        else:
            title = setup.get_value('title')
            description = setup.get_value('description')
            reference = setup.get_value('reference')
            url_reference = setup.get_value('url_reference')
            # Format the description (may contain XML)
            description = XMLParser(description)

        files = []
        for child in children:
            if child != 'setup.conf':
                child_path = '%s/%s' % (path, child)
                view = (link % child_path) if child.endswith('.po') else None
                files.append({
                    'child_name': child,
                    'view': view,
                    'to_child': ';download?path=%s' % child_path})

        template = root.get_resource('/ui/odf-i18n/browse_test.xml')
        namespace = {
            'title': title,
            'description': description,
            'reference': reference,
            'url_reference': url_reference,
            'content': files}
        body = stl(template, namespace)

        return {'location': location, 'body': body}



class Translation_View(STLForm):

    access = True
    title = MSG(u'Online translation')
    template = '/ui/odf-i18n/translation_view.xml'


    # First form
    action_odf2tr_schema = {
        'odf_file': FileDataType(mandatory=True),
        'srx_file': FileDataType(),
        'output_type': String(mandatory=True)}

    def action_odf2tr(self, resource, context, form):
        odf_file_name, odf_file_mime_type, odf_file_data = form['odf_file']
        srx_file = form['srx_file']
        output_type = form['output_type']

        # Not a too big file
        if len(odf_file_data) >= 102400:
            context.message = ERROR(u'Your ODF file is too big >= 100Kb')
            return

        # Get the good "get_units"
        odf_handler = get_handler_class_by_mimetype(odf_file_mime_type)
        try:
            get_units = odf_handler(string=odf_file_data).get_units
        except AttributeError:
            context.message = ERROR(u'malformed ODF file')
            return

        # a SRX file ?
        if srx_file is not None:
            srx_file_data = srx_file[2]
            try:
                srx_handler = SRXFile(string=srx_file_data)
            except XMLError:
                context.message = ERROR(u'unexpected error, please verify '
                                        u'your input files')
                return
        else:
            srx_handler = None

        # The good handler for the output
        if output_type == 'PO':
            out_filename = odf_file_name+'.po'
            out_handler = POFile()
        else:
            out_filename = odf_file_name+'.xlf'
            out_handler = XLFFile()

        # Make the output
        for source, source_context, line in get_units(
                                            srx_handler=srx_handler):
            out_handler.add_unit(odf_file_name, source, source_context, line)



        # Return the result
        response = context.response
        response.set_header('Content-Disposition',
                            'inline; filename="%s"' % out_filename)
        response.set_header('Content-Type', out_handler.class_mimetypes[0])
        return out_handler.to_str()


    # Second form
    action_odf2odf_schema = {
        'tr_odf_file': FileDataType(mandatory=True),
        'tr_srx_file': FileDataType(),
        'tr_input': FileDataType(mandatory=True)}

    def action_odf2odf(self, resource, context, form):
        odf_file_name, odf_file_mime_type, odf_file_data = form['tr_odf_file']
        srx_file = form['tr_srx_file']
        trash, input_file_mime_type, input_file_data = form['tr_input']

        # Not a too big file
        if len(odf_file_data) >= 102400:
            context.message = ERROR(u'Your ODF file is too big >= 100Kb')
            return

        # Get the good "translate"
        odf_handler = get_handler_class_by_mimetype(odf_file_mime_type)
        try:
            translate = odf_handler(string=odf_file_data).translate
        except AttributeError:
            context.message = ERROR(u'malformed ODF file')
            return

        # a SRX file ?
        if srx_file is not None:
            srx_file_data = srx_file[2]
            try:
                srx_handler = SRXFile(string=srx_file_data)
            except XMLError:
                context.message = ERROR(u'unexpected error, please verify '
                                        u'your input files')
                return
        else:
            srx_handler = None

        # Get the catalog and test it
        input_handler = get_handler_class_by_mimetype(input_file_mime_type)
        catalog = input_handler(string=input_file_data)
        try:
            catalog.gettext
        except AttributeError:
            context.message = ERROR(u'unexpected error, please verify '
                                    u'your input files')
            return

        # Make the translation!
        data = translate(catalog, srx_handler=srx_handler)

        # Return the result
        response = context.response
        response.set_header('Content-Disposition',
                            'inline; filename="%s"' % odf_file_name)
        response.set_header('Content-Type', odf_file_mime_type)
        return data




    def get_namespace(self, resource, context):
        return  {}



class ODFWS(Project):

    class_id = 'hforge.org/odf-i18n-tests'
    class_title = MSG(u'i18n Testsuite')
    class_skin = 'ui/odf-i18n'
    class_views = ['browse_tests', 'translation'] + Project.class_views

    # Views
    download = ODFWSDownload()
    browse_tests = ODFWSBrowseTests()
    translation = Translation_View()



###########################################################################
# Register
###########################################################################
register_resource_class(ODFWS)
register_website(ODFWS)
