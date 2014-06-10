# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech srl
#    (<http://www.didotech.com>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Multi payment improvements',
    'version': '0.1.1',
    'category': 'Localisation/Italy',
    'description': """

Functionalities:

- Add multi payment to bank statement

""",
    'author': 'Sergio Corato',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'account','account_voucher',
    ],
    "init_xml": [
    ],
    "update_xml": [
        'payment_view.xml',
    ],
    "demo_xml": [],
    "active": False,
    "installable": True
}
