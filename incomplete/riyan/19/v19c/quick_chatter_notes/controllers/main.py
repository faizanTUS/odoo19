# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http
from odoo.http import request

class QuickChatterNotesController(http.Controller):

    @http.route('/quick_chatter_notes/fetch', type='json', auth='user')
    def fetch_quick_notes(self):
        user = request.env.user
        QuickNote = request.env['quick.chatter.note'].sudo()

        notes = QuickNote.search([
            '|',
            ('global_note', '=', True),
            ('user_id', '=', user.id),
        ])

        return [
            {
                'id': note.id,
                'name': note.name,
                'content': note.content,
            }
            for note in notes
        ]
