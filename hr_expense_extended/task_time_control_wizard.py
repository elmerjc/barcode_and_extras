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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import time
import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class wizard_expense_line(orm.TransientModel):
    _name = 'wizard.expense.line'
    
    def _get_payer(self, cr, uid, context=None):
        return self.pool['hr.expense.line']._columns['payer'].selection
    
    #def _amount(self, cr, uid, ids, field_name, arg, context=None):
    #    if ids:
    #        result = {}
    #    else:
    #        return {}
    #
    #    wizards = self.browse(cr, uid, ids)
    #    for wizard in wizards:
    #        result['wizard.id'] = wizard.unit_amount * wizard.unit_quantity
    #    pdb.set_trace()
    #    return result
    
    _columns = {
        'name': fields.char('Expense Note', size=128, required=True),
        'date_value': fields.date('Date', required=True),
        #'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        'unit_amount': fields.float('Unit Price', digits_compute=dp.get_precision('Account')),
        'unit_quantity': fields.float('Quantities'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('hr_expense_ok', '=', True)]),
        'ref': fields.char('Reference', size=32),
        'payer': fields.selection(_get_payer, _('Payer'), required=True),
        'wizard_id': fields.many2one('task.time.control.confirm.wizard', 'Wizard')
    }
    
    _defaults = {
        'unit_quantity': 1,
        'date_value': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
    }
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            res['name'] = product.name
            amount_unit = product.price_get('standard_price')[product.id]
            res['unit_amount'] = amount_unit
            
        return {'value': res}
    

class task_time_control_confirm_wizard(orm.TransientModel):
    _inherit = 'task.time.control.confirm.wizard'
    
    _columns = {
        'expense_line_ids': fields.one2many('wizard.expense.line', 'wizard_id', 'Expenses'),
        'user_id': fields.many2one("res.users", 'User')
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

    def close_confirm(self, cr, uid, ids, context=None):
        confirm_wizard = self.browse(cr, uid, ids[0])
        employee = self.pool['hr.employee'].get_employee(cr, uid, uid)
        expense_values = {
            'employee_id': employee.id,
            'company_id': employee.user_id.company_id.id,
            'journal_id': False,
            'user_valid': False,
            'department_id': False
        }
        
        for expense_line in confirm_wizard.expense_line_ids:
            expense_values['date'] = expense_line.date_value
            hr_expense_id = self.pool['hr.expense.expense'].create(cr, uid, expense_values)
            
            values = {
                'task_id': confirm_wizard.started_task.id,
                'name': expense_line.name,
                'date_value': expense_line.date_value,
                'unit_amount': expense_line.unit_amount,
                'unit_quantity': expense_line.unit_quantity,
                'product_id': expense_line.product_id.id,
                'ref': expense_line.ref,
                'payer': expense_line.payer,
                'expense_id': hr_expense_id
            }
            self.pool['hr.expense.line'].create(cr, uid, values)
        
        return super(task_time_control_confirm_wizard, self).close_confirm(cr, uid, ids, context)
