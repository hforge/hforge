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
from itools import vfs
from itools.datatypes import String
from itools.gettext import MSG, POFile
from itools.handlers import ConfigFile
from itools.handlers import get_handler, Database
from itools.stl import stl
from itools.uri import Path
from itools.web import BaseView, STLView, MSG_MISSING_OR_INVALID

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_website
from ikaaro.website import WebSite


# ODF i18n Testsuite location
root_path = expanduser('~/sandboxes/odf-i18n-tests/documents')
root_path = Path(root_path)



class ODFWSDownload(BaseView):

    access = True
    query_schema = {
        'path': String,
    }

    def GET(self, resource, context):
        response = context.response
        # Filename
        filename = context.query['path']
        if filename[0] != '.' or filename.find('..') >= 0:
            return context.come_back(MSG_MISSING_OR_INVALID)

        path = root_path.resolve2(filename)
        response.set_header('Content-Disposition',
                            'inline; filename="%s"' % path.get_name())
        # File
        resource = get_handler(path)
        resource.database = Database()
        # Content-Type
        response.set_header('Content-Type', resource.get_mimetype())
        return resource.to_str()



class ODFWSBrowseTests(STLView):

    access = True
    title = MSG(u'View')
    template = '/ui/odf-i18n/template.xml'
    query_schema = {
        'path': String(default='.')}


    def get_namespace(self, resource, context):
        # Get the path
        str_path = context.query['path']
        if str_path[0] != '.' or str_path.find('..') >= 0:
            goto = './;browse_tests'
            return context.come_back(MSG_MISSING_OR_INVALID, goto=goto)
        path = Path(str_path)

        # Build the common namespace
        if path == '.':
            name = MSG(u'Testsuite Documents')
        else:
            name = path.get_name()
        # Crumbs
        base = '/%s/;browse_tests' % context.site_root.get_pathto(resource)
        link = base + '?path=%s'
        crumbs = []
        breadcrumb_path = path
        while breadcrumb_path != '.':
            crumbs.append({
                'name': breadcrumb_path.get_name(),
                'link': link % breadcrumb_path})
            # Next
            breadcrumb_path = breadcrumb_path.resolve2('..')
        crumbs.append({'name': 'Test Suite', 'link': link % '.'})
        crumbs.reverse()
        common_ns = {
            'h1_title': resource.class_title,
            'name': name,
            'breadcrumb': crumbs}

        # Get the resource
        uri = root_path.resolve2(path)
        resource = get_handler(uri)
        resource.database = Database()

        # View PO file
        root = context.root
        if isinstance(resource, POFile):
            msgs = [
                {'id': '" "'.join(item.msgid), 'str': '" "'.join(item.msgstr)}
                for item in resource.get_messages() ]

            namespace = {'messages': msgs}
            template = root.get_resource('/ui/odf-i18n/ODFWS_view_po.xml')
            common_ns['body'] = stl(template, namespace)
            return common_ns

        # Browse Folders
        files = []
        folder_is_test = False
        childs = resource.get_handler_names()
        childs.sort()
        a_handler = root_path.resolve2(str_path + '/' + childs[0])
        if vfs.is_folder(a_handler):
            # Folder
            for child_name in childs:
                path = '%s/%s' % (str_path, child_name)
                files.append({
                    'child_name': child_name,
                    'to_child': link % path})
            namespace = {'content': files}
            template = root.get_resource('/ui/odf-i18n/ODFWS_browse_folder.xml')
            common_ns['body'] = stl(template, namespace)
            return common_ns

        # Test Folder
        namespace = {}
        has_metadata = False
        for child_name in childs:
            child_link = str_path + '/' + child_name
            # Metadatas File
            if child_name.endswith('.conf'):
                abs_path = root_path.resolve2(child_link)
                setup_file = ConfigFile(abs_path)
                namespace['title'] = setup_file.get_value('title')
                description = setup_file.get_value('description')
                namespace['description'] = description
                reference = setup_file.get_value('reference')
                namespace['reference'] = reference
                url_reference = setup_file.get_value('url_reference')
                namespace['url_reference'] = url_reference
                has_metadata = True
                continue
            # Test Files
            file = {
                'child_name': child_name,
                'view': None,
                'to_child': ';download?path=%s' % child_link,
            }
            if child_name.endswith('.po'):
                file['view'] = '%s?path=%s' % (base, child_link)
            files.append(file)
        namespace['content'] = files

        if has_metadata:
            template_path = '/ui/odf-i18n/ODFWS_browse_test.xml'
        else:
            template_path = '/ui/odf-i18n/ODFWS_browse_test_files.xml'
        template = root.get_resource(template_path)
        common_ns['body'] = stl(template, namespace)
        return common_ns



class ODFWS(WebSite):

    class_id = 'hforge.org/odf-i18n-tests'
    class_title = MSG(u'i18n Testsuite')
    class_skin = 'ui/odf-i18n'
    class_views = ['browse_tests'] + WebSite.class_views

    # Views
    download = ODFWSDownload()
    browse_tests = ODFWSBrowseTests()



###########################################################################
# Register
###########################################################################
register_resource_class(ODFWS)
register_website(ODFWS)
