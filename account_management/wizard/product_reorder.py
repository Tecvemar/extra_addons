# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc
import time

class product_sorting(osv.osv_memory):

    def reorder(self, cr, uid, ids, context=None):
        print 'context entrando, ', context
        product_obj = self.pool.get('product.product')
        categ_obj = self.pool.get('product.category')
        obj_model = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        form = self.read(cr, uid, ids, [])[0]
        if not form['product_ids']:
            raise osv.except_osv(_('UserError'), _('You must select products to reorder'))
        vals = {
        'categ_id' : form['categ_id'],
        }
        if not form['acc_prod_id']:
            if categ_obj.browse(cr, uid, form['categ_id']).acc_prod_id:
                vals.update({'acc_prod_id': categ_obj.browse(cr, uid, form['categ_id']).acc_prod_id.id})
            else:
                raise osv.except_osv(_('UserError'), _("The Category You have selected lacks of Accounting Category \n Solve the problem in the Category or Select an Accounting Category"))
        else:
            vals.update({'acc_prod_id' : form['acc_prod_id']})
        
        if not form.get('override_unique',False):
            vals.update({'unique_account' : categ_obj.browse(cr, uid, form['categ_id']).unique_account})
        else:
            vals.update({
            'unique_account' : form.get('unique_account',False),
            'purchase_ok' : form.get('purchase_ok',False),
            'sale_ok' : form.get('sale_ok',False),
            'type' : form.get('type',False),
            })


        partial = 0
        for prod_id in form['product_ids']:
            partial+=1
            total = len(form['product_ids'])
            print '%s/%s'%(partial,total)
            product_obj.write(cr, uid, prod_id, vals)
            

        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','product_sorting_view')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']

        return{
            'domain': "[]",
            'target': 'new',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'product.sorting',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window'
                    }

    _name = "product.sorting"
    _description = "Product Sorting"
    _columns = {
        'product_ids': fields.many2many('product.product', 'product_product_rel','sort_id','product_id','Products'),
        'categ_id': fields.many2one('product.category','Category', required=True),
        'acc_prod_id': fields.many2one('account.product','Accounting Category'),
        'purchase_ok': fields.boolean('Can be Purchased'),
        'sale_ok': fields.boolean('Can be sold'),
        'type': fields.selection([('product','Stockable Product'),('consu', 'Consumable'),('service','Service')], 'Product Type', required=True, help="Will change the way procurements are processed. Consumables are stockable products with infinite stock, or for use when you have no stock management in the system."),
        'unique_account':fields.boolean(
            'Require Unique Account', 
            help='Selecting this field allow you to create Unique Accounts for this Record, Taking into Account the Accounting Classification, not doing so, Will asign those ones in the Product Category' ),
        'override_unique':fields.boolean(
            'Override Unique Account Requirement', 
            help='Selecting this field will allow you to override the Unique Account Requirement set in the Product Category for these Records' ),
        'progress':fields.float(string='Progress', readonly=True,digits_compute= dp.get_precision('Progress')),
    }

product_sorting()
