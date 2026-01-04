
import base64
import xlsxwriter
from io import BytesIO
from odoo import models, fields, _

class SaleOrderImportWizard(models.TransientModel):
    _name = 'sale.order.import.wizard'
    _description = 'Sale Order Import from Excel Wizard'

    import_file = fields.Binary(
        string='Excel File',
        required=True,
        help='Upload your Excel file with columns: Section, Model, Quantity'
    )
    import_filename = fields.Char(
        string='Filename'
    )
    template_file = fields.Binary(
        string='Template',
        compute='_compute_template_file',
        readonly=True
    )

    def _compute_template_file(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Import Template')

        # Write headers
        headers = ['Section', 'Model', 'Quantity']
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)

        # Write sample data
        sample_data = [
            ('Electronics', 'iPhone 15 Pro', 5),
            ('Electronics', 'iPad Air', 3),
            ('Accessories', 'Apple Pencil', 8),
            ('Office Supplies', 'Notebook A4', 50),
        ]
        for r, row_data in enumerate(sample_data, 1):
            for c, cell_data in enumerate(row_data):
                worksheet.write(r, c, cell_data)
        
        workbook.close()
        output.seek(0)
        self.template_file = base64.b64encode(output.read())


    def action_download_template(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=sale.order.import.wizard&id={self.id}&field=template_file&download=true&filename=SO_Import_Template.xlsx',
            'target': 'self',
        }
