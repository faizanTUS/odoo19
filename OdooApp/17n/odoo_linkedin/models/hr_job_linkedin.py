import requests
import mechanicalsoup
import shlex
import os
import subprocess
import json
import base64
from urllib.parse import urlsplit
from urllib.parse import parse_qs
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
try:
    import mechanize
    from linkedin import linkedin
    from urllib.request import HTTPRedirectHandler as MechanizeRedirectHandler

except ImportError:
    _logger.error('Odoo module hr_linkedin_recruitment depends on the several external python package'
                  'Please read the doc/requirement.txt file inside the module.')


class HrJobShare(models.Model):
    _inherit = 'hr.job'

    update_key = fields.Boolean(string='Update Key', readonly=True)
    share_id = fields.Char(string='Sharing Post ID', readonly=True)
    article_blog_url = fields.Char(string='Job URL')
    article_blog_title = fields.Char(string='Job Title')
    article_blog_image_url = fields.Char(string='Job Image URL')
    post_type = fields.Selection(
        [('share_post', 'Share Post'), ('share_article', 'Share Article'), ('share_image_post', 'Share Image Post')],
        string='Select Post Type', default='share_post')
    description = fields.Text(string='Job Description', sanitize_attributes=False)
    automate_post = fields.Boolean('Automate post')
    post_date = fields.Date('Date to Post')
    multiple_user_share_ids = fields.One2many('res.users.share.id', 'job_id', string="Multiple users linkedin share")
    user_ids = fields.Many2many('res.users','res_users_automated_post_rel',string='Share Via', domain="[('linkedin_token', '!=', False)]")

    def _send_linkedin_post(self):
        jobs = self.env['hr.job'].search([('automate_post','=',True),('post_date', '=', fields.date.today()), ('update_key', '=', False)])
        for job in jobs:
            if job.post_type == 'share_post':
                for user in job.user_ids:
                    job.share_linkedin(user)
            elif job.post_type == 'share_article':
                for user in job.user_ids:
                    job.share_linkedin_article(user)
            elif job.post_type == 'share_image_post':
                for user in job.user_ids:
                    job.share_linkedin_image(user)

    def share_linkedin(self,user=False):
        """ Button function for sharing post """
        if not user:
            user = self.env.user
        credential_dict = self.get_authorize(user)
        access_token = credential_dict['access_token']
        linkedin_credential = credential_dict['linkedin_credential']
        share_data = {
            "author": "urn:li:person:" + linkedin_credential['profile_urn'],
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": self.description
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # URLS

        page_share_url = 'https://api.linkedin.com/v2/ugcPosts'
        if self.description:
            try:
                response = self.share_request('POST', page_share_url, access_token, data=json.dumps(share_data))
                share_response_text = response.json()
                share_response_code = response.status_code
                if share_response_code == 201:
                    r = share_response_text.get('id', {})
                    self.env['res.users.share.id'].create(
                        {'share_user_id': user.id, 'share_id': r.replace('urn:li:share:', ''), 'job_id': self.id})
                    self.update_key = True
                elif share_response_code == 404:
                    raise UserError("Resource does not exist.!")
                elif share_response_code == 409:
                    raise UserError("Already shared!")
                elif share_response_code == 422:
                    raise UserError("This Content Already Shared!")
                else:
                    raise UserError("Error!! Check your connection...")
            except Exception as e:
                raise UserError(e)
        else:
            raise UserError("Provide a Job description....")

    def share_linkedin_article(self,user=False):
        """ Button function for sharing post Article"""
        if not user:
            user = self.env.user
        credential_dict = self.get_authorize(user)
        access_token = credential_dict['access_token']
        linkedin_credential = credential_dict['linkedin_credential']
        share_data = {
            "author": "urn:li:person:" + linkedin_credential['profile_urn'],
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": self.description
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": self.article_blog_title
                            },
                            "originalUrl": self.article_blog_url,
                            "title": {
                                "text": self.article_blog_title
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # URLS

        page_share_url = 'https://api.linkedin.com/v2/ugcPosts'
        if self.description:
            try:
                response = self.share_request('POST', page_share_url, access_token, data=json.dumps(share_data))
                share_response_text = response.json()
                share_response_code = response.status_code
                if share_response_code == 201:
                    r = share_response_text.get('id', {})
                    self.env['res.users.share.id'].create(
                        {'share_user_id': user.id, 'share_id': r.replace('urn:li:share:', ''), 'job_id': self.id})
                    self.update_key = True
                elif share_response_code == 404:
                    raise UserError("Resource does not exist.!")
                elif share_response_code == 409:
                    raise UserError("Already shared!")
                elif share_response_code == 422:
                    raise UserError("This Content Already Shared!")
                else:
                    raise UserError("Error!! Check your connection...")
            except Exception as e:
                raise UserError(e)
        else:
            raise UserError("Provide a Job description....")

    def share_linkedin_image(self, user=False):
        """ Button function for sharing image post """
        if not user:
            user = self.env.user
        credential_dict = self.get_authorize(user)
        access_token = credential_dict['access_token']
        linkedin_credential = credential_dict['linkedin_credential']
        media = []
        attachments = self.env['ir.attachment'].search([('res_id', 'in', self.ids), ('res_model', '=', self._name)])
        if attachments:
            filepath = '/tmp/'
            for attachment in attachments:
                filename = attachment.name.replace(' ', '_')
                file = os.path.join(filepath, filename)

                with open(file, "wb") as imgFile:
                    imgFile.write(base64.b64decode(attachment.datas))
                '''step-1 :- Asset & Upload URL Generate '''
                share_data = {
                    "registerUploadRequest": {
                        "recipes": [
                            "urn:li:digitalmediaRecipe:feedshare-image"
                        ],
                        "owner": "urn:li:person:" + linkedin_credential['profile_urn'],
                        "serviceRelationships": [
                            {
                                "relationshipType": "OWNER",
                                "identifier": "urn:li:userGeneratedContent"
                            }
                        ]
                    }
                }
                page_share_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
                try:
                    response = self.share_request('POST', page_share_url, access_token, data=json.dumps(share_data))
                    share_response_code = response.status_code
                    if share_response_code == 200:
                        bb = response.json().get('value', {}) and response.json().get('value', {}).get('asset',
                                                                                                       {}) or False
                        if not bb:
                            raise UserError('you have a issue in image registered')
                        upload_url = response.json()['value']['uploadMechanism'][
                            'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'][
                            'uploadUrl']
                        asset = bb.replace('urn:li:digitalmediaAsset:', '')
                        '''Step-2 IMAGE Binary File Upload'''
                        curl_url = "curl -i --upload-file " + file + " --header 'Authorization: Bearer " + access_token + "' " + upload_url + " "
                        curl_command_line = '''''' + curl_url + ''''''
                        args = shlex.split(curl_command_line)
                        try:
                            response = subprocess.run(args, capture_output=True, text=True).stdout
                            if not (response.split() and response.split().index('201')):
                                raise UserError("Something Want's Wrong In Image Files Uploads")
                        except Exception as e:
                            raise UserError(e)
                        '''IMAGE Binary File Upload Status'''
                        he = {
                            'Authorization': 'Bearer ' + str(access_token),
                            'X-Restli-Protocol-Version': '2.0.0',
                            'Content-Type': 'multipart/form-data'
                        }
                        try:
                            ab = requests.get('https://api.linkedin.com/v2/assets/' + asset, headers=he)
                            status = ""
                            if ab.status_code == 200:
                                r = ab.json().get('recipes', {})
                                for ra in r:
                                    status = ra['status']
                            else:
                                raise UserError("This Asset Id Not Found System")
                            if status != "AVAILABLE":
                                raise UserError(status)
                        except Exception as e:
                            raise UserError(e)
                        media.append(
                            {
                                "status": "READY",
                                "description": {
                                    "text": "Center stage!"
                                },
                                "media": "urn:li:digitalmediaAsset:" + asset,
                                "title": {
                                    "text": "first image post"
                                }
                            }
                        )
                    else:
                        raise UserError("Error!! Check your connection...")
                    os.remove(file)
                except Exception as e:
                    raise UserError(e)
        else:
            raise UserError("Please Attached Files")

        '''Step:-3 Upload & Share Image POST'''
        payload = {
            "author": "urn:li:person:" + linkedin_credential['profile_urn'],
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": self.description
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": media
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        page_share_url = 'https://api.linkedin.com/v2/ugcPosts'
        try:
            response = self.share_request('POST', page_share_url, access_token, data=json.dumps(payload))
            if response.status_code == 201:
                r = response.json().get('id', {})
                self.env['res.users.share.id'].create(
                    {'share_user_id': user.id, 'share_id': r.replace('urn:li:share:', ''), 'job_id': self.id})
                self.update_key = True
            elif response.status_code == 404:
                raise UserError("Resource does not exist.!")
            elif response.status_code == 409:
                raise UserError("Already shared!")
            elif response.status_code == 422:
                raise UserError("This Content Already Shared!")
            else:
                raise UserError("Error!! Check your connection & Linkedin Configuration...")
        except Exception as e:
            raise UserError(e)

    def delete_post(self):
        """ Button function for sharing po7st """
        for rec in self.multiple_user_share_ids:
            credential_dict = self.get_authorize(rec.share_user_id)
            access_token = credential_dict['access_token']

            url = "https://api.linkedin.com/v2/ugcPosts/urn:li:share:" + rec.share_id
            payload = {}
            try:
                response = self.share_request('DELETE', url, access_token, data=json.dumps(payload))
                share_response_code = response.status_code
                if share_response_code == 204:
                    self.update_key = False
                    rec.unlink()
                else:
                    raise UserError("something want's wrong")
            except Exception as e:
                raise UserError(e)

    def send_draft(self):
        self.update_key = False

    @api.model
    def share_request(self, method, page_share_url, access_token, data):
        """ Function will return UPDATED KEY , [201] if sharing is OK """
        headers = {'x-li-format': 'json', 'Content-Type': 'application/json'}
        params = {}
        params.update({'oauth2_access_token': access_token})
        kw = dict(data=data, params=params, headers=headers, timeout=60)
        req_response = requests.request(method.upper(), page_share_url, **kw)
        return req_response

    @api.model
    def get_urn(self, method, has_access_url, access_token):
        """ Function will return TRUE if credentials user has the access to update """
        headers = {'x-li-format': 'json', 'Content-Type': 'application/json'}
        params = {}
        params.update({'oauth2_access_token': access_token})
        kw = dict(params=params, headers=headers, timeout=60)
        req_response = requests.request(method.upper(), has_access_url, **kw)
        return req_response

    def get_authorize(self,user):
        """ Supporting function for authenticating operations """
        linkedin_credential = {}
        linkedin_auth_provider = self.env.ref('odoo_linkedin.provider_linkedin')
        if linkedin_auth_provider.client_id and linkedin_auth_provider.client_secret:
            linkedin_credential['api_key'] = linkedin_auth_provider.client_id
            linkedin_credential['secret_key'] = linkedin_auth_provider.client_secret
        else:
            raise UserError(_('LinkedIn Access Credentials are empty.Please fill up in Auth Provider form.'))
        if user.linkedin_username:
            linkedin_credential['un'] = user.linkedin_username
        else:
            raise UserError(_('Please fill up Linkedin username User settings.'))
        if user.linkedin_password:
            linkedin_credential['pw'] = user.linkedin_password
        else:
            raise UserError(_('Please fill up Linkedin password in User settings.'))
        linkedin_suit_credent = {}
        if user.linkedin_token:
            linkedin_credential['linkedin_token'] = user.linkedin_token
            linkedin_suit_credent = {'access_token': linkedin_credential['linkedin_token']}

        else:
            # Browser Data Posting And Signing
            br = mechanicalsoup.StatefulBrowser()
            br.set_cookiejar(mechanize.CookieJar())
            return_uri = 'https://www.techultrasolutions.com/'
            linkedin_permissions = ['w_member_social', 'r_basicprofile']
            url = "https://www.linkedin.com/oauth/v2/authorization"
            payload = {
                "response_type": "code",
                "client_id": linkedin_credential['api_key'],
                "redirect_uri": return_uri,
                "state": "DCEeFWf45A53sdfKef424",
                "scope": "r_basicprofile w_member_social"
            }
            try:
                auth = linkedin.LinkedInAuthentication(linkedin_credential['api_key'],
                                                       linkedin_credential['secret_key'],
                                                       return_uri,
                                                       linkedin_permissions)
                response = requests.get(url, params=payload)
                try:
                    br.open(response.url)
                    br.select_form(selector='form', nr=0)
                    br['session_key'] = linkedin_credential['un']
                    br['session_password'] = linkedin_credential['pw']
                    br.submit_selected()
                    # noinspection PyBroadException
                    try:
                        # noinspection PyTypeChecker
                        auth.authorization_code = parse_qs(urlsplit(br.get_url()).query)['code']
                        linkedin_suit_credent = {'access_token': str(auth.get_access_token().access_token)}
                        user.write({'last_token_generate_date': fields.date.today(),
                                             'linkedin_token': linkedin_suit_credent['access_token']})
                    except:
                        br.open(br.get_url())
                        br.select_form(selector='form', nr=1)
                        br.submit_selected()
                        # noinspection PyTypeChecker
                        auth.authorization_code = parse_qs(urlsplit(br.get_url()).query)['code']
                        if not auth.authorization_code:
                            raise UserError("Please check Redirect URLs in the LinkedIn app settings!")
                        linkedin_suit_credent = {'access_token': str(auth.get_access_token().access_token)}
                        user.write({'last_token_generate_date': fields.date.today(),
                                             'linkedin_token': linkedin_suit_credent['access_token']})
                except:
                    raise UserError("Please check Redirect URLs in the LinkedIn app settings & Configuration!")
            except Exception as e:
                raise UserError(e)

        member_url = 'https://api.linkedin.com/v2/me'
        response = self.get_urn('GET', member_url, linkedin_suit_credent['access_token'])
        urn_response_text = response.json()
        linkedin_credential['profile_urn'] = urn_response_text['id']
        linkedin_suit_credent['linkedin_credential'] = linkedin_credential
        if not linkedin_credential['profile_urn']:
            raise UserError("Please Check Your Configuration")
        return linkedin_suit_credent
