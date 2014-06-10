# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
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
    "name": "Core extended",
    "version": "2.0.4.0",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "category": "Base",
    "description": """
        Module extendes OpenERP core functionality:
        ir_sequence - add functions:
            current_number(cr, uid, sequence_id)
            go_back(cr, uid, sequence_id, steps_back=1)
            create() will set code to the value find in context dictionary (if value is present in context)
            
        ir_attachment - add function
            get_as_zip(cr, uid, ids, log=False, encode=True, compress=True)
            
        ordereddict - Backport of OrderedDict() class that runs on Python 2.4, 2.5, 2.6, 2.7 and pypy.
        
        wkf_service - add function
            trg_last_action(uid, model, obj_id, cr) - this function is useful when debugging a workflow related problems 
            
    """,
    "depends": [
        'base',
    ],
    "init_xml": [],
    "update_xml": [
    ],
    "active": False,
    "installable": True,
    'external_dependencies': {
        'python': [
            'zlib',
        ]  
    }
}
