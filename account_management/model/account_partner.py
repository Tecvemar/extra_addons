# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    humbertoarocha@gmail.com
#    Creditos Compartidos con
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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


__AYUDA__ = '''
Escriba el Patron de las cuentas, su estructura, por ejemplo:
Clase:           1,
Grupo:           122,
Cuentas:         122333,
Subcuentas:      122333444,
Cuentas Aux.:    1223334445555
Entonces escriba:  1, 122, 122333, 122333444, 122333444555
'''


__TIPO__ = [
            ('receivable','Cuenta x Cobrar'),
            ('payable','Cuenta x Pagar'),
            ]

__res_partner_account_help__ = '''
Esta cuenta se usará para establecer el padre
de los partners que tengan como clasificacion
este Grupo, en conjunto con la secuencia, de
tal manera que si esta cuenta tiene una estruc-
tura, 107003, entonces el partner, que tenga
esta clasificacion, tendra una cuenta como la
que sigue 1070030005, si el patron de cuentas
en la compañía es:
1, 122, 122333, 1223334444
Es de notarse que la cuenta que aqui se sele-
cciona debe ser del tipo del ultimo en el pa-
tron, que para este ejemplo es:
107003 y cuadra con lo establecido 122333
 '''
__res_partner_account_help_default__ = '''
Esta cuenta se establecera como la cuenta con-
table a usar en el caso de que la empresa no -
realice operaciones como proveedor o como cliente,
dependiendo del caso
 '''

__ACC__ = {
            'customer':  ('property_account_receivable',   'account_kind_rec',       'Cuenta x Cobrar'),
            'supplier':  ('property_account_payable',      'account_kind_pay',       'Cuenta x Pagar'),
            }

class res_partner_account(osv.osv):
    def on_change_company(self, cr, uid, ids, company_id, context=None):
        if context is None: context = {}
        res = {}
        rc_obj = self.pool.get('res.company')
        pattern = rc_obj.browse(cr, uid, company_id, context=context).pattern
        res = {'value': {
            'level': len(rc_obj._get_pattern(pattern)) - 1,
            }
        }
        return res

    def _get_level(self, cr, uid, ids, fieldname, args, context=None):
        if context is None:
            context = {}
        res = {}
        rc_obj = self.pool.get('res.company')
        for id in ids:
            res[id] = 0
        for rpa in self.browse(cr, uid, ids, context=context):
            company_id = rpa.company_id.id
            pattern = rpa.company_id.pattern
            level = len(rc_obj._get_pattern(pattern)) - 1
            if level < 1:
                raise osv.except_osv(_('Warning, Pattern has too few levels!!!'),
                                     _('The company you are accessing has a Pattern with too few levels,\nYou can not afford this feature'))
            res[id] = level
        return res

    _name = 'res.partner.account'
    _description = 'Partner Accounting Classification'
    _columns = {
        'name':fields.char(
            'Nombre',
            size = 128,
            required = True,
            readonly = False,),
        'property_account_partner': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Cuenta Anfitriona",
            method=True,
            view_load=True,
            domain="[('type', '=', 'view'),('level','=',level),('level','>',0)]",
            help=__res_partner_account_help__,
            required=True,
            readonly=False),
        'property_account_partner_default': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Cuenta Contable por Defecto",
            method=True,
            view_load=True,
            domain="[('type', '!=', 'view'),('parent_id', '=', property_account_partner), ('company_id', '=', company_id), ('reconcile', '=', True), ('user_type', '=', user_type), ('type', '=', type),]",
            help=__res_partner_account_help_default__,
            required=True,
            readonly=False),
        'company_id':fields.many2one(
            'res.company',
            'Compañia',
            required = True),
        'user_type': fields.many2one(
            'account.account.type',
            'Tipo de Cuenta',
            required=True),
        'level': fields.function(_get_level,method=True,type='integer',string='Level'),
        'type': fields.selection(
            __TIPO__,
            'Tipo',
            readonly=False,
            required=True),
    }
    #~ TODO: Check if this is going to be really deleted!!!
    #~ _sql_constraints = [
                        #~ ('name_uniq','unique(name)', 'Otro registro ya tiene este nombre!'),
                        #~ ('account_uniq','unique(property_account_partner)', 'Otro registro ya esta usando esta Cuenta!'),
                        #~ ]

    def _check(self, cr, uid, vals, context=None):
        cuentas=[vals.get('property_account_partner',False)]
        if not cuentas[0]:
            partner_acc_id = vals.get('id',False)
            if partner_acc_id:
                cuentas=[self.browse(cr, uid,partner_acc_id).property_account_partner.id]

        pattern = self.pool.get('res.company').browse(cr, uid, vals['company_id']).pattern
        self.pool.get('res.company')._check_accounts(cr, uid, pattern, cuentas)
        #~ vals['name'] = self._get_name(cr, uid, cuentas)
        return vals

    def _get_name(self, cr, uid, cuentas):
        obj = self.pool.get('account.account')
        code = obj.browse(cr,uid,cuentas[0]).code
        name = obj.browse(cr,uid,cuentas[0]).name
        return u'%s %s'%(code, name)

    def create(self, cr, uid, vals, context=None):
        self._check(cr, uid, vals,context)
        return super(res_partner_account, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('company_id',False):
            vals.update({'company_id':self.browse(cr, uid, ids[0],context=context).company_id.id,'id':ids[0]})
        self._check(cr, uid, vals,context)
        return super(res_partner_account, self).write(cr, uid, ids, vals, context)

    def _get_account(self, cr, uid, kind_id, account_name, do_account=False, account_id=None, do_write=False, context=None):
        obj = self.browse(cr, uid, kind_id)
        if not do_account:
            return obj.property_account_partner_default.id
        parent_id =     obj.property_account_partner.id
        parent_name =   obj.property_account_partner.name
        company_id =    obj.company_id.id
        user_type =     obj.user_type.id
        type =          obj.type

        aa_obj = self.pool.get('account.account')
        if do_write == False:
            account_id = aa_obj.create(cr, uid, {
                                'auto': True,
                                'name': u'%s - %s'%(parent_name, account_name),
                                'user_type': user_type,
                                'type': type,
                                'company_id':company_id,
                                'currency_mode':'current',
                                'active': True,
                                'reconcile': True,
                                'parent_id':parent_id,
                            },context)

            return account_id
        else:
            values = {
                                'code': codigo,
                                'name': u'%s - %s'%(parent_name, account_name),
                                'user_type': user_type,
                                'company_id':company_id,
                                'currency_mode':'current',
                                'active': True,
                                'reconcile': True,
                                'parent_id':parent_id,
                            }
            return True
res_partner_account()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'property_account_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Payable",
            method=True,
            view_load=True,
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=False,
            readonly=False),

        'property_account_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Receivable",
            method=True,
            view_load=True,
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=False,
            readonly=False),

        'account_kind_rec':fields.property(
            'res.partner.account',
            type='many2one',
            relation='res.partner.account',
            string='Tipo de CxC',
            method=True,
            view_load=True,
            domain="[('type', '=', 'receivable')]",
            help="Este Concepto le permite generar las CxC para\nla empresa de acuerdo a la cuenta contable\ndel grupo en el cual se clasifica",
            required=False,
            readonly=False),
        'account_kind_pay':fields.property(
            'res.partner.account',
            type='many2one',
            relation='res.partner.account',
            string='Tipo de CxP',
            method=True,
            view_load=True,
            domain="[('type', '=', 'payable')]",
            help="Este Concepto le permite generar las CxP para\nla empresa de acuerdo a la cuenta contable\ndel grupo en el cual se clasifica",
            required=False,
            readonly=False),
    }

    def _validate_assigned_account(self, cr, uid, ids, context):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        pnr_brw = self.browse(cr, uid, ids[0], context=context)
        if pnr_brw.account_kind_rec and pnr_brw.customer:
            if (pnr_brw.property_account_receivable.id == pnr_brw.account_kind_rec.property_account_partner_default.id):
                raise osv.except_osv(
                    _('Error!'),
                    _('Can\'t use default receivable account for this partner'))
        if pnr_brw.account_kind_pay and pnr_brw.supplier:
            if (pnr_brw.property_account_payable.id == pnr_brw.account_kind_pay.property_account_partner_default.id):
                raise osv.except_osv(
                    _('Error!'),
                    _('Can\'t use default payable account for this partner'))
        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        attributes = ['customer','supplier','name']
        previous_accounts = {}

        for k in __ACC__:
            attr = __ACC__[k][0]
            if not previous_accounts.has_key(attr):
                previous_accounts.update({attr:False})

        for k in __ACC__:
            attr = __ACC__[k][1]
            if not previous_accounts.has_key(attr):
                previous_accounts.update({attr:False})

        for attr in attributes:
            if not previous_accounts.has_key(attr):
                previous_accounts.update({attr:False})


        context.update({'previous_accounts':previous_accounts})


        #~ OBTENIENDO LAS CUENTAS CONTABLES QUE NO SE ACTUALIZARON
        for k in __ACC__:
            attr = __ACC__[k][0]
            if not vals.has_key(attr):
                vals.update({attr:False})

        for k in __ACC__:
            attr = __ACC__[k][1]
            if not vals.has_key(attr):
                vals.update({attr:False})

        for attr in attributes:
            if not vals.has_key(attr):
                vals.update({attr:False})
        vals.update(self._update_code(cr, uid, None, vals, context=context))
        res = super(res_partner, self).create(cr, uid, vals, context)
        if not res:
            raise osv.except_osv(
                _('Error!'),
                _('Can\'t create a partner, (can be duplicated)'))
        self._validate_assigned_account(cr, uid, res, context=context)
        return res

    def _switch_accounts(self, cr, uid, ids, k,vals, context=None):
        prod_id = None
        if context is None:
            context={}

        aml_obj = self.pool.get('account.move.line')
        ai_obj = self.pool.get('account.invoice')
        avl_obj = self.pool.get('account.voucher.line')

        #~ NEEDS REVIEWS
        previous_accounts={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']

        per_obj = self.pool.get('account.period')
        period_ids = per_obj.search(cr, uid, [('special','=',False),
                                    ('state', '=', 'draft')],
                                    context=context)

        search_criteria = \
            [('account_id','=',previous_accounts[__ACC__[k][0]]),
             ('partner_id','in',ids),
             ('period_id', 'in', period_ids)]

        aml_ids = period_ids and \
            aml_obj.search( cr, uid, search_criteria, context=context) \
            or False
        ai_ids = period_ids and \
            ai_obj.search( cr, uid, search_criteria, context=context) \
            or False
        search_criteria.pop()
        avl_ids = period_ids and \
            avl_obj.search( cr, uid, search_criteria, context=context) \
            or False

        if aml_ids:
            cr.execute('UPDATE account_move_line SET account_id = %s WHERE id in (%s)'%(vals[__ACC__[k][0]],', '.join([str(i) for i in aml_ids])))

        if ai_ids:
            cr.execute('UPDATE account_invoice SET account_id = %s WHERE id in (%s)'%(vals[__ACC__[k][0]],', '.join([str(i) for i in ai_ids])))

        if avl_ids:
            cr.execute('UPDATE account_voucher_line SET account_id = %s WHERE id in (%s)'%(vals[__ACC__[k][0]],', '.join([str(i) for i in avl_ids])))

        return True

    def _check_unique(self,cr,uid,ids,k,vals,context=None):

        if context is None:
            context={}
        previous_accounts = context.get('previous_accounts', {})

        pro_obj=self.pool.get('ir.property')

        part_ids=pro_obj.search(cr,uid,[('name','=',__ACC__[k][0]),('value_reference','=','account.account,%s'%previous_accounts[__ACC__[k][0]]),('res_id','like','res.partner,')])

        if len(part_ids)==1:
            return True
        else:
            return False

    def _drop_properties(self, cr, uid, ids, k, context=None):
        ir_prop_obj = self.pool.get('ir.property')
        if context is None:
            context={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']

        res_id = '%s,%s'%('res.partner',ids[0])
        value_reference = '%s,%s'%('account.account',previous_accounts[__ACC__[k][0]])
        ir_prop_ids = ir_prop_obj.search(cr, uid, [('res_id','=',res_id),('value_reference','=',value_reference),('name','=',__ACC__[k][0])], context=context)
        ir_prop_obj.unlink(cr, uid, ir_prop_ids, context=context)

        return ir_prop_obj.search(cr, uid, [('value_reference','=',value_reference)])

    def _search_model(self, cr, uid, ids, model, acc, context=None):
        if context is None:
            context={}
        account_ids = self.pool.get('account.account').search(cr, uid, [('id', 'child_of', acc)])
        return self.pool.get(model).search(cr, uid, [('account_id', 'in', account_ids)]) and True or False

    def _unlink_account(self, cr, uid, ids, k, vals, context=None):
        if context is None:
            context={}
        if context.get('previous_accounts',False):
            previous_accounts = context['previous_accounts']
        else:
            previous_accounts={}

        if previous_accounts.get(__ACC__[k][0],False):
            model= 'account.move.line'
            aml= self._search_model(cr,uid,ids,model,[previous_accounts[__ACC__[k][0]]],context=context)
            model= 'account.invoice'
            ai= self._search_model(cr,uid,ids,model,[previous_accounts[__ACC__[k][0]]],context=context)
            model= 'account.voucher.line'
            avl= self._search_model(cr,uid,ids,model,[previous_accounts[__ACC__[k][0]]],context=context)
            properties = self._drop_properties(cr,uid,ids,k,context=context)
            if not any([aml,ai,avl,properties]):
                self.pool.get('account.account').unlink(cr,uid,[previous_accounts[__ACC__[k][0]]], context)
                return True
        return False

    def _assign_account(self,cr,uid,ids,k,vals, context=None):

        if context is None:
            context={}
        previous_accounts = context.get('previous_accounts', {})

        ## To avoid use of property_account_partner_default as account
        rpa = self.pool.get('res.partner.account')
        rpa_brw = rpa.browse(cr,uid,vals[__ACC__[k][1]])
        default_acc = rpa_brw.property_account_partner_default and rpa_brw.property_account_partner_default.id

        if self._check_unique(cr,uid,ids,k,vals,context=context) and \
                previous_accounts[__ACC__[k][0]] != default_acc:
            parent_id = getattr(rpa_brw,'property_account_partner').id
            parent_name = getattr(rpa_brw,'property_account_partner').name
            try:
                name = str(u'%s - %s'%(parent_name.decode('utf-8').upper(), vals['name'].decode('utf-8').upper())).encode('utf-8')
            except:
                name = '%s - %s'%(parent_name, vals['name'])
            self.pool.get('account.account').write(cr,uid,[previous_accounts[__ACC__[k][0]]],{'parent_id':parent_id,'auto':True,'name':name},context)
            vals[__ACC__[k][0]]=previous_accounts[__ACC__[k][0]]
        else:
            vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)
            self._switch_accounts(cr,uid,ids,k,vals,context=context)
            self._unlink_account(cr,uid,ids,k,vals,context=context)

        return vals

    def _comparison(self,cr,uid,ids,k,vals, context=None):
        if context is None:
            context={}
        previous_accounts={}
        if context.get('previous_accounts',False):
            previous_accounts=context['previous_accounts']

        rpa = self.pool.get('res.partner.account')
        #~ This condition indicates if supplier/customer or not
        if vals.get(k,False):
            #~ This condition indicates accounting account was or not assigned
            if vals.get(__ACC__[k][1],False):
                if previous_accounts.get(__ACC__[k][1],False) == vals.get(__ACC__[k][1],False):

                    if not previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)

                    elif not previous_accounts.get(__ACC__[k][0],False) and vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) != vals.get(__ACC__[k][0],False):

                        if self._check_unique(cr,uid,ids,k,vals,context=context):
                            vals[__ACC__[k][0]]=previous_accounts[__ACC__[k][0]]
                        else:
                            vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)
                            self._switch_accounts(cr,uid,ids,k,vals,context=context)
                            self._unlink_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        if self._check_unique(cr,uid,ids,k,vals,context=context):
                            vals[__ACC__[k][0]]=previous_accounts[__ACC__[k][0]]
                        else:
                            vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)
                            self._switch_accounts(cr,uid,ids,k,vals,context=context)
                            self._unlink_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) == vals.get(__ACC__[k][0],False):
                        vals = self._assign_account(cr,uid,ids,k,vals,context=context)

                else:

                    if not previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)

                    elif not previous_accounts.get(__ACC__[k][0],False) and vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = rpa._get_account(cr, uid, vals.get(__ACC__[k][1],False), vals['name'], vals[k],context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) != vals.get(__ACC__[k][0],False):
                        vals = self._assign_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals = self._assign_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) == vals.get(__ACC__[k][0],False):
                        vals = self._assign_account(cr,uid,ids,k,vals,context=context)

            else:
                if not previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                    if not context.get('account_company_create',False):
                        raise osv.except_osv(('Atencion !'), ('La %s para este partner no puede ser nula')%(__ACC__[k][2]))
                    else:
                        pass
                elif not previous_accounts.get(__ACC__[k][0],False) and vals.get(__ACC__[k][0],False):
                    pass
                elif previous_accounts.get(__ACC__[k][0],False) != vals.get(__ACC__[k][0],False):
                    self._switch_accounts(cr,uid,ids,k,vals,context=context)
                    self._unlink_account(cr,uid,ids,k,vals,context=context)

                elif previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                    vals[__ACC__[k][0]]=previous_accounts[__ACC__[k][0]]

                elif previous_accounts.get(__ACC__[k][0],False) == vals.get(__ACC__[k][0],False):
                    pass

        else:
            if vals.get(__ACC__[k][1],False):
                if previous_accounts.get(__ACC__[k][1],False) == vals.get(__ACC__[k][1],False):
                    if not previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                    elif not previous_accounts.get(__ACC__[k][0],False) and vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                    elif previous_accounts.get(__ACC__[k][0],False) != vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                        self._switch_accounts(cr,uid,ids,k,vals,context=context)
                        self._unlink_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]]=previous_accounts[__ACC__[k][0]]

                    elif previous_accounts.get(__ACC__[k][0],False) == vals.get(__ACC__[k][0],False):

                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                        self._switch_accounts(cr,uid,ids,k,vals,context=context)
                        self._unlink_account(cr,uid,ids,k,vals,context=context)

                else:
                    if not previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id

                    elif not previous_accounts.get(__ACC__[k][0],False) and vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id

                    elif previous_accounts.get(__ACC__[k][0],False) != vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                        self._switch_accounts(cr,uid,ids,k,vals,context=context)
                        self._unlink_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                        self._switch_accounts(cr,uid,ids,k,vals,context=context)
                        self._unlink_account(cr,uid,ids,k,vals,context=context)

                    elif previous_accounts.get(__ACC__[k][0],False) == vals.get(__ACC__[k][0],False):
                        vals[__ACC__[k][0]] = getattr(rpa.browse(cr,uid,vals[__ACC__[k][1]]),'property_account_partner_default').id
                        self._switch_accounts(cr,uid,ids,k,vals,context=context)
                        self._unlink_account(cr,uid,ids,k,vals,context=context)

            else:
                if not previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                    if not context.get('account_company_create',False):
                        raise osv.except_osv(('Atencion !'), ('La %s para este partner no puede ser nula')%(__ACC__[k][2]))
                    else:
                        pass

                elif not previous_accounts.get(__ACC__[k][0],False) and vals.get(__ACC__[k][0],False):
                    pass

                elif previous_accounts.get(__ACC__[k][0],False) != vals.get(__ACC__[k][0],False):
                    self._switch_accounts(cr,uid,ids,k,vals,context=context)
                    self._unlink_account(cr,uid,ids,k,vals,context=context)

                elif previous_accounts.get(__ACC__[k][0],False) and not vals.get(__ACC__[k][0],False):
                    if not context.get('account_company_create',False):
                        raise osv.except_osv(('Atencion !'), ('La %s para este partner no puede ser nula')%(__ACC__[k][2]))
                    else:
                        pass
                elif previous_accounts.get(__ACC__[k][0],False) == vals.get(__ACC__[k][0],False):
                    pass
        return vals

    def _update_code(self, cr, uid,ids,vals, context=None):
        if context is None:
            context={}

        for k in __ACC__:
            vals = self._comparison(cr, uid,ids,k,vals,context=context)
        return vals

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if type(ids)==int:
            ids = [ids]

        if not set(vals.keys()) & set(['customer','supplier' ,'property_account_receivable', 'property_account_payable' ,'account_kind_rec', 'account_kind_pay']):
            return super(res_partner, self).write(cr, uid, ids, vals, context)

        attributes = ['customer','supplier','name']
        self_brw = self.browse(cr,uid,ids[0],context)
        previous_accounts = {}


        for k in __ACC__:
            attr = __ACC__[k][0]
            if not previous_accounts.has_key(attr):
                previous_accounts.update({attr:getattr(self_brw,attr) and getattr(self_brw,attr).id})

        for k in __ACC__:
            attr = __ACC__[k][1]
            if not previous_accounts.has_key(attr):
                previous_accounts.update({attr:getattr(self_brw,attr) and getattr(self_brw,attr).id})

        for attr in attributes:
            if not previous_accounts.has_key(attr):
                previous_accounts.update({attr:getattr(self_brw, attr)})


        context.update({'previous_accounts':previous_accounts})


        #~ OBTENIENDO LAS CUENTAS CONTABLES QUE NO SE ACTUALIZARON
        for k in __ACC__:
            attr = __ACC__[k][0]
            if not vals.has_key(attr):
                vals.update({attr:getattr(self_brw, attr) and getattr(self_brw, attr).id})

        for k in __ACC__:
            attr = __ACC__[k][1]
            if not vals.has_key(attr):
                vals.update({attr:getattr(self_brw, attr) and getattr(self_brw, attr).id})

        for attr in attributes:
            if not vals.has_key(attr):
                vals.update({attr:getattr(self_brw, attr)})



        keys_in_vals = vals.keys()
        vals.update(self._update_code(cr, uid, ids, vals, context=context))

        valuex = {}
        for i in keys_in_vals:
            valuex[i]=vals[i]
        #~ res = super(product_template, self).write(cr, uid, ids, valuex, context)
        res = super(res_partner, self).write(cr, uid, ids, valuex, context)
        for id in ids:
            self._validate_assigned_account(cr, uid, id, context=context)
        return res

    def search_aml(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        aml_obj = self.pool.get('account.move.line')
        return  aml_obj.search(cr, uid, [('partner_id','=',id)],context=context)


    def search_ai(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        ai_obj = self.pool.get('account.invoice')
        return ai_obj.search(cr, uid, [('partner_id','=',id)],context=context)


    def search_so(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        so_obj = self.pool.get('sale.order')
        return so_obj.search(cr, uid, [('partner_id','=',id)],context=context)

    def search_po(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        po_obj = self.pool.get('purchase.order')
        return po_obj.search(cr, uid, [('partner_id','=',id)],context=context)

    def search_avl(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        avl_obj = self.pool.get('account.voucher.line')
        return avl_obj.search(cr, uid, [('partner_id','=',id)],context=context)

    def _test_unlink(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        # TODO OR COMPLETE THE REMAINING FUNCTIONS SO IT COULD BE
        # POSIBLE TO CHECK ALL THE POSSIBILITIES.
        test = []
        test.append(all([self.search_aml(cr, uid, id, context=context) and True]))
        test.append(all([self.search_ai(cr, uid, id, context=context) and True]))
        test.append(all([self.search_so(cr, uid, id, context=context) and True]))
        test.append(all([self.search_po(cr, uid, id, context=context) and True]))
        test.append(all([self.search_avl(cr, uid, id, context=context) and True]))
        return test

    def _try_unlink(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        attributes = ['customer','supplier']
        self_brw = self.browse(cr,uid,id,context)
        previous_accounts = {}
        vals={}

        for k in __ACC__:
            attr = __ACC__[k][0]
            previous_accounts.update({attr:getattr(self_brw,attr) and getattr(self_brw,attr).id})

        for k in __ACC__:
            attr = __ACC__[k][1]
            previous_accounts.update({attr:getattr(self_brw,attr) and getattr(self_brw,attr).id})

        for attr in attributes:
            previous_accounts.update({attr:getattr(self_brw, attr)})


        context.update({'previous_accounts':previous_accounts})


        #~ OBTENIENDO LAS CUENTAS CONTABLES QUE NO SE ACTUALIZARON
        for k in __ACC__:
            attr = __ACC__[k][0]
            vals.update({attr:False})

        for k in __ACC__:
            attr = __ACC__[k][1]
            vals.update({attr:False})

        for attr in attributes:
            vals.update({attr:False})

        if not any(self._test_unlink(cr, uid, id, context=context)):
            test=[True]
            for k in __ACC__:
                if self._check_unique(cr,uid,id,k,vals,context=context):
                    test.append(self._unlink_account(cr,uid,[id],k,vals,context=context))
                else:
                    test.append(True)
            return all(test)
        return False

    def unlink(self, cr, uid, ids,context=None):
        if context is None:
            context = {}

        res = [id for id in ids if self._try_unlink(cr, uid, id, context=context)]
        if res:
            return super(res_partner,self).unlink(cr, uid, res, context=context)
        return False
res_partner()
