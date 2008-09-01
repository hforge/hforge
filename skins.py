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
from itools import get_abspath
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.skins import register_skin, Skin as BaseSkin


class Skin(BaseSkin):

    def get_template_title(self, context):
        here = context.resource
        return here.get_title()


    def build_namespace(self, context):
        namespace = BaseSkin.build_namespace(self, context)
        # h1 Title
        site_root = context.resource.get_site_root()
        namespace['h1_title'] = site_root.get_property('title')
        # Right Column
        try:
            column_obj = site_root.get_resource('columnright')
        except LookupError:
            columnright = None
        else:
            columnright = column_obj.get_handler().events
        namespace['column'] = columnright
        return namespace



###########################################################################
# Register Skin
###########################################################################
# hforge skin
hforge_path = get_abspath('ui/hforge')
hforge_skin = Skin(hforge_path)
register_skin('hforge', hforge_skin)

# odf-i18n skin
hforge_path = get_abspath('ui/odf-i18n')
hforge_skin = Skin(hforge_path)
register_skin('odf-i18n', hforge_skin)
