from odoo import http, _
from odoo.exceptions import AccessError, UserError
from odoo.addons.web.controllers.main import Home
import base64
import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class AvailabilityReportController(http.Controller):
    
    @http.route('/ops/availability-report/<int:sale_order_id>', type='http', auth='user')
    def generate_availability_report(self, sale_order_id, **kwargs):
        """
        Generate an availability report for a sale order.
        Stock levels are masked based on user's branch/business unit permissions.
        """
        try:
            # Get the sale order
            sale_order = http.request.env['sale.order'].browse(sale_order_id)
            
            # Check access
            if not sale_order.exists():
                raise UserError(_('Sale order not found'))
            
            # Check permission
            user = http.request.env.user
            user_context = user.get_effective_matrix_access()
            
            # Verify user has access to the order's branch
            if sale_order.ops_branch_id:
                if sale_order.ops_branch_id.id not in user_context['branch_ids'].ids:
                    raise AccessError(_('You do not have permission to view this sale order'))
            
            # Get availability data
            availability_data = sale_order._get_products_availability_data()
            
            # Filter stock levels based on permissions
            filtered_data = self._mask_stock_levels(availability_data, user, sale_order)
            
            # Generate PDF
            pdf_content = self._generate_pdf(filtered_data, sale_order)
            
            # Return PDF response
            return http.Response(
                pdf_content,
                content_type='application/pdf',
                headers=[('Content-Disposition', f'inline; filename=Availability_{sale_order.name}.pdf')]
            )
            
        except AccessError as e:
            return http.Response(
                str(e),
                status=403,
                content_type='text/plain'
            )
        except UserError as e:
            return http.Response(
                str(e),
                status=400,
                content_type='text/plain'
            )
    
    def _mask_stock_levels(self, availability_data, user, sale_order):
        """
        Mask stock levels based on user permissions.
        
        Rules:
        - Show full stock if user manages the warehouse
        - Show masked stock "***" if user doesn't have warehouse access
        - Show partial stock if user has partial access
        """
        masked_data = []
        
        is_warehouse_manager = user.has_group('stock.group_stock_manager')
        
        for item in availability_data:
            masked_item = item.copy()
            
            # Full access: warehouse manager
            if is_warehouse_manager:
                masked_data.append(masked_item)
                continue
            
            # Check business unit access
            product = http.request.env['product.product'].search([
                ('default_code', '=', item.get('sku'))
            ], limit=1)
            
            if product and product.business_unit_id:
                user_bus_units = user.get_effective_matrix_access()['business_unit_ids']
                if product.business_unit_id.id in user_bus_units.ids:
                    # User has access to this product's business unit
                    masked_data.append(masked_item)
                else:
                    # Mask stock information
                    masked_item['stock_on_hand'] = '***'
                    masked_item['display_qty'] = '***'
                    masked_item['is_insufficient'] = False
                    masked_data.append(masked_item)
            else:
                # No business unit restriction, show data
                masked_data.append(masked_item)
        
        return masked_data
    
    def _generate_pdf(self, availability_data, sale_order):
        """
        Generate a PDF report of product availability.
        """
        if not HAS_REPORTLAB:
            # Fallback: Return simple HTML response
            html_content = self._generate_html_report(availability_data, sale_order)
            return html_content.encode('utf-8')
        
        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.5*inch,
        )
        
        # Build document content
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=0.2*inch,
        )
        
        elements.append(Paragraph(
            f'Product Availability Report',
            title_style
        ))
        
        # Order info
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
        )
        
        elements.append(Paragraph(
            f'<b>Order:</b> {sale_order.name} | <b>Partner:</b> {sale_order.partner_id.name} | '
            f'<b>Date:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            info_style
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Data table
        table_data = [
            ['SKU', 'Product Name', 'Ordered Qty', 'Stock On Hand', 'Available', 'Status']
        ]
        
        for item in availability_data:
            stock_str = str(item.get('stock_on_hand', '***'))
            display_str = str(item.get('display_qty', '***'))
            status = 'IN STOCK' if not item.get('is_insufficient') else 'LOW STOCK'
            
            table_data.append([
                item.get('sku', ''),
                item.get('product_name', ''),
                str(item.get('ordered_qty', '')),
                stock_str,
                display_str,
                status,
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        
        elements.append(table)
        
        # Footer note
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
        )
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            '<i>Stock levels masked based on user permissions.</i>',
            footer_style
        ))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        return pdf_buffer.read()
    
    def _generate_html_report(self, availability_data, sale_order):
        """Fallback HTML report generation"""
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #1f4788; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #1f4788; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .low-stock {{ background-color: #ffe0e0; }}
                .footer {{ margin-top: 20px; font-size: 10px; color: #666; }}
            </style>
        </head>
        <body>
            <h1>Product Availability Report</h1>
            <p><strong>Order:</strong> {sale_order.name} | <strong>Partner:</strong> {sale_order.partner_id.name}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <table>
                <tr>
                    <th>SKU</th>
                    <th>Product Name</th>
                    <th>Ordered Qty</th>
                    <th>Stock On Hand</th>
                    <th>Available</th>
                    <th>Status</th>
                </tr>
        """
        
        for item in availability_data:
            stock_str = str(item.get('stock_on_hand', '***'))
            display_str = str(item.get('display_qty', '***'))
            status = 'IN STOCK' if not item.get('is_insufficient') else 'LOW STOCK'
            row_class = 'low-stock' if item.get('is_insufficient') else ''
            
            html += f"""
                <tr class="{row_class}">
                    <td>{item.get('sku', '')}</td>
                    <td>{item.get('product_name', '')}</td>
                    <td>{item.get('ordered_qty', '')}</td>
                    <td>{stock_str}</td>
                    <td>{display_str}</td>
                    <td>{status}</td>
                </tr>
            """
        
        html += """
            </table>
            <div class="footer">
                <p><em>Stock levels masked based on user permissions.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
