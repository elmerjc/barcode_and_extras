# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013-2014 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Project Extended',
    'version': '3.4.9.14',
    'category': 'Generic Modules/Projects & Services',
    'description': """Tasks list on a dedicated tab on the project form
""",
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'project',
        'project_gtd',
        'project_long_term',
        'project_timesheet',
    ],
    "data": [
        'project/project_view.xml',
        'project/project_task_view.xml',
        'project/project_view_menu.xml',
        'res_partner/res_partner_view.xml',
        'security/security.xml',
    ],
    "active": False,
    "installable": True
}
