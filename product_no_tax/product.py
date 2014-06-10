#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyraght (c) 2013 Didotech srl (<http://www.didotech.com>)
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

from osv import fields, osv
from tools.translate import _


class product_product(osv.osv):
    _inherit = "product.product"
        
    def _hide_tax_on_product(self, cr, uid, ids, field_name, arg, context):
        res = {}
        
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr, uid, company_id)
        
        for product_id in ids:           
            res[product_id] = company.hide_tax_on_product
        return res
    
    
        
    _columns = {
        'hide_tax': fields.function(_hide_tax_on_product, string="Tax Invisible", type='boolean', readonly=True, method=True),
    }
    