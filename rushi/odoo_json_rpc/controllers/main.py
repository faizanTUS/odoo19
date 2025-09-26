# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import logging
from odoo import http
from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.addons.web.controllers.dataset import DataSet
import json
from odoo.tools import date_utils
_logger = logging.getLogger(__name__)
from odoo.modules.registry import Registry
_logger = logging.getLogger(__name__)


class OdooAPI(DataSet):

    @http.route('/json-call/user_authenticate', type='json', auth="public",csrf=False)
    def user_authenticate(self, **post):
        print ("post>>>>>", post)
        if not post:
            return {'error': 'Please send data to Odoo.'}
        if not post.get('login'):
            return {'error': 'Please send login.'}
        if not post.get('password'):
            return {'error': 'Please send password.'}
        if not post.get('db'):
            return {'error': 'Please send database.'}
        # uid = request.session.authenticate(str(post.get('db')), str(post.get('login')), str(post.get('password')))
        credential = {'db': str(post.get('db')), 'login': str(post.get('login')), 'password': str(post.get('password')),'type': 'password'}
        uid = request.session.authenticate(request.env, credential)
        # uid = request.session.authenticate(str(post.get('db')), {'type': "password",'login': str(post.get('login')), 'password': str(post.get('password'))})
        print ("uid>>>>>",uid)
        if not uid:
            return {'error': 'There is no user found! Please check your credentials.'}
        user = request.env['res.users'].sudo().browse([uid.get('uid')])
        get_admin_token = request.env['jsonrpc.token'].sudo().search_read([('user_id', '=', 2)], ['token'])
        get_user_token = request.env['jsonrpc.token'].sudo().create({
            'user_id': uid.get('uid'),
            'actived': True,
            'reg_remote_addr_uses': True,
            'url':'/json-call'
        })
        get_user_token.generate_token()

        # return {'token': get_user_token.token, 'uid': uid,'company_ids': user.company_ids.ids, 'partner_id': user.partner_id.id}
        res = {'token': get_user_token.token, 'uid': uid.get('uid'), 'company_ids': user.company_ids.ids,'partner_id': user.partner_id.id}
        if get_admin_token:
                       res.update({
                               'admin_token': get_admin_token[0].get('token')
                                                })
        return res

    @http.route(['/json-call/user_logout'], type='json', auth="public", csrf=False)
    def user_logout(self, **post):

        if not post:
            return {'error': 'Please send data to Odoo.'}
        if not post.get('token'):
            return {'error': 'Please send token.'}

        check_token = request.env['jsonrpc.token'].sudo().search(
            [('token', '=', str(post.get('token')))])
        if check_token:
            check_token.sudo().unlink()

        return True

    @http.route(['/json-call'], type='json', auth="public", jsonrpctoken=True, csrf=False)
    def jsonrpc_method(self, **post):
        model = ''
        method = ''
        if post.get('model') and post.get('method'):
            model = post.get('model')
            method = post.get('method')
        else:
            return {'error':'Model or Method is missing or wrong'}
        res = self.call_kw(model, method, post.get('args') or [[]], post.get('context') or {})
        print("ressssssssssssssssssssssssssssssssssssskkkkkkkkkkkkkkkkkkkkkkkkkkkkk",res)
        if model == "res.users" and method in ("search", "search_read", "read"):
            for r in res:
                user_id = request.env['res.users'].search([('id', '=', r["id"])])
                if user_id:
                    partner_list = []
                    for user in user_id:

                        res_partner = request.env['jsonrpc.token'].get_user_details(user)
                        partner_list.append(res_partner)
                    r.update({'user_details' : partner_list})
        return res

class APIAll(http.Controller):

    @http.route('/json-call/product_category_list', type='http', auth='public', methods=['GET','POST'], csrf=False, website=True)
    def product_category_list(self, **post):
        res = {}
        lst = []
        for category in request.env['product.category'].sudo().search([]):
            lst.append({'cat_id': category.id,
                        'cat_name':category.display_name,
                        'product_count':category.product_count,
                        })
        res['status'] = True
        res['message'] = "Data available"
        res['data'] = lst
        return json.dumps(res)

    @http.route('/json-call/product_brand_list', type='http', auth="public", csrf=False)
    def product_brand_list(self, **post):
        res = {}
        lst = []
        for brand in request.env['product.brand'].sudo().search([]):
            lst.append({'brand_id': brand.id, 'brand_name': brand.brand_name,
                        'product_count': brand.product_count,
                        })
        res['status'] = True
        res['message'] = "Data available"
        res['data'] = lst
        return json.dumps(res)

    @http.route('/json-call/product_list', type='http', methods=['GET', 'POST'], auth="public", csrf=False)
    def product_list(self, **post):
        res = {}
        lst = []
        if post.get('page') and post.get('product_count'):
            limit = 0
            if int(post.get('page')) == 1:
                offset = 0
            else:
                offset = ((int(post.get('page')) - 1)) * int(post.get('product_count'))
            limit = int(post.get('product_count'))
            products = request.env['product.product'].with_user(request.env['res.users'].browse(2)).with_context(allowed_company_ids=[1]).search_read([],offset=int(offset), limit=limit, order='id asc')
            for i in products:
                tax_data = []
                for tax in i.get('taxes_id'):
                    tax_dict_vals = request.env['account.tax'].with_user(
                        request.env['res.users'].browse(2)).with_context(allowed_company_ids=[1]).search_read([['id','=',tax]],['id','name','amount'],order='id asc')
                    if tax_dict_vals:
                        tax_data.append(tax_dict_vals[0])

                i['tax_data'] = tax_data
            res['status'] = True
            res['message'] = "Data available"
            res['page'] = int(post.get('page'))
            res['data'] = products

            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Missing page or product_count"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/product_sort_list', type='http', auth="public", csrf=False)
    def product_sort_list(self, **post):
        res = {}
        if post.get('page') and post.get('product_count'):
            if int(post.get('page')) == 1:
                offset = 0
            else:
                offset = ((int(post.get('page')) - 1)) * int(post.get('product_count'))
            limit = int(post.get('product_count'))
            if post.get('sort') or post.get('latest'):
                if post.get('sort') == 'a-z':
                    if post.get('latest'):
                        products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='name asc,id desc')
                    else:
                        products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='name asc')
                elif post.get('sort') == 'z-a':
                    if post.get('latest'):
                        products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='name desc,id desc')
                    else:
                        products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='name desc')
                else:
                    if post.get('latest'):
                        products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='id desc')
                    else:
                        products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='id asc')
            else:
                products = request.env['product.product'].sudo().search_read([], offset=offset, limit=limit, order='id asc')
            res['status'] = True
            res['message'] = "Data available"
            res['page'] = int(post.get('page'))
            res['data'] = products
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Missing page or product_count"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/product_filter', type='http', auth="public", csrf=False)
    def product_filter(self, **post):
        res = {}
        lst = []
        if post.get('page') and post.get('product_count'):
            if int(post.get('page')) == 1:
                offset = 0
            else:
                offset = ((int(post.get('page')) - 1)) * int(post.get('product_count'))
            limit = int(post.get('product_count'))
            domain = []
            if post.get('categ_id'):
                domain += [('categ_id','=',int(post.get('categ_id')))]
            if post.get('brand_id'):
                domain += [('brand_id','=',int(post.get('brand_id')))]
            if post.get('price_start'):
                domain += [('list_price','>=',float(post.get('price_start')))]
            if post.get('price_end'):
                domain += [('list_price', '<=', float(post.get('price_end')))]
            products = request.env['product.product'].sudo().search_read(domain, offset=offset, limit=limit, order='id asc')
            if len(products) > 0:
                res['status'] = True
                res['message'] = "Data available"
                res['page'] = int(post.get('page'))
                res['data'] = products
                return json.dumps(res, default=date_utils.json_default)
            else:
                res['status'] = False
                res['message'] = "Data Unavailable"
                return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Missing page or product_count"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/get_product_by_pincode', type='http', auth="public", csrf=False)
    def get_product_by_pincode(self, **post):
        res = {}
        lst = []
        if post.get('pincode') and post.get('product_id') and post.get('qty'):
            for pin in request.env['pin.code.info'].sudo().search([('pin_code','=',int(post.get('pincode')))]):
                available_quantity = sum(request.env['stock.quant'].sudo().search([('company_id', '=', pin.company_id.id),('product_id','=',int(post.get('product_id')))]).mapped(
                    'available_quantity'))
                if available_quantity > 0:
                    if float(post.get('qty')) <= available_quantity:
                        lst.append({'mart_id': pin.company_id.id, 'mart_name': pin.company_id.name})
            if len(lst) > 0:
                res['status'] = True
                res['message'] = "Data available"
                res['data'] = lst
                return json.dumps(res, default=date_utils.json_default)
            else:
                res['status'] = False
                res['message'] = "we are not delivering to this pincode now"
                return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Missing pincode or product or Quantity"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/create_order', auth='public', csrf=False, type='http')
    def create_order(self, **post):
        res = {}
        lst = []
        currency = request.env.ref('base.main_company').currency_id
        if post:
            try:
                lst_convert = list(eval(post.get('line_data')))
                partner = request.env['res.partner'].sudo().search([('phone', '=', str(post.get('phone'))),('phone','!=',False)])
                if not partner:

                    country = request.env['res.country'].search([('name','=ilike',post.get('country'))])
                    state = request.env['res.country.state'].search([('name','=ilike',post.get('state'))])
                    partner = request.env['res.partner'].sudo().create({
                        'customer_rank':1,
                        'name': post.get('name'),
                        'email':post.get('email'),
                        'phone':post.get('phone'),
                        'company_name':post.get('company_name') if post.get('company_name') else "",
                        'vat':post.get('gst') if post.get('gst') else "",
                        'street':post.get('street'),
                        'street2':post.get('street2'),
                        'zip':post.get('zip'),
                        'city':post.get('city'),
                        'country_id':country.id,
                        'state_id':state.id,
                    })
                if partner:

                    so = request.env['sale.order'].sudo().create({
                        'partner_id': partner.id,
                        'website_id': 1,
                        'company_id': int(post.get('mart_id')),
                        'order_line': [(0, 0, {
                            'product_id': int(line.get('product_id')),
                            'product_uom_qty': line.get('product_quantity'),
                            'price_unit': line.get('payble_amount'),
                        })for line in lst_convert]
                    })
                    transac = request.env['payment.transaction'].sudo().create({
                        'reference':so.name,
                        'acquirer_id':14,
                        'amount':so.amount_total,
                        'currency_id':currency.id,
                        'sale_order_ids':[(4,so.id)]
                    })

                if so:
                    if transac:
                        lst.append({'tranasaction_id': transac.id, 'payment_mode': transac.acquirer_id.name})
                    res['status'] = True
                    res['message'] = 'order created'
                    res['order_id'] = so.id
                    res['payment_details'] = lst
                    res['customer_details'] = partner.id
                    res['mart_id'] = int(post.get('mart_id'))
                    res['shipping_address'] = (so.partner_shipping_id.street) if so.partner_shipping_id.street else '' + ' ' + (so.partner_shipping_id.street2)if so.partner_shipping_id.street2 else '' + ' ' + (so.partner_shipping_id.city) if so.partner_shipping_id.city else '' + ' ' + (so.partner_shipping_id.state_id.name) if so.partner_shipping_id.state_id else '' + ' ' + (so.partner_shipping_id.country_id.name) if so.partner_shipping_id.country_id else ''
                    return json.dumps(res)
            except:
                res['status'] = False
                res['message'] = 'Some thing went wrong please check product_id,mart_id exist or not'
                return json.dumps(res)

    @http.route('/json-call/pincode_mapping', auth='public', csrf=False, type='http')
    def pincode_mapping(self, **post):
        res = {}
        companies =[]

        res_company = request.env['res.company'].sudo().search([])
        if res_company:
            for rec in res_company:
                if rec.pin_code_ids:
                    company = {}
                    company['company_id'] = rec.id
                    company['company_name'] = rec.name
                    pincode =[]
                    for pin in rec.pin_code_ids:
                        pincode.append((pin.id,pin.pin_code,pin.village.name))
                        company['pincode'] = pincode
                    companies.append(company)


            if companies:
                res['status'] =True
                res['message'] ='Data Available'
                res['data'] = companies
            else:
                res['status'] = False
                res['message'] = 'Data Not Available'

            return json.dumps(res)

    @http.route('/json-call/vendors', auth='public', csrf=False, type='http')
    def get_vendor(self, **post):
        res = {}
        vendors = request.env['res.partner'].sudo().search_read([('user_ids','=',False),('supplier_rank','>=',1)])
        if len(vendors) > 0:
            res['status'] = True
            res['message'] = "Data available"
            res['data'] = vendors
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Data Unavailable"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/vendors_po', auth='public', csrf=False, type='http')
    def get_vendor_po(self, **post):
        res = {}

        vendors = request.env['res.partner'].sudo().search([('user_ids', '=', False), ('supplier_rank', '>=', 1)])
        for partner in vendors:
            po = request.env['purchase.order'].sudo().search_read([('partner_id','=',partner.id)])

            for line in po:
                lines = request.env['purchase.order.line'].sudo().search_read([('id', 'in', line.get('order_line'))])
                line['order_line'] = lines

        if len(po) > 0:
            res['status'] = True
            res['message'] = "Data available"
            res['data'] = po
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Data Unavailable"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/order_history', type='http', auth="public", csrf=False)
    def get_order_history(self, **post):
        res = {}
        if int(post.get('mobile')):
            id = 0
            char_to_replace = {' ':'','"':'',"'":'','-':''}
            for partner in request.env['res.partner'].sudo().search([]):
                phone = str(partner.phone)
                for key, value in char_to_replace.items():
                    phone = phone.replace(key, value)

                if phone.find('/') == 10:
                    if phone[0:10] == str(post.get('mobile'))[-10:]:
                        phone = phone[0:10]
                        id = int(partner.id)
                    if phone[11:] == str(post.get('mobile'))[-10:]:
                        phone = phone[11:]
                        id = int(partner.id)
                else:
                    if str(post.get('mobile'))[-10:] == phone[-10:]:
                        phone = phone[-10:]
                        id = int(partner.id)
                # if str(post.get('mobile'))[-10:] == str(partner.phone).replace(" ", "")[-10:]:
                #     id = int(partner.id)

            so = request.env['sale.order'].sudo().search_read([('partner_id','=',id), ('website_id', '!=', False)])

            for line in so:
                lines = request.env['sale.order.line'].sudo().search_read(
                    [('id', 'in', line.get('order_line'))])
                line['order_line'] = lines

        if len(so) > 0:
            res['status'] = True
            res['message'] = "Data available"
            res['data'] = so
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Data Unavailable"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/order_id', auth='public', csrf=False, type='http')
    def get_order_id(self, **post):
        res = {}
        if post.get('id'):
            so = request.env['sale.order'].sudo().search_read([('id','=',int(post.get('id'))), ('website_id', '!=', False)])
            for line in so:
                lines = request.env['sale.order.line'].sudo().search_read([('id', 'in', line.get('order_line'))])
                line['order_line'] = lines

        if len(so) > 0:
            res['status'] = True
            res['message'] = "Data available"
            res['data'] = so
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Data Unavailable"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/mart_wise_product_data', auth='public', csrf=False, type='http')
    def mart_wise_product_data(self, **post):
        res = {}
        lst = []
        marts = request.env['res.company'].sudo().search([('company_type','!=','super_mart')], order='id asc')
        for company in marts:
            if company.partner_id.user_ids:
                products = request.env['stock.valuation.layer'].sudo().read_group([('company_id','=',company.id)], fields=['product_id','quantity'], groupby='product_id')
                lst.append({'mart_company_id': company.id,
                            'mart_partner_name': company.name,
                            'mart_user_name': company.email,
                            'mart_partner_id': company.partner_id.id,
                            'products': [{'product_id':product.get('product_id')[0],
                                          'product_name':request.env['product.product'].sudo().browse(product.get('product_id')[0]).display_name,
                                          'qty_available':product.get('quantity'),
                                          'selling_price':request.env['product.product'].sudo().browse(product.get('product_id')[0]).lst_price,
                                          }for product in products]})
        res['status'] = True
        res['message'] = "Data Available"
        res['data'] = lst
        return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/all_orders', auth='public', csrf=False, type='http')
    def get_all_orders(self, **post):
        res = {}
        so = request.env['sale.order'].sudo().search_read(
            [('website_id', '!=', False)])

        for line in so:
            lines = request.env['sale.order.line'].sudo().search_read([('id', 'in', line.get('order_line'))])
            parter_shipp = request.env['res.partner'].sudo().browse(line.get('partner_shipping_id')[0])
            line['shipping_address'] = (parter_shipp.street) if parter_shipp.street else '' + ' ' + (parter_shipp.street2)if parter_shipp.street2 else '' + ' ' + (parter_shipp.city) if parter_shipp.city else '' + ' ' + (parter_shipp.state_id.name) if parter_shipp.state_id else '' + ' ' + (parter_shipp.country_id.name) if parter_shipp.country_id else ''

            line['order_line'] = lines
            partner = request.env['res.partner'].sudo().browse((line.get('partner_id')[0]))
            if partner:
                line['mobile'] = partner.mobile if partner.mobile else partner.phone
            else:
                line['mobile'] = ''
        if len(so) > 0:
            res['status'] = True
            res['message'] = "Data available"
            res['data'] = so
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Data Unavailable"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/all_active_marts', auth='public', csrf=False, type='http')
    def get_all_active_marts(self, **post):
        res = {}
        lst = []
        companies = request.env['res.company'].sudo().search(
            [('id', '!=', 1)])

        for company in companies:

            lst.append({
                'mart_id': company.id,
                'mart_name': company.name,
                'mart_pincode': company.zip,
                'mart_email': company.email,
                'mart_mobile': company.phone,

            })
        if len(companies) > 0:
            res['status'] = True
            res['message'] = "Data Available"
            res['data'] = lst
            return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Data Not Available"
            return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/validate_cart', auth='public', csrf=False, type='http')
    def validate_cart(self, **post):
        res = {}
        lst = []
        if post:
            try:
                lst_convert = list(eval(post.get('line_data')))
                mart_id = int(post.get('mart_id'))
                if (mart_id):
                    for line in lst_convert:
                        products = request.env['stock.valuation.layer'].sudo().read_group([('company_id','=',mart_id),('product_id','=',int(line.get('product_id')))], fields=['product_id','quantity'], groupby='product_id')
                        if products:
                            for product in products:
                                lst.append({'product_id': product.get('product_id')[0],
                                            'qty_available': product.get('quantity'),
                                            'is_available': True if int(product.get('quantity')) >= int(line.get('product_quantity')) else False,
                                            })
                        else:
                            lst.append({'product_id': int(line.get('product_id')),
                                        'qty_available': 0.0,
                                        'is_available': False,
                                        })
                    res['status'] = True
                    res['message'] = "Data Available"
                    res['data'] = lst
                    return json.dumps(res, default=date_utils.json_default)
            except:
                res['status'] = False
                res['message'] = "Something Went Wrong"
                return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/get_mart_partner_data_for_bank', auth='public', csrf=False, type='http')
    def get_mart_partner_data_for_bank(self, **post):
        res = {}
        token = post.get('token')

        if not token:
            res['status'] = False
            res['message'] = {'error': 'Please send token.'}
            return json.dumps(res, default=date_utils.json_default)

        else:
            check_token = request.env['jsonrpc.token'].sudo().search(
                [('token', '=', str(token))])
            if not check_token:
                return {'error': 'Invalid token.'}
            else:
                companies = request.env['res.company'].sudo().search_read(
                    [('id', '!=', 1)])

                if len(companies) > 0:
                    res['status'] = True
                    res['message'] = "Data available"
                    res['data'] = companies
                    return json.dumps(res, default=date_utils.json_default)
                else:
                    res['status'] = False
                    res['message'] = "Data Unavailable"
                    return json.dumps(res, default=date_utils.json_default)

    @http.route('/json-call/mart_wise_inventory_data', auth='public', csrf=False,methods=['GET'] ,type='http', cors='*' )
    def mart_wise_inventory_data(self, **post):
        res = {}
        lst = []
        if post:
            if post.get('mart_id'):
                lst_convert = list(eval(post.get('mart_id')))
                for records in lst_convert:
                    marts = request.env['res.company'].sudo().search([('id', '=', records)])
                    for company in marts:
                        if company.partner_id.user_ids:
                            products = request.env['stock.valuation.layer'].sudo().read_group([('company_id', '=', company.id)],
                                                                                              fields=['product_id', 'quantity','value','unit_cost'],
                                                                                              groupby='product_id')
                            lst.append({'mart_company_id': company.id,
                                        'mart_partner_name': company.name,
                                        'mart_user_name': company.email,
                                        'mart_partner_id': company.partner_id.id,
                                        'products': [{'product_id': product.get('product_id')[0],
                                                      'product_name': request.env['product.product'].sudo().browse(product.get('product_id')[0]).display_name,
                                                      # 'unit_cost': product.get('unit_cost'),
                                                      'product_qty': product.get('quantity'),
                                                      'value': product.get('value'),
                                                      } for product in products]})
                        res['status'] = True
                        res['message'] = "Data Available"
                        res['data'] = lst
                        return json.dumps(res, default=date_utils.json_default)
            else:
                res['status'] = False
                res['message'] = "Mart Id Required"
                return json.dumps(res, default=date_utils.json_default)

        else:
            res['status'] = False
            res['message'] = "Mart Id Required"
            return json.dumps(res, default=date_utils.json_default)


    @http.route('/json-call/get_sathi_details', auth='public', csrf=False, type='http', cors='*', methods=['GET'])
    def get_sathi_details(self, **post):
        res = {}
        lst = []
        if post:
            if post.get('email'):
                lst_convert = list(eval(post.get('email')))
                for records in lst_convert:
                    sathi = request.env['res.sathi'].sudo().search([('email', '=', records)])

                    if sathi:
                        for rec in sathi:
                            pos_obj = request.env['pos.order'].sudo().search([('company_id', 'in', rec.company_ids.ids)])
                            target_achieved = (sum(pos_obj.mapped('amount_total')))
                            lst.append({
                                'sathi_id': sathi.id,
                                'sathi_name': sathi.name,
                                'mart_id': sathi.company_ids.id or " ",
                                'mart_name': sathi.company_ids.name or " ",
                                'target_amount': sathi.target ,
                                'target_achieved': round(target_achieved,2)})

                        res['status'] = True
                        res['message'] = "Data Available"
                        res['data'] = lst
                        return json.dumps(res, default=date_utils.json_default)
                    else:
                        res['status'] = False
                        res['message'] = "Sathi doesn't exist for this email"
                        return json.dumps(res, default=date_utils.json_default)

            else:
                res['status'] = False
                res['message'] = "Email Id Required"
                return json.dumps(res, default=date_utils.json_default)
        else:
            res['status'] = False
            res['message'] = "Email Id Required"
            return json.dumps(res, default=date_utils.json_default)


