# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class MultipleUserSelection(models.TransientModel):
    _name = 'multiple.user.selection'
    _description = 'Multiple User Selection'

    user_ids = fields.Many2many('res.users', string='Users', domain="[('linkedin_token', '!=', False)]")
    post_type = fields.Selection(
        [('share_post', 'Share Post'), ('share_article', 'Share Article'), ('share_image_post', 'Share Image Post')],
        string='Select Post Type', default='share_post')

    def post_multiple_user_post_linkedin(self):
        if self._context.get('active_id'):
            active_record = self.env['hr.job'].browse(self._context.get('active_id'))
            for user in self.user_ids:
                if self.post_type == 'share_post':
                    active_record.share_linkedin(user)
                elif self.post_type == 'share_article':
                    active_record.share_linkedin_article(user)
                elif self.post_type == 'share_image_post':
                    active_record.share_linkedin_image(user)
        return True