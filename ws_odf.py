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

# Import from itools
from itools import vfs
from itools.datatypes import String
from itools.gettext import POFile
from itools.handlers import ConfigFile
from itools.handlers import get_handler, Database
from itools.stl import stl
from itools.uri import Path

# Import from ikaaro
from ikaaro.messages import MSG_MISSING_OR_INVALID
from ikaaro.registry import register_object_class, register_website
from ikaaro.website import WebSite


# ODF i18n Testsuite location
root_path = Path('/home/elbichon/itaapy/sandboxes/odf-i18n-tests/documents')



class ODFWS(WebSite):
    class_id = 'hforge.org/odf-i18n-tests'
    class_title = u'i18n Testsuite'
    class_skin = 'ui/odf-i18n'


    GET__access__ = True
    def GET(self, context):
        return context.uri.resolve2(';browse_tests')


    download__access__ = True
    def download(self, context):
        response = context.response
        # Filename
        filename = context.get_form_value('path', type=String)
        if (not filename.startswith('.')) or filename.find('..') >= 0:
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


    browse_tests__access__ = True
    def browse_tests(self, context):
        str_path = context.get_form_value('path', type=String, default='.')
        if (not str_path.startswith('.')) or str_path.find('..') >= 0:
            return context.come_back(message=MSG_MISSING_OR_INVALID,
                                     goto='./;browse_tests')
        path = Path(str_path)
        uri = root_path.resolve2(path)
        resource = get_handler(uri)
        resource.database = Database()

        # Build common namespace
        common_ns = {}
        common_ns['h1_title'] = self.class_title
        if path == '.':
            common_ns['name'] = u'Testsuite Documents'
        else:
            common_ns['name'] = path.get_name()
        crumbs = []
        breadcrumb_path = path
        while breadcrumb_path != '.':
            crumb = {}
            crumb['name'] = breadcrumb_path.get_name()
            link = './;browse_tests?path=./' + breadcrumb_path.__str__()
            crumb['link'] = link
            crumbs.append(crumb)
            breadcrumb_path = breadcrumb_path.resolve2('..')
        crumb = {}
        crumb['name'] = 'Test Suite'
        crumb['link'] = './;browse_tests?path=.'
        crumbs.append(crumb)
        crumbs.reverse()
        common_ns['breadcrumb'] = crumbs

        namespace = {}
        # View PO file
        if isinstance(resource, POFile):
            msgs = []
            for message in resource.get_messages():
                msg = {}
                msg['id'] = '" "'.join(message.msgid)
                msg['str'] = '" "'.join(message.msgstr)
                msgs.append(msg)
            namespace['messages'] = msgs
            template = self.get_object('/ui/odf-i18n/ODFWS_view_po.xml')
            common_ns['body'] = stl(template, namespace)
            common_template = self.get_object('/ui/odf-i18n/template.xml')
            return stl(common_template, common_ns)

        # Browse Folders
        files = []
        folder_is_test = False
        childs = resource.get_handler_names()
        childs.sort()
        an_handler = root_path.resolve2(str_path + '/' + childs[0])
        if vfs.is_folder(an_handler):
            # Folder
            for child_name in childs:
                child_link = str_path + '/' + child_name
                file = {}
                file['child_name'] = child_name
                file['to_child'] = ';browse_tests?path=%s' % child_link
                files.append(file)
            namespace['content'] = files
            template = self.get_object('/ui/odf-i18n/ODFWS_browse_folder.xml')
            common_ns['body'] = stl(template, namespace)
            common_template = self.get_object('/ui/odf-i18n/template.xml')
            return stl(common_template, common_ns)
        else:
            # Test Folder
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
                file = {}
                file['child_name'] = child_name
                file['view'] = None
                file['to_child'] = ';download?path=%s' % child_link
                if child_name.endswith('.po'):
                    file['view'] = ';browse_tests?path=%s' % child_link
                files.append(file)
            namespace['content'] = files

            if has_metadata:
                template_path = '/ui/odf-i18n/ODFWS_browse_test.xml'
            else:
                template_path = '/ui/odf-i18n/ODFWS_browse_test_files.xml'
            template = self.get_object(template_path)
            common_ns['body'] = stl(template, namespace)
            common_template = self.get_object('/ui/odf-i18n/template.xml')
            return stl(common_template, common_ns)



###########################################################################
# Register
###########################################################################
register_object_class(ODFWS)
register_website(ODFWS)
