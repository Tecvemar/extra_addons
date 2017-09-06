# -*- encoding: utf-8 -*-
##############################################################################
#
#    VAUXOO, C.A.
#    Copyright (C) VAUXOO, C.A. (<http://www.vauxoo.com>). All Rights Reserved
#    humbertoarocha@gmail.com
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
from osv import osv
from osv import fields
from tools.translate import _
from tools import config

#~ from random import randrange
from datetime import datetime

__AYUDA__ = '''
Escriba el Patron de las cuentas, su estructura, por ejemplo:
Clase:           1,
Grupo:           12,
Cuentas:         123,
Subcuentas:      1234,
Cuentas Aux.:    1234567
Entonces escriba:  1, 12, 123, 1234, 1234567
'''
__ACC__ = {
                'income':   ('property_account_income',                     'income',       'u_type_income',        'Incoming Account'),
                'expense':  ('property_account_expense',                    'expense',      'u_type_expense',       'Expense Account'),
                'stock_in': ('property_stock_account_input',                'stock_in',     'u_type_stock_in',      'In-Stock Account'),
                'stock_out':('property_stock_account_output',               'stock_out',    'u_type_stock_out',     'Out-Stock Account'),
                'diff':     ('property_account_creditor_price_difference',  'price_diff',   'u_type_price_diff',    'Difference Account'),
                'allowance':('property_account_allowance',                  'allowance',    'u_type_allowance',     'Allowance Account'),
                'return':   ('property_account_return',                     'return',       'u_type_return',        'Sale Return Account'),
                    }

class account_product(osv.osv):
    _name='account.product'
    _description='Clasificacion Contable de los Productos'
    _columns={
            'name':fields.char('Nombre', size=128, required = True),
            'company_id':fields.many2one('res.company', 'Compania', required=True,),

            'income':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            'expense':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            'stock_in':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            'stock_out':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            'price_diff':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            'allowance':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            'return':fields.many2one('account.account', 'Cuenta Anfitriona',  domain=[('type','=','view')],required=False),
            
            'u_type_income':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            'u_type_expense':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            'u_type_stock_in':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            'u_type_stock_out':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            'u_type_price_diff':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            'u_type_allowance':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            'u_type_return':fields.many2one('account.account.type', 'Tipo de Cuenta',required=False),
            
            'same_stock':fields.boolean('Same as Stock-in Account', help='Selecting this field indicates that uses the same account as Stock-In',),
            
            'unique_income':fields.boolean('Income Unique Account', help='Selecting this field allow you to create Unique Accounts for Incomes',),
            'unique_expense':fields.boolean('Expense Unique Account', help='Selecting this field allow you to create Unique Accounts for Expenses',),
            'unique_stock':fields.boolean('Stock Unique Account', help='Selecting this field allow you to create Unique Accounts for Stocks',),
            'unique_diff':fields.boolean('Price Diff Unique Account', help='Selecting this field allow you to create Unique Accounts for Prices Difference',),
            'unique_allowance':fields.boolean('Allow. Unique Account', help='Selecting this field allow you to create Unique Accounts for Allowances',),
            'unique_return':fields.boolean('Return Unique Account', help='Selecting this field allow you to create Unique Accounts for Sale Returns',),
    }

    def _get_account(self, cr, uid, vals, k, context=None):
        if vals.get('acc_prod_id',False):
            acc_prod_obj = self.pool.get('account.product')
            obj_cls = acc_prod_obj.browse(cr,uid,vals['acc_prod_id'], context=context)
            company_id = obj_cls.company_id.id
                
        acc_obj = getattr(obj_cls, __ACC__[k][1])
        user_type = getattr(obj_cls,__ACC__[k][2])
        
        if not acc_obj:
            note = ''' 
La Clasificacion Contable [%s]\n
no tiene una cuenta anfitriona para [%s]
'''%(obj_cls.name,__ACC__[k][3])
            raise osv.except_osv(('Atencion !'), (note))
        
        
        if not user_type:
            note = ''' 
La Clasificacion Contable [%s]\n
no tiene un tipo de cuenta para [%s]
'''%(obj_cls.name,__ACC__[k][3])
            raise osv.except_osv(('Atencion !'), (note))
        
        values =  {
                            'auto': True,
                            'name': u'%s - %s'%(acc_obj.name, vals.get('name')),
                            'user_type': user_type.id,
                            'type': 'other',
                            'company_id':company_id,
                            'currency_mode':'current',
                            'active': True,
                            'reconcile': False,
                            'parent_id':acc_obj.id,
                        }
        return self.pool.get('account.account').create(cr, uid, values, context)

account_product()

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'acc_prod_id': fields.property('account.product',
            type='many2one', relation='account.product',
            string='Product Accounting Classification', method=True, view_load=True,
            help='This account will be used to value the output stock'),
        'property_account_allowance': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Allowance Account",
            method=True,
            view_load=True,
            help="This account will be used to book Allowances when making Customer Refunds."),
        'property_account_return': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale Return Account",
            method=True,
            view_load=True,
            help="This account will be used to book Sale Returns when making Customer Refunds."),
        'unique_account':fields.boolean(
            'Require Unique Account', 
            help='Selecting this field allow you to create Unique Accounts for this Record, Taking into Account the Accounting Classification, not doing so, Will asign those ones in the Product Category' ),
    }

product_category()

class product_template(osv.osv):
    _inherit='product.template'
    _columns={
        'acc_prod_id':fields.many2one('account.product',
            'Clasificacion Contable',
            required=False,
            readonly=False),
        'unique_account':fields.boolean(
            'Require Unique Account', 
            help='Selecting this field allow you to create Unique Accounts for this Record, Taking into Account the Accounting Classification, not doing so, Will asign those ones in the Product Category' ),
        'property_account_allowance': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Allowance Account",
            method=True,
            view_load=True,
            help="This account will be used to book Allowances when making Customer Refunds."),
        'property_account_return': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale Return Account",
            method=True,
            view_load=True,
            help="This account will be used to book Sale Returns when making Customer Refunds."),
    }

    def _check_account(self, cr, uid, ids, method, context={}):
        line_obj = self.pool.get('account.move.line')
        account_ids = self.pool.get('account.account').search(cr, uid, [('id', 'child_of', ids)])
        aml = False
        if line_obj.search(cr, uid, [('account_id', 'in', account_ids)]):
            aml = True
        if not aml and self.pool.get('account.invoice.line').search(cr, uid, [('account_id', 'in', ids)]):
            aml = True
        #Checking whether the account is set as a property to any Resource
        value_reference = 'account.account,' + str(ids[0])
        prop_acc = self.pool.get('ir.property').search(cr, uid, [('value_reference','=',value_reference)], context=context)

        prop_ids = False
        if method is None:
            if len(prop_acc)>1:
                prop_ids = False
            else:
                prop_ids = prop_acc
        elif method == 'stock':
            res = []
            for x in self.pool.get('ir.property').read(cr, uid, prop_acc, ['res_id'], context):
                res.append(x['res_id'])
            if len(set(res)) <= 1:
                prop_ids =  prop_acc
        return (aml,prop_ids)

    def _search_aml(self,cr,uid,ids,acc,context=None):
        if context is None:
            context={}
        account_ids = self.pool.get('account.account').search(cr, uid, [('id', 'child_of', acc)])
        return self.pool.get('account.move.line').search(cr, uid, [('account_id', 'in', account_ids)]) and True or False

    def _search_ail(self, cr, uid, ids, acc, context=None):
        if context is None:
            context={}
        account_ids = self.pool.get('account.account').search(cr, uid, [('id', 'child_of', acc)])
        return self.pool.get('account.invoice.line').search(cr, uid, [('account_id', 'in', account_ids)]) and True or False

    def _drop_properties(self, cr, uid, ids, k, context=None):
        ir_prop_obj = self.pool.get('ir.property')
        if context is None:
            context={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']
        res_id = '%s,%s'%('product.template',ids[0])
        value = '%s,%s'%('account.account',previous_accounts[__ACC__[k][0]])
        ir_prop_ids = ir_prop_obj.search(cr, uid, [('res_id','=',res_id),('value_reference','=',value),('name','=',__ACC__[k][0])], context=context)
        ir_prop_obj.unlink(cr, uid, ir_prop_ids, context=context)
        
        return ir_prop_obj.search(cr, uid, [('value_reference','=',value)])

    def _unlink_account(self, cr, uid, ids, k, vals, context=None):
        if context is None:
            context={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']
        else:
            previous_accounts={}

        if previous_accounts.get(__ACC__[k][0],False):
            aml= self._search_aml(cr,uid,ids,[previous_accounts[__ACC__[k][0]]],context=context)
            ail= self._search_ail(cr,uid,ids,[previous_accounts[__ACC__[k][0]]],context=context)
            properties = self._drop_properties(cr,uid,ids,k,context=context)
            if not any([aml,ail,properties]):
                self.pool.get('account.account').unlink(cr,uid,[previous_accounts[__ACC__[k][0]]], context)
                return True
        return False

    def _switch_accounts(self, cr, uid, ids, k,stock_account,vals, context=None):
        prod_id = None
        if context is None:
            context={}
        if context.get('__last_update',False):
            ctx_keys = context['__last_update'].keys()
            prod_id=[int(i.split(',')[1]) for i in ctx_keys if 'product.product' in i]
            prod_id = prod_id and prod_id[0] or []
        if not prod_id:
            return False
        
        aml_obj = self.pool.get('account.move.line')
        ai_obj = self.pool.get('account.invoice')
        ail_obj = self.pool.get('account.invoice.line')
        #~ NEEDS REVIEWS
        previous_accounts={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']
        

        if stock_account in ['stock_out','stock_in']: 
            
            if stock_account == 'stock_in':
                ai_ids = ai_obj.search(cr, uid, [('type','in',['in_invoice','out_refund'])],context=context)
                aml_ids = aml_obj.search(cr, uid, [('account_id','=',previous_accounts[__ACC__[k][0]]),('product_id','=',prod_id),('debit','>',0)],context=context)
                ail_ids = ail_obj.search(cr, uid, [('account_id','=',previous_accounts[__ACC__[k][0]]),('product_id','=',prod_id),('invoice_id','in',ai_ids)],context=context)
            
            else:
                ai_ids = ai_obj.search(cr, uid, [('type','in',['out_invoice','in_refund'])],context=context)
                aml_ids = aml_obj.search(cr, uid, [('account_id','=',previous_accounts[__ACC__[k][0]]),('product_id','=',prod_id),('credit','>',0)],context=context)
                ail_ids = ail_obj.search(cr, uid, [('account_id','=',previous_accounts[__ACC__[k][0]]),('product_id','=',prod_id),('invoice_id','in',ai_ids)],context=context)
                
            for i in aml_ids:
                cr.execute('UPDATE account_move_line SET account_id = %s WHERE id = %s'%(vals[__ACC__[stock_account][0]],i))
            
            for i in ail_ids:
                cr.execute('UPDATE account_invoice_line SET account_id = %s WHERE id = %s'%(vals[__ACC__[stock_account][0]],i))
        else:
            
            aml_ids = aml_obj.search(cr, uid, [('account_id','=',previous_accounts[__ACC__[k][0]]),('product_id','=',prod_id)],context=context)
            ail_ids = ail_obj.search(cr, uid, [('account_id','=',previous_accounts[__ACC__[k][0]]),('product_id','=',prod_id)],context=context)
            
            for i in aml_ids:
                cr.execute('UPDATE account_move_line SET account_id = %s WHERE id = %s'%(vals[__ACC__[k][0]],i))
            
            for i in ail_ids:
                cr.execute('UPDATE account_invoice_line SET account_id = %s WHERE id = %s'%(vals[__ACC__[k][0]],i))
        return True 

    def _account_comparison(self, cr, uid, ids,k,vals, context=None):
        acc_prod_obj = self.pool.get('account.product')
        if vals.get('acc_prod_id',False):
            obj_cls = acc_prod_obj.browse(cr,uid,vals['acc_prod_id'], context=context)
            company_id = obj_cls.company_id.id
            acc_prod_obj = self.pool.get('account.product')
        if context is None:
            context={}
        prev={}
        if context.get('previous_accounts',False):
            prev = context['previous_accounts']
        
            #~ ELABORAR METODO DE COMPARACION PARA LAS CUENTAS DE COMPRA Y VENTA SOLAMENTE (en proceso)
            #~ SE CREARA UNO ESPECIAL PARA LAS CUENTAS DE STOCK
            #~ TODO: ESTAS ES LA COMPARACION
            #~ ╔=========================╦==============================╦=============╗
            #~ ║                         ║      UNICIDAD DE CUENTA      ║     SIN     ║
            #~ ║         CUENTAS         ╠================╦=============╣   UNICIDAD  ║
            #~ ║                         ║     UNICA      ║   NO-UNICA  ║   DE  CTAS  ║
            #~ ╠=========================╬============╦===╬=============╩=========╦===╣
            #~ ║   NULL    -->     NULL  ║    CREAR   ║ * ║           PASS        ║ * ║
            #~ ╠=========================╬============╬===╬=======================╬===╣
            #~ ║   NULL    -->     1001  ║   ASIGNA   ║ * ║          ASIGNA       ║ * ║
            #~ ╠=========================╬============╬===╬=======================╬===╣
            #~ ║   1000    -->     NULL  ║   REASIGNA ║   ║          UNLINK       ║   ║
            #~ ║                         ║    1000    ║ * ║                       ║ * ║
            #~ ╠=========================╬============╬===╬=======================╬===╣
            #~ ║   1000    -->     1001  ║    1001    ║   ║           1001        ║   ║
            #~ ║                         ║   SWITCH   ║ * ║          SWITCH       ║ * ║
            #~ ║                         ║   UNLINK   ║   ║          UNLINK       ║   ║
            #~ ╠=========================╬============╬===╬=======================╬===╣
            #~ ║   1000    -->     1000  ║    PASS    ║ * ║           PASS        ║ * ║
            #~ ╚=========================╩============╩===╩=======================╩===╝
        
        if not vals.get('type',False) == 'service':
            if vals.get('acc_prod_id',False) and getattr(obj_cls,'unique_' + str('stock' in k and 'stock' or k)) and vals.get('unique_account',False):
                
                if not vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ CREAMOS LA CUENTA
                    vals[__ACC__[k][0]] = acc_prod_obj._get_account(cr, uid, vals, k, context=context)
                elif vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ NO SE HACE NADA YA QUE LE PERMITIMOS AL USUARIO ASIGNAR LA CUENTA QUE DESEE
                    pass
                elif not vals[__ACC__[k][0]] and prev.get(__ACC__[k][0],False):
                    #~ REASIGNAMOS LA CUENTA ANTERIOR Y ASI EVITAMOS QUE EL USUARIO BORRE LA CUENTA
                    vals[__ACC__[k][0]]= prev.get(__ACC__[k][0],False)
                elif vals[__ACC__[k][0]] != prev.get(__ACC__[k][0],False):
                    #~ TODO: 
                        #~ 1.- HACER SWITCH DE LA CUENTA PREVIA A LA CUENTA ACTUAL (AML Y AIL)(PRODUCT_ID)
                        #~ 2.- HACER UN UNLIK DE PROPERTY
                        #~ 3.- INTENTAR HACER UN UNLINK DE LA CUENTA PREVIA (AML Y AIL)
                    self._switch_accounts(cr,uid,ids,k,k,vals,context=context)
                    self._unlink_account(cr,uid,ids,k,vals,context=context)

                    #~ self._drop_property_account(cr,uid,ids,k,context=context)
                    #~ pass
                elif vals[__ACC__[k][0]] == prev.get(__ACC__[k][0],False):
                    #~ EL USUARIO MANTUVO LA CUENTA 
                    pass
            else:
                if not vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ CREAMOS LA CUENTA
                    pass
                elif vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ NO SE HACE NADA YA QUE LE PERMITIMOS AL USUARIO ASIGNAR LA CUENTA QUE DESEE
                    pass
                elif not vals[__ACC__[k][0]] and prev.get(__ACC__[k][0],False):
                    #~ HACEMOS UN UNLINK DE LA CUENTA 
                    self._unlink_account(cr,uid,ids,k,vals,context=context)
                    vals[__ACC__[k][0]] = False

                elif vals[__ACC__[k][0]] != prev.get(__ACC__[k][0],False):
                    #~ TODO: 
                        #~ 1.- HACER SWITCH DE LA CUENTA PREVIA A LA CUENTA ACTUAL (AML Y AIL)(PRODUCT_ID)
                        #~ 2.- HACER UN UNLIK DE PROPERTY
                        #~ 3.- INTENTAR HACER UN UNLINK DE LA CUENTA PREVIA (AML Y AIL)
                    #~ self._drop_property_account(cr,uid,ids,k,context=context)
                    #~ pass
                    self._switch_accounts(cr,uid,ids,k,k,vals,context=context)
                    self._unlink_account(cr,uid,ids,k,vals,context=context)

                elif vals[__ACC__[k][0]] == prev.get(__ACC__[k][0],False):
                    #~ EL USUARIO MANTUVO LA CUENTA 
                    pass
        else:
            if vals.get('acc_prod_id',False) and getattr(obj_cls,'unique_' + str('stock' in k and 'stock' or k)) and vals.get('unique_account',False) and not 'stock' in k:
                if not vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ CREAMOS LA CUENTA
                    vals[__ACC__[k][0]] = acc_prod_obj._get_account(cr, uid, vals, k, context=context)
                elif vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ NO SE HACE NADA YA QUE LE PERMITIMOS AL USUARIO ASIGNAR LA CUENTA QUE DESEE
                    pass
                elif not vals[__ACC__[k][0]] and prev.get(__ACC__[k][0],False):
                    #~ REASIGNAMOS LA CUENTA ANTERIOR Y ASI EVITAMOS QUE EL USUARIO BORRE LA CUENTA
                    vals[__ACC__[k][0]]= prev.get(__ACC__[k][0],False)
                elif vals[__ACC__[k][0]] != prev.get(__ACC__[k][0],False):
                    #~ TODO: 
                        #~ 1.- HACER SWITCH DE LA CUENTA PREVIA A LA CUENTA ACTUAL (AML Y AIL)(PRODUCT_ID)
                        #~ 2.- HACER UN UNLIK DE PROPERTY
                        #~ 3.- INTENTAR HACER UN UNLINK DE LA CUENTA PREVIA (AML Y AIL)
                    self._switch_accounts(cr,uid,ids,k,k,vals,context=context)
                    self._unlink_account(cr,uid,ids,k,vals,context=context)

                    #~ self._drop_property_account(cr,uid,ids,k,context=context)
                    #~ pass
                elif vals[__ACC__[k][0]] == prev.get(__ACC__[k][0],False):
                    #~ EL USUARIO MANTUVO LA CUENTA 
                    pass
            else:
                if not vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ CREAMOS LA CUENTA
                    pass
                elif vals[__ACC__[k][0]] and not prev.get(__ACC__[k][0],False):
                    #~ NO SE HACE NADA YA QUE LE PERMITIMOS AL USUARIO ASIGNAR LA CUENTA QUE DESEE
                    pass
                elif not vals[__ACC__[k][0]] and prev.get(__ACC__[k][0],False):
                    #~ HACEMOS UN UNLINK DE LA CUENTA 
                    if not self._unlink_account(cr,uid,ids,k,vals,context=context):
                        vals[__ACC__[k][0]]= prev.get(__ACC__[k][0],False)

                elif vals[__ACC__[k][0]] != prev.get(__ACC__[k][0],False):
                    #~ TODO: 
                        #~ 1.- HACER SWITCH DE LA CUENTA PREVIA A LA CUENTA ACTUAL (AML Y AIL)(PRODUCT_ID)
                        #~ 2.- HACER UN UNLIK DE PROPERTY
                        #~ 3.- INTENTAR HACER UN UNLINK DE LA CUENTA PREVIA (AML Y AIL)
                    #~ self._drop_property_account(cr,uid,ids,k,context=context)
                    #~ pass
                    self._switch_accounts(cr,uid,ids,k,k,vals,context=context)
                    self._unlink_account(cr,uid,ids,k,vals,context=context)

                elif vals[__ACC__[k][0]] == prev.get(__ACC__[k][0],False):
                    #~ EL USUARIO MANTUVO LA CUENTA 
                    pass
        return vals

    def _account_stock_comparison(self, cr, uid, ids,vals, context=None):
        acc_prod_obj = self.pool.get('account.product')
        if vals.get('acc_prod_id',False):
            obj_cls = acc_prod_obj.browse(cr,uid,vals['acc_prod_id'], context=context)
            company_id = obj_cls.company_id.id
            acc_prod_obj = self.pool.get('account.product')
        if context is None:
            context={}
        previous_accounts={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']
      
        
        #~ ELABORAR METODO DE COMPARACION PARA LAS CUENTAS DE STOCK SOLAMENTE (en proceso)
        #~ TODO: ESTAS ES LA COMPARACION
        #~ ╔============================╤================================================╤=================╗
        #~ ║           CUENTAS          |                UNICIDAD DE CUENTA              |       SIN       ║
        #~ ║--------------┬-------------┤----------------------------------┬-------------┤                 ║
        #~ ║              |             |                UNICA             |             |     UNICIDAD    ║
        #~ ║   STOCK_IN   |  STOCK_OUT  |----------------┬-----------------|   NO-UNICA  |                 ║
        #~ ║              |             |       SAME     |    NOT SAME     |             |     DE  CTAS    ║
        #~ ╚==============╧=============╧================╧=================╧=============╧=================╝
        #~ ╔===╦==========╦=============╦============╦===╦=================╦===========================╦===╗
        #~ ║ P ║   1000   ║    1000     ║            ║   ║                 ║                           ║   ║
        #1 ║---║    \/    ║     \/      ║  REASIGNA  ║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   NULL   ║    NULL     ║            ║   ║                 ║                           ║   ║
        #~ ╠===╬==========╬=============╬============╬===╬=================╬===========================╬===╣
        #~ ║ P ║   NULL   ║    NULL     ║            ║   ║                 ║                           ║   ║
        #2 ║---║    \/    ║     \/      ║    CREAR   ║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   NULL   ║    NULL     ║            ║   ║                 ║                           ║   ║
        #~ ╠===╬==========╬=============╬============╬===╬=================╬===========================╬===╣
        #~ ║ P ║   1000   ║    1000     ║   SWITCH   ║   ║                 ║                           ║   ║
        #3 ║---║    \/    ║     \/      ║1001 -> NULL║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   1001   ║    NULL     ║UNLINK(1000)║   ║                 ║                           ║   ║
        #~ ╠===╬==========╬=============╬============╬===╬=================╬===========================╬===╣
        #~ ║ P ║   1000   ║    1000     ║  REASIGNA  ║   ║                 ║                           ║   ║
        #4 ║---║    \/    ║     \/      ║1000 -> NULL║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   1000   ║    NULL     ║            ║   ║                 ║                           ║   ║
        #~ ╠===╬==========╬=============╬============╬===╬=================╬===========================╬===╣
        #~ ║ P ║   1000   ║    1000     ║  REASIGNA  ║   ║                 ║                           ║   ║
        #5 ║---║    \/    ║     \/      ║1000 -> 1001║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   1000   ║    1001     ║UNLINK(1000)║   ║                 ║                           ║   ║
        #~ ╠===╬==========╬=============╬============╬===╬=================╬===========================╬===╣
        #~ ║ P ║   1000   ║    1000     ║   SWITCH   ║   ║                 ║                           ║   ║
        #6 ║---║    \/    ║     \/      ║UNLINK(1000)║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   1001   ║    1001     ║            ║   ║                 ║                           ║   ║
        #~ ╠===╬==========╬=============╬============╬===╬=================╬===========================╬===╣
        #~ ║ P ║   1000   ║    1000     ║  REASIGNA  ║   ║                 ║                           ║   ║
        #7 ║---║    \/    ║     \/      ║1001<->1002 ║ * ║   COMPARISON A  ║        COMPARISON B       ║   ║
        #~ ║ A ║   1001   ║    1002     ║UNLINK(1000)║   ║                 ║                           ║   ║
        #~ ╚===╩==========╩=============╩============╩===╩=================╩===========================╩===╝
    
        if not vals['type']=='service' and vals['unique_account'] and obj_cls.unique_stock:
            if obj_cls.same_stock:
                if previous_accounts.get(__ACC__['stock_out'][0]) == previous_accounts.get(__ACC__['stock_in'][0]):
                #~ CASO 1 Y 2
                    if not vals[__ACC__['stock_out'][0]] and not vals[__ACC__['stock_in'][0]]:
                        if previous_accounts.get(__ACC__['stock_out'][0],False):
                            vals[__ACC__['stock_in'][0]] = previous_accounts.get(__ACC__['stock_out'][0],False)
                            vals[__ACC__['stock_out'][0]] = vals[__ACC__['stock_in'][0]]
                        else:
                            vals[__ACC__['stock_in'][0]] = acc_prod_obj._get_account(cr, uid, vals,'stock_in', context=None)
                            vals[__ACC__['stock_out'][0]] = vals[__ACC__['stock_in'][0]]

                #~ CASO 3 Y 4
                    elif not vals[__ACC__['stock_out'][0]] and vals[__ACC__['stock_in'][0]]:
                        if previous_accounts.get(__ACC__['stock_out'][0],False) and previous_accounts.get(__ACC__['stock_out'][0],False) != vals[__ACC__['stock_in'][0]]:
                            #~ CASO 3A
                            self._switch_accounts(cr,uid,ids,'stock_in','stock_in',vals,context=context)
                            self._switch_accounts(cr,uid,ids,'stock_out','stock_in',vals,context=context)

                            vals[__ACC__['stock_out'][0]] = vals[__ACC__['stock_in'][0]]

                            self._unlink_account(cr,uid,ids,'stock_in',vals,context=context)
                            self._unlink_account(cr,uid,ids,'stock_out',vals,context=context)
                        
                        elif previous_accounts.get(__ACC__['stock_out'][0],False) and previous_accounts.get(__ACC__['stock_out'][0],False) == vals[__ACC__['stock_in'][0]]:
                            #~ CASO 4A
                            vals[__ACC__['stock_out'][0]] = previous_accounts.get(__ACC__['stock_out'][0],False)

                    elif not vals[__ACC__['stock_in'][0]] and vals[__ACC__['stock_out'][0]]:
                        if previous_accounts.get(__ACC__['stock_out'][0],False) and previous_accounts.get(__ACC__['stock_out'][0],False) != vals[__ACC__['stock_out'][0]]:
                            #~ CASO 3B
                            self._switch_accounts(cr,uid,ids,'stock_in','stock_in',vals,context=context)
                            self._switch_accounts(cr,uid,ids,'stock_out','stock_in',vals,context=context)

                            vals[__ACC__['stock_in'][0]] = vals[__ACC__['stock_out'][0]]

                            self._unlink_account(cr,uid,ids,'stock_in',vals,context=context)
                            self._unlink_account(cr,uid,ids,'stock_out',vals,context=context)
                            
                        if previous_accounts.get(__ACC__['stock_out'][0],False) and previous_accounts.get(__ACC__['stock_out'][0],False) == vals[__ACC__['stock_out'][0]]:
                            #~ CASO 4B
                            vals[__ACC__['stock_in'][0]] = previous_accounts.get(__ACC__['stock_out'][0],False)
                
                #~ CASO 5 6 y 7
                    elif vals[__ACC__['stock_out'][0]] and vals[__ACC__['stock_in'][0]]:
                        
                        #~ CASO 5
                        if previous_accounts.get(__ACC__['stock_out'][0],False) and vals[__ACC__['stock_out'][0]] != vals[__ACC__['stock_in'][0]]:
                            if previous_accounts.get(__ACC__['stock_out'][0],False) == vals[__ACC__['stock_in'][0]]:
                                #~ CASO 5A
                                self._switch_accounts(cr,uid,ids,'stock_in','stock_out',vals,context=context)
                                self._switch_accounts(cr,uid,ids,'stock_out','stock_out',vals,context=context)
                                
                                vals[__ACC__['stock_in'][0]] = vals[__ACC__['stock_out'][0]]
                                
                                self._unlink_account(cr,uid,ids,'stock_in',vals,context=context)
                                self._unlink_account(cr,uid,ids,'stock_out',vals,context=context)
                            
                            elif previous_accounts.get(__ACC__['stock_out'][0],False) == vals[__ACC__['stock_out'][0]]:
                                #~ CASO 5B
                                self._switch_accounts(cr,uid,ids,'stock_in','stock_in',vals,context=context)
                                self._switch_accounts(cr,uid,ids,'stock_out','stock_in',vals,context=context)

                                vals[__ACC__['stock_out'][0]] = vals[__ACC__['stock_in'][0]]

                                self._unlink_account(cr,uid,ids,'stock_in',vals,context=context)
                                self._unlink_account(cr,uid,ids,'stock_out',vals,context=context)
                            
                            #~ CASO 7
                            elif previous_accounts.get(__ACC__['stock_out'][0],False) != vals[__ACC__['stock_in'][0]] or previous_accounts.get(__ACC__['stock_out'][0],False) != vals[__ACC__['stock_out'][0]]:
                                #~ CASO 7
                                self._switch_accounts(cr,uid,ids,'stock_in','stock_in',vals,context=context)
                                self._switch_accounts(cr,uid,ids,'stock_out','stock_in',vals,context=context)
                                
                                self._unlink_account(cr,uid,ids,'stock_out',vals,context=context)
                                self._unlink_account(cr,uid,ids,'stock_in',vals,context=context)
                        
                        #~ CASO 6
                        elif previous_accounts.get(__ACC__['stock_out'][0],False) and vals[__ACC__['stock_out'][0]] == vals[__ACC__['stock_in'][0]]:
                            self._switch_accounts(cr,uid,ids,'stock_in','stock_in',vals,context=context)
                            self._switch_accounts(cr,uid,ids,'stock_out','stock_in',vals,context=context)

                            self._unlink_account(cr,uid,ids,'stock_out',vals,context=context)
                            self._unlink_account(cr,uid,ids,'stock_in',vals,context=context)
            else:
                vals = self._account_comparison(cr, uid, ids,'stock_in',vals,context=context)
                vals = self._account_comparison(cr, uid, ids,'stock_out',vals,context=context)

        elif not vals['type']=='service':
            pass
        
            vals = self._account_comparison(cr, uid, ids,'stock_in',vals,context=context)
            vals = self._account_comparison(cr, uid, ids,'stock_out',vals,context=context)
        
        elif vals['type']=='service':
            vals[__ACC__['stock_in'][0]] = False
            vals[__ACC__['stock_out'][0]] = False
            
            vals = self._account_comparison(cr, uid, ids,'stock_in',vals,context=context)
            vals = self._account_comparison(cr, uid, ids,'stock_out',vals,context=context)
            
            vals[__ACC__['stock_in'][0]] = False
            vals[__ACC__['stock_out'][0]] = False
            
        return vals

    def _check_unique_account(self, cr, uid,ids, type_account,account_list,vals, context=None):
        acc_prod_obj = self.pool.get('account.product')
        if context is None:
            context={}
        if context.get('previous_accounts',False):
            previous_accounts=context['previous_accounts']

        for k in account_list:
            vals = self._account_comparison(cr, uid, ids, k,vals,context=context)
        return vals

    def _check_unique_account_stock(self, cr, uid, ids, account_list, vals, context=None):
        acc_prod_obj = self.pool.get('account.product')
        if context is None:
            context={}
        previous_accounts={}
        if context.get('previous_accounts',False):
            previous_accounts=context['previous_accounts']
            
        vals = self._account_stock_comparison(cr, uid, ids, vals, context=context)
        
        return vals

    def _update_code(self, cr, uid,ids,vals, context=None):
        if context is None:
            context={}

        if not vals.get('purchase_ok', False):
            for k in ['expense', 'diff']:
                vals[__ACC__[k][0]]=False 
        if not vals.get('sale_ok', False):
            for k in ['income','allowance','return']:
                vals[__ACC__[k][0]]=False 
        
        vals = self._check_unique_account(cr, uid, ids,'purchase_ok', ['expense', 'diff'], vals, context=context)
        vals = self._check_unique_account(cr, uid, ids,'sale_ok', ['income','allowance','return'], vals, context=context)
        vals = self._check_unique_account_stock(cr, uid, ids, ['stock_in','stock_out'], vals, context=context)
        
        return vals

    def create(self, cr, uid, vals, context=None):
        '''
        Al crear los productos se deben tener minimos en consideracion 
        los siguientes tres aspectos: 
        1.- Se decidio que se colocaran las cuentas del producto manual-
        mente (No se crean cuentas).
        2.- Que se dejara que el producto tome las cuentas que se han de-
        desde la categoria del producto (No se crean cuentas).
        3.- Se Seleccionara la Creacion de Cuentas Unicas.
        
        When creating products three minimun aspects should be taken into
        account:
        1.- The product accounts were picked manually (No Accounts will
        be created).
        2.- No accounts picked, the product's account will be those difined
        into the product category (No Accounts will be created).
        3.- Require Unique Accounts will be selected.
        '''
        if not vals.has_key('unique_account'):
            vals.update({'unique_account':False})

        #~ Updating values not set in the view by the user
        if not vals.has_key('acc_prod_id'):
            vals.update({'acc_prod_id':False})
        
        attributes = ['name', 'purchase_ok', 'sale_ok', 'type',]
                            
        for attr in attributes:
            if not vals.has_key(attr):
                vals.update({attr:False})
        

        for k in __ACC__:
            attr = __ACC__[k][0]
            if not vals.has_key(attr):
                vals.update({attr:False})
        
        vals.update(self._update_code(cr, uid, None, vals, context))
        return super(product_template, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        
        
        if context is None:
            context = {}
                
        self_brw = self.browse(cr,uid,ids[0],context)
        
        # Saving the old accounts if any into a dict
        previous_accounts = {}
        for k in __ACC__:
            attr = __ACC__[k][0]
            previous_accounts.update(
                {attr:getattr(self_brw, attr).id}
                )
        context.update({'previous_accounts':previous_accounts})

        if not vals.has_key('unique_account'):
            vals.update({'unique_account':self_brw.unique_account})

        #~ Updating values not set in the view by the user
        if not vals.has_key('acc_prod_id'):
            vals.update({'acc_prod_id':self_brw.acc_prod_id.id})
        
        attributes = ['name', 'purchase_ok', 'sale_ok', 'type',]
                            
        for attr in attributes:
            if not vals.has_key(attr):
                vals.update({attr:getattr(self_brw, attr)})
        
        for k in __ACC__:
            attr = __ACC__[k][0]
            if not vals.has_key(attr):
                vals.update({attr:getattr(self_brw, attr).id})

        keys_in_vals = vals.keys()
        vals.update(self._update_code(cr, uid, ids, vals, context=context))
        #~ incorporar una funcion que verifique si el acc_prod_id ha cambiado
        #~ si ese elemento ha cambiado entonces se hace un cambio en los parents
        #~ de las cuentas contables de los productos que tengo si y solo si
        #~ esa cuenta contable aparece una sola vez en las propiedades

        valuex = {}
        for i in keys_in_vals:
            valuex[i]=vals[i]
        #~ res = super(product_template, self).write(cr, uid, ids, valuex, context)
        return super(product_template, self).write(cr, uid, ids, valuex, context)
        #~ CAMBIO DE NOMBRE DE LA CUENTA 
        #~ VALIDAR QUE SE HAGA EL CAMBIO SOLO CUANDO LA CUENTA SEA UNICA PARA EL PRODUCTO 
        
        self_brw = self.browse(cr,uid,ids[0],context)
        acc_obj = self.pool.get('account.account')
        for k in __ACC__:
            attr = __ACC__[k][0]
            if vals.get(attr,False):
                if not 'stock' in attr:
                    var = None
                else:
                    var = 'stock'
                aml, prop_ids = self._check_account(cr, uid, [vals[attr]], var, context)
                if prop_ids:
                    value = {'parent_id': self_brw.acc_prod_id and getattr(self_brw.acc_prod_id,__ACC__[k][1]).id or False}
                    if value.get('parent_id',False):
                        value.update({'name': u'%s - %s'%(getattr(self_brw.acc_prod_id,__ACC__[k][1]).name.decode('utf-8').upper(), vals['name'].decode('utf-8').upper()),})
                        acc_obj.write(cr, uid,[vals[attr]], value, context)

        if write_again:
            #~ Esto es solo necesario si se quiere que los parametros
            #~ de la categoria del producto se copien el producto.

            res = super(product_template, self).write(cr, uid, ids, vals, context)
        return res

    def on_change_categ_id(self, cr, uid, ids, categ_id):
        if categ_id:
            categ_brw = self.pool.get("product.category").browse(cr,uid,categ_id)
            if categ_brw.acc_prod_id:
                return {'value': {'acc_prod_id':  categ_brw.acc_prod_id.id, 'unique_account': categ_brw.unique_account}}
            else:
                return {'value': {'acc_prod_id': None, 'unique_account': categ_brw.unique_account}}
        return {}

product_template()

class product_product(osv.osv):
    _inherit='product.product'
    
    def on_change_categ_id(self, cr, uid, ids, categ_id):
        if categ_id:
            categ_brw = self.pool.get("product.category").browse(cr,uid,categ_id)
            if categ_brw.acc_prod_id:
                return {'value': {'acc_prod_id':  categ_brw.acc_prod_id.id, 'unique_account': categ_brw.unique_account}}
            else:
                return {'value': {'acc_prod_id': None, 'unique_account': categ_brw.unique_account}}
        return {}
        
    def copy(self, cr, uid, id, default={}, context={}, done_list=[], local=False):
        '''This will avoid copying the same account from an old product to a new one'''
        if not default:
            default = {}
        default = default.copy()
        for k in __ACC__:
            default.update({__ACC__[k][0]:False})
        return super(product_product, self).copy(cr, uid, id, default, context=context)
    
    def unlink(self, cr, uid, ids, context={}):
        aux=[]
        for i in ids:
            aml_obj = self.pool.get('account.move.line')
            aml_ids = aml_obj.search(cr, uid, [('product_id','=',i)],context=context)
            
            ail_obj = self.pool.get('account.invoice.line')
            ail_ids = ail_obj.search(cr, uid, [('product_id','=',i)],context=context)
            
            pol_obj = self.pool.get('purchase.order.line')
            pol_ids = pol_obj.search(cr, uid, [('product_id','=',i)],context=context)
            
            sol_obj = self.pool.get('sale.order.line')
            sol_ids = sol_obj.search(cr, uid, [('product_id','=',i)],context=context)
            
            sm_obj = self.pool.get('stock.move')
            sm_ids = sm_obj.search(cr, uid, [('product_id','=',i)],context=context)
            
            if not any([aml_ids,ail_ids,pol_ids,sol_ids,sm_ids]):
                aux.append(i)
            else:
                raise osv.except_osv(_('Error'), _('El producto no puede ser borrado ya que esta siendo usado!'))
        return super(product_product, self).unlink(cr, uid, aux, context=context)

product_product()
