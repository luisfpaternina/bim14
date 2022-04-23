import io
import json

import xlwt

from odoo import http
from odoo.tools import html_escape


class MainController(http.Controller):

    @http.route('/tree_excel_export/download', type='http', auth='user')
    def download(self, header, body, **kwargs):
        try:
            excel = self.generate_excel(json.loads(header), json.loads(body))
        except Exception as e:
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return http.request.make_response(html_escape(json.dumps(error)))
        httpheaders = [('Content-Type', 'application/xls'), ('Content-Length', len(excel)), ('Content-Disposition', 'attachment; filename="export.xls"'), ]
        return http.request.make_response(excel, headers=httpheaders)

    def generate_excel(self, header, body):
        workbook = xlwt.Workbook()
        header_style = xlwt.easyxf('font: bold true')
        sheet = workbook.add_sheet('hoja')

        for i, th in enumerate(header):
            sheet.write(0, i, th, header_style)

        for i, tr in enumerate(body, 1):
            for j, td in enumerate(tr):
                sheet.write(i, j, td)

        with io.BytesIO() as stream:
            workbook.save(stream)
            stream.seek(0)
            excel = stream.getvalue()
        return excel
