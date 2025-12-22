# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http
from odoo.http import request
import base64
import fitz
import io
import time
from PIL import Image


class PdfMergeController(http.Controller):
    @http.route('/pdf_merge/load_data', type='json', auth='user')
    def load_data(self, document_id, **kwargs):
        try:
            doc = request.env['pdf.split.document'].browse(int(document_id))
            result = {
                'original_pages': [],
                'split_files': []
            }

            if doc.pdf_file:
                pdf_data = base64.b64decode(doc.pdf_file)
                pdf = fitz.open(stream=pdf_data, filetype='pdf')
                for i in range(len(pdf)):
                    page = pdf.load_page(i)
                    pix = page.get_pixmap(dpi=120, alpha=False)
                    img_bytes = io.BytesIO()
                    Image.frombytes("RGB", [pix.width, pix.height], pix.samples) \
                        .save(img_bytes, format='JPEG', quality=85)
                    img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
                    result['original_pages'].append({
                        'number': i + 1,
                        'preview_url': f"data:image/jpeg;base64,{img_base64}"
                    })

            for split in doc.split_ids:
                pdf_data = base64.b64decode(split.split_file)
                pdf = fitz.open(stream=pdf_data, filetype='pdf')
                for i in range(len(pdf)):
                    page = pdf.load_page(i)
                    pix = page.get_pixmap(dpi=120, alpha=False)
                    img_bytes = io.BytesIO()
                    Image.frombytes("RGB", [pix.width, pix.height], pix.samples) \
                        .save(img_bytes, format='JPEG', quality=85)
                    img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
                    result['split_files'].append({
                        'id': split.id,
                        'name': split.name,
                        'number': i + 1,
                        'preview_url': f"data:image/jpeg;base64,{img_base64}"
                    })

            return result
        except Exception as e:
            return {'error': f'Error loading data: {str(e)}'}

    @http.route('/pdf_merge/process_uploaded_file', type='json', auth='user')
    def process_uploaded_file(self, file_name, file_content, document_id, start_page, **kwargs):
        try:
            pdf_data = base64.b64decode(file_content)
            pdf = fitz.open(stream=pdf_data, filetype='pdf')
            pages = []

            for i in range(len(pdf)):
                page = pdf.load_page(i)
                pix = page.get_pixmap(dpi=120, alpha=False)
                img_bytes = io.BytesIO()
                Image.frombytes("RGB", [pix.width, pix.height], pix.samples) \
                    .save(img_bytes, format='JPEG', quality=85)
                img_base64 = base64.b64encode(img_bytes.getvalue()).decode()

                single_page_pdf = fitz.open()
                single_page_pdf.insert_pdf(pdf, from_page=i, to_page=i)
                page_content = base64.b64encode(single_page_pdf.tobytes()).decode()

                pages.append({
                    'id': f"uploaded_{int(time.time())}_{i}",
                    'number': start_page + i,
                    'preview_url': f"data:image/jpeg;base64,{img_base64}",
                    'content': page_content
                })

            return {'pages': pages}
        except Exception as e:
            return {'error': f'Error processing uploaded file: {str(e)}'}

    @http.route('/pdf_merge/get_page_content', type='json', auth='user')
    def get_page_content(self, document_id, page_id, page_type, page_number, **kwargs):
        try:
            doc = request.env['pdf.split.document'].browse(int(document_id))

            if page_type == 'original':
                if not doc.pdf_file:
                    return {'error': 'Original PDF not found'}

                pdf_data = base64.b64decode(doc.pdf_file)
                pdf = fitz.open(stream=pdf_data, filetype='pdf')

                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf, from_page=page_number - 1, to_page=page_number - 1)
                return {'content': base64.b64encode(new_pdf.tobytes()).decode()}

            elif page_type == 'split':
                split = request.env['pdf.split.result'].browse(int(page_id))
                if not split.exists():
                    return {'error': 'Split file not found'}

                pdf_data = base64.b64decode(split.split_file)
                pdf = fitz.open(stream=pdf_data, filetype='pdf')

                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf, from_page=page_number - 1, to_page=page_number - 1)
                return {'content': base64.b64encode(new_pdf.tobytes()).decode()}

            return {'error': 'Invalid page type'}
        except Exception as e:
            return {'error': f'Error getting page content: {str(e)}'}

    @http.route('/pdf_merge/merge_pages', type='json', auth='user')
    def merge_pages(self, document_id, pages, **kwargs):
        try:
            doc = request.env['pdf.split.document'].browse(int(document_id))
            output_pdf = fitz.open()

            for page in pages:
                if not page.get('content'):
                    return {'success': False, 'error': f'Missing content for page {page.get("id")}'}

                pdf_data = base64.b64decode(page['content'])
                pdf = fitz.open(stream=pdf_data, filetype='pdf')
                output_pdf.insert_pdf(pdf)

            filename = f"merged_{doc.name or 'document'}"
            request.env['pdf.split.result'].create({
                'name': filename,
                'document_id': doc.id,
                'split_file': base64.b64encode(output_pdf.tobytes()),
            })

            doc.state = 'merged'
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
