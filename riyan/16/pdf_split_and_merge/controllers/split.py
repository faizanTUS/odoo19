# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http
from odoo.http import request
import base64
import fitz
import io
from PIL import Image

class PdfSplitController(http.Controller):

    @http.route('/pdf_split/load_pages', type='json', auth='user')
    def load_pages(self, document_id, **kwargs):
        try:
            doc = request.env['pdf.split.document'].browse(int(document_id))
            if not doc.exists() or not doc.pdf_file:
                return {'error': 'Document not found or invalid'}

            pdf_data = base64.b64decode(doc.pdf_file)
            pdf = fitz.open(stream=pdf_data, filetype='pdf')
            pages = []

            for i in range(len(pdf)):
                page = pdf.load_page(i)
                pix = page.get_pixmap(dpi=120, alpha=False)
                img_bytes = io.BytesIO()
                Image.frombytes("RGB", [pix.width, pix.height], pix.samples) \
                    .save(img_bytes, format='JPEG', quality=85)

                img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
                data_url = f"data:image/jpeg;base64,{img_base64}"

                pages.append({
                    'number': i + 1,
                    'preview_url': data_url,
                    'width': pix.width,
                    'height': pix.height
                })
            return {'pages': pages}
        except Exception as e:
            return {'error': f'Error processing PDF: {str(e)}'}

    @http.route('/pdf_split/split_selected', type='json', auth='user')
    def split_selected(self, document_id, selected_pages, **kwargs):
        try:
            doc = request.env['pdf.split.document'].browse(int(document_id))
            if not doc.exists() or not doc.pdf_file:
                return {'success': False, 'error': 'Document not found or invalid'}

            pdf_bytes = base64.b64decode(doc.pdf_file)
            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(pdf_doc)

            doc.split_ids.unlink()

            for page_num in map(int, selected_pages):
                if page_num < 1 or page_num > total_pages:
                    continue

                page_index = page_num - 1
                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf_doc, from_page=page_index, to_page=page_index)
                filename = f"{page_num}.pdf"
                request.env['pdf.split.result'].create({
                    'name': filename,
                    'document_id': doc.id,
                    'split_file': base64.b64encode(new_pdf.tobytes()),
                })

            doc.state = 'split'
            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}
