# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech srl (http://www.didotech.com)
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from xlwt import Workbook, easyxf
from cStringIO import StringIO
import collections


class Style:
    bold_header = easyxf('font: bold on; align: horiz center')


class ExportSalesTeamReport(orm.TransientModel):
    _name = 'export.sales.team.report'

    _description = "Export revenue on month basis for selected Sales Team"

    def get_years_selection(self, cr, uid, context):
        cr.execute("""SELECT EXTRACT(YEAR FROM date_order) as year
            FROM sale_order
            GROUP BY year
            ORDER BY year
        """)
        years = cr.fetchall()
        return [(str(int(year[0])), str(int(year[0]))) for year in years]

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 64, readonly=True),
        'year': fields.selection(get_years_selection, _('Year'), required=True),
        'state': fields.selection(
            (
                ('selection', 'selection'),
                ('end', 'end')
            ), 'state', required=True, translate=False, readonly=True
        )
    }

    _defaults = {
        'state': lambda *a: 'selection',
    }

    table_layout = collections.OrderedDict({
        0: {'name': 'CLIENTE', 'width': 10000},
        1: {'name': 'year', 'width': 2000},
        2: {'name': 'totale', 'width': 3000}
    })

    def get_query(self, date_start, date_end, section_id):
        return """SELECT partner_id, SUM(amount_total)
                FROM sale_order
                WHERE date_order >= '{date_start}'
                AND date_order <= '{date_end}'
                AND state in ('manual', 'progress', 'done')
                AND section_id = {section_id}
                GROUP BY partner_id""".format(date_start=date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                              date_end=date_end.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                              section_id=section_id)

    def get_period(self, year, month):
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        return start_date, end_date

    def write_header(self, ws, row):
        for column, layout in self.table_layout.items():
            ws.write(row, column, layout['name'], Style.bold_header)
            ws.col(column).width = layout['width']

        for month in range(1, 13):
            ws.write(row, month + column, date(2000, month, 1).strftime('%B'), Style.bold_header)

        return ws

    def action_team_report(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context)
        year = int(wizard.year)

        file_name = 'Sales_Team_{year}.xls'.format(year=year)

        book = Workbook(encoding='utf-8')

        for section in self.pool['crm.case.section'].browse(cr, uid, context['active_ids'], context):
            #ws = book.add_sheet(name, cell_overwrite_ok=True)
            ws = book.add_sheet(section.name)

            query = self.get_query(date(year, 1, 1), date(year, 12, 31), section.id)
            cr.execute(query)
            results = cr.fetchall()
            results = dict(results)
            report = {}

            for partner in self.pool['res.partner'].browse(cr, uid, results.keys(), context=context):
                report[partner.id] = {
                    'name': partner.name,
                    'total_amount': results[partner.id]
                }

            for month in range(1, 13):
                date_start, date_end = self.get_period(year, month)
                query = self.get_query(date_start, date_end, section.id)
                cr.execute(query)
                results = cr.fetchall()

                for key, value in results:
                    report[key].update({month: value})

            ws.write(0, 5, 'Fatturato Mensile Clienti', Style.bold_header)
            now = datetime.now()
            ws.write(1, 0, 'DATA: {}'.format(now.strftime('%d/%m/%Y')))
            ws.write(1, 2, 'ORA: {}'.format(now.strftime('%H:%M')))

            currency = self.pool['res.users'].browse(cr, uid, uid, context).company_id.currency_id
            ws.write(2, 0, 'Divisa: {}'.format(currency.name))

            Style.currency = easyxf('align: horiz right', num_format_str=u'{symbol}#,##0.00'.format(symbol=currency.symbol))

            ws = self.write_header(ws, 4)

            for row, item in enumerate(report.items(), 5):
                partner_id, values = item

                ws.write(row, 0, values['name'])
                ws.write(row, 1, year)
                ws.write(row, 2, values['total_amount'], Style.currency)

                for month in range(1, 13):
                    ws.write(row, month + 2, values.get(month, 0), Style.currency)

        """PARSING DATA AS STRING """
        file_data = StringIO()
        book.save(file_data)
        """STRING ENCODE OF DATA IN WKSHEET"""
        out = file_data.getvalue()
        out = out.encode("base64")
        return self.write(cr, uid, ids, {'state': 'end', 'data': out, 'name': file_name}, context=context)
