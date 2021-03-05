
import re

from odoo.http import request, route, Controller

from io import BytesIO
from zipfile import ZipFile


class HrPayroll(Controller):

    @route(["/print/payslip/dispersions"], type='http', auth='user')
    def get_payroll_report_print(self, list_ids='', **post):
        """Get print dispersions petitions
        - Get dispersions text and name from the payslip batch
        - If there are not dispersions return not found
        - If there is just one dispersion return a .TXT file
        - If there is more dispersions return a .zip file with a txt per dispersion/bank
        """
        is_allowed = request.env.user.has_group('l10n_mx_edi_payslip.l10n_mx_edi_allow_print_payslip_dispertion')
        if not is_allowed or not list_ids or re.search("[^0-9|,]", list_ids):
            return request.not_found()
        ids = [int(s) for s in list_ids.split(',')]
        payslips_run = request.env['hr.payslip.run'].browse(ids)

        dispersions = payslips_run._get_payslips_dispersions()
        if not dispersions:
            return request.not_found()

        # If there is just one bank/dispersion download a single txt
        if len(dispersions) == 1:
            report_name = dispersions[0][0]
            text = dispersions[0][1]
            texthttpheaders = [
                ('Content-Type', 'text/plain'),
                ('Content-Length', len(text)),
                ('Content-Disposition', 'attachment; filename=%s.txt;' % report_name)
            ]
            return request.make_response(text, headers=texthttpheaders)

        zip_stream = BytesIO()
        with ZipFile(zip_stream, 'w') as zipped:
            for dispersion in dispersions:
                zipped.writestr(dispersion[0], dispersion[1])
            zipped.close()

        zip_name = payslips_run._get_payslips_dispersion_report_name()
        ziphttpheaders = [
            ('Content-Type', 'application/zip'),
            ('Content-Length', len(zip_stream.getvalue())),
            ('Content-Disposition', 'attachment; filename=%s.zip;' % zip_name)
        ]
        return request.make_response(zip_stream.getvalue(), headers=ziphttpheaders)
