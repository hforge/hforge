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
from itools.core import get_abspath

# Import from ikaaro
from ikaaro.skins import register_skin, Skin as BaseSkin


class Skin(BaseSkin):

    def get_template_title(self, context):
        here = context.resource
        return here.get_title()


    def build_namespace(self, context):
        namespace = BaseSkin.build_namespace(self, context)
        namespace['column'] = None

        # Right Column
        resource = context.resource
        if resource is not resource.get_site_root():
            return namespace

        if context.view is not resource.get_view(None):
            return namespace

        try:
            column = resource.get_resource('columnright')
        except LookupError:
            return namespace

        namespace['column'] = column.get_handler().events
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
