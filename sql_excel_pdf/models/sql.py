# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from io import BytesIO
from psycopg2 import ProgrammingError
import xlwt,  base64, re


class SqlExcelPdf(models.Model):
    _name = "sql.excel.pdf"
    _inherit = ['mail.thread']
    _description = "Sql to Excel Pdf Views"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Archive", default=True)
    category_id = fields.Many2one('sql.category',string="Category", required=True)
    tag_ids = fields.Many2many('sql.tags','tags_cate_rel','tag_id','sql_id', string="Tags")
    created_by = fields.Many2one('res.users',string="Created By",default=lambda self: self.env.user, readonly=True)
    created_date = fields.Date(string="Created Date", readonly=True, default=fields.date.today())
    last_updated_by = fields.Many2one('res.users',string="Last Updated By", track_visibility='onchange', readonly=True)
    last_updated_date = fields.Date(string="Last Updated Date", track_visibility='onchange', readonly=True)
    sql_query = fields.Text(string="Query", required=True, copy=False, index=True, track_visibility='onchange', help="You can't use the following words"
        ": DELETE, DROP, CREATE, INSERT, ALTER, TRUNCATE, EXECUTE, UPDATE.")
    file = fields.Binary('XLS File', readonly=True)
    file_name = fields.Char('XLs Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ], string='Status', copy=False, index=True, track_visibility='onchange', default='draft')

    PROHIBITED_WORDS = [
        'delete',
        'drop',
        'insert',
        'alter',
        'truncate',
        'execute',
        'create',
        'update',
        'ir_config_parameter',
    ]

    @api.multi
    def write(self, values):
        values['last_updated_by'] = self.env.user.id
        values['last_updated_date'] = fields.date.today()
        res = super(SqlExcelPdf, self).write(values)
        return res

    @api.multi
    def action_validate(self):
        self._check_prohibited_words()
        self.prepare_query_execution()
        return self.write({'state': 'validate'})

    @api.multi
    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def prepare_query_execution(self):
        self.ensure_one()
        column_list = ['S.No']
        res = {}
        try:
            self.env.cr.execute(self.sql_query)
            for column in self.env.cr.description:
                column_list.append(column[0])
            result = self.env.cr.fetchall()
        except ProgrammingError as e:
            raise UserError(
                _("The SQL query is not valid:\n\n %s") % e)
        res.update({'column_list':column_list, 'result':result})
        return res

    @api.multi
    def _check_prohibited_words(self):
        self.ensure_one()
        query = self.sql_query.lower()
        for word in self.PROHIBITED_WORDS:
            expr = r'\b%s\b' % word
            is_not_safe = re.search(expr, query)
            if is_not_safe:
                raise UserError(_(
                    "The query is not allowed. Because it contains unsafe Query"
                    " '%s'") % (word))

    @api.multi
    def print_pdf_report(self):
        return self.env.ref('sql_excel_pdf.action_report_sql_pdf').report_action(self)

    @api.multi
    def print_xls_report(self):
        fp = BytesIO()
        Workbook = xlwt.Workbook()
        sheet = Workbook.add_sheet(self.name)
        style_bold_head = xlwt.easyxf('font: bold 1; align: horiz center; pattern: pattern solid, fore_colour black; font: bold 1')
        style_bold = xlwt.easyxf('font: bold 1; align: horiz center; pattern: pattern solid, fore_colour gray25; font: bold 1')
        style_value = xlwt.easyxf('font: bold 0;')
        style_italic = xlwt.easyxf('font: italic 1; align: horiz center;')
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy hh:mm:ss'
        val  = self.prepare_query_execution()
        row = 1
        col = 0
        date_time = datetime.now()
        date = date_time.strftime('%d-%m-%Y %H:%M:%S')
        header_cols = len(val.get('column_list'))
        # Set sheet first row (for header purpuse)  
        sheet.write_merge(row, row, 0, header_cols - 1, self.name, style_bold_head)
        report_value = 'Database :' + self.env.cr.dbname + ' |' +' Printed by :' + self.env.user.name + ' |' + ' Printed on :' + date + 'Hrs' 
        row += 1
        sheet.write_merge(row, row, 0, header_cols - 1, report_value , style_italic)
        row += 1
        col = 0
        # Set Header
        for col_val in val.get('column_list'):
            sheet.write(row, col, col_val, style_bold)
            col += 1
        
        row += 1
        col = 0
        s_no = 1
        # Set data
        for col_result in val.get('result'):
            col = 0
            sheet.write(row, col, s_no, style_value)
            for result in col_result: 
                if type(result) == datetime:
                    sheet.col(col + 1).width = 5000
                    sheet.write(row, col + 1, result, date_format)
                else:
                    sheet.col(col + 1).width = 5000
                    sheet.write(row, col + 1, result, style_value)
                col += 1
            row += 1
            s_no += 1

        Workbook.save(fp)
        self.file = base64.encodestring(fp.getvalue())
        self.file_name = self.name + ' - ' + date + '.xls'



class SqlCategory(models.Model):
    _name = "sql.category"
    _description = "Sql Category"

    name = fields.Char(string="Name", required=True)

class SqlTags(models.Model):
    _name = "sql.tags"
    _description = "Sql Tags"

    name = fields.Char(string="Name", required=True)
