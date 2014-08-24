# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2014 Didotech srl (www.didotech.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
import logging
_logger = logging.getLogger(__name__)


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, *args):
        super(account_invoice, self).action_number(cr, uid, ids, *args)
        asset_obj = self.pool.get('account.asset.asset')
        asset_line_obj = self.pool.get('account.asset.depreciation.line')
        for inv in self.browse(cr, uid, ids):
            for aml in inv.move_id.line_id:
                if aml.asset_id and not aml.subsequent_asset_id:
                    asset = aml.asset_id
                    ctx = {'create_asset_from_move_line': True}
                    asset_obj.write(cr, uid, [asset.id], {'code': '', }, context=ctx)
                    # TODO progressive number?
                    asset_line_name = asset_obj._get_depreciation_entry_name(cr, uid, asset, 0)
                    asset_line_obj.write(cr, uid, [asset.depreciation_line_ids[0].id],
                        {'name': asset_line_name}, context={'allow_asset_line_update': True})
                elif aml.subsequent_asset_id:
                    asset = aml.subsequent_asset_id
                    ctx = {'update_asset_value_from_move_line': True}
                    if asset.type == 'normal':
                        # create subsequent asset line
                        line_name = asset_obj._get_depreciation_entry_name(cr, uid, asset, 0, context=ctx)
                        vals = {}
                        vals['tax_code_id'] = aml.tax_code_id.id
                        vals['tax_amount'] = aml.tax_amount
                        vals['quantity'] = aml.quantity
                        vals['debit'] = aml.debit
                        vals['credit'] = aml.credit
                        
                        asset_value = self.pool['account.move.line'].get_asset_value_with_ind_tax(cr, uid, vals, context={})
                        asset_line_vals = {
                            'amount': aml.debit and asset_value or aml.credit and - asset_value,
                            'asset_id': asset.id,
                            'name': line_name,
                            'line_date': aml.date,
                            'init_entry': True,
                            'type': 'create',
                        }
                        asset_line_id = asset_line_obj.create(cr, uid, asset_line_vals, context=ctx)
                        asset_line_obj.write(cr, uid, [asset_line_id], {'move_id': aml.move_id.id})
        return True

    def action_cancel(self, cr, uid, ids, *args):
        assets = []
        for inv in self.browse(cr, uid, ids):
            move = inv.move_id
            assets = move and [aml.asset_id for aml in filter(lambda x: x.asset_id, move.line_id)]
        super(account_invoice, self).action_cancel(cr, uid, ids, *args)
        if assets:
            asset_obj = self.pool.get('account.asset.asset')
            asset_obj.unlink(cr, uid, [x.id for x in assets])
        return True

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        if x.get('asset_category_id'):
            if res.get('debit') or res.get('credit'):  # skip empty debit/credit
                res['asset_category_id'] = x['asset_category_id']
        if x.get('subsequent_asset_id'):
            if res.get('debit') or res.get('credit'):  # skip empty debit/credit
                res['subsequent_asset_id'] = x['subsequent_asset_id']
        return res

    def inv_line_characteristic_hashcode(self, invoice, invoice_line):
        res = super(account_invoice, self).inv_line_characteristic_hashcode(invoice, invoice_line)
        res += '-%s' % invoice_line.get('asset_category_id', 'False')
        return res


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    _columns = {
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
        'subsequent_asset_id': fields.many2one('account.asset.asset', 'Subsequent Purchase of Asset'),
    }

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id):
        res = super(account_invoice_line, self).onchange_account_id(cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id)
        if account_id:
            asset_category = self.pool.get('account.account').browse(cr, uid, account_id).asset_category_id
            if asset_category:
                vals = {'asset_category_id': asset_category.id}
                if 'value' not in res:
                    res['value'] = vals
                else:
                    res['value'].update(vals)
        return res

    def onchange_subsequent_asset_id(self, cr, uid, ids, subsequent_asset_id):
        res = {}
        if subsequent_asset_id:
            asset_id = self.pool['account.asset.asset'].browse(cr, uid, subsequent_asset_id)
            res['value'] = {'asset_category_id': asset_id.category_id.id}
        return res

    def onchange_asset_ctg_id(self, cr, uid, ids, asset_ctg_id):
        res = {}
        if asset_ctg_id:
            asset_ctg = self.pool['account.asset.category'].browse(cr, uid, asset_ctg_id)
            res['value'] = {'account_id': asset_ctg.account_asset_id.id}
        return res

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context)
        if line.asset_category_id:
            res['asset_category_id'] = line.asset_category_id.id
        if line.subsequent_asset_id:
            res['subsequent_asset_id'] = line.subsequent_asset_id.id
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
