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

# Import from itools
from itools import get_abspath
from itools.datatypes import Email, String
from itools.stl import stl
from itools.web import FormError

# Import from ikaaro
from ikaaro.registry import register_object_class
from ikaaro.skins import register_skin
from ikaaro.root import Root as BaseRoot


class Root(BaseRoot):
    class_id = 'hforge.org'
    class_title = 'HForge'
    class_skin = 'ui/hforge'

    browse_content__access__ = 'is_allowed_to_edit'
    last_changes__access__ = 'is_allowed_to_edit'


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
# Objects
register_object_class(Root)
# Skin
register_skin('hforge', get_abspath(globals(), 'ui/hforge'))
