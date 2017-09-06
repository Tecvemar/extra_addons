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
import tools
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

__CUENTAS__ = {
                'income':   ('property_account_income',                     'income',       'u_type_income'),
                'expense':  ('property_account_expense',                    'expense',      'u_type_expense'),
                'stock_in': ('property_stock_account_input',                'stock_in',     'u_type_stock_in'),
                'stock_out':('property_stock_account_output',               'stock_out',    'u_type_stock_out',),
                'diff':     ('property_account_creditor_price_difference',  'price_diff',   'u_type_price_diff'),
                    }
__TYPE__ = ['receivable',
            'payable',
            'consolidation',
            'other',
            'closed',]

class res_company(osv.osv):
    _name = 'res.company'
    _inherit = 'res.company'

    _columns = {
        'pattern':fields.char(
            'Patron de Cuentas Contables',
            size=1024,
            required=False,
            help=__AYUDA__,),
    }

    def _equal_accounts(self, cuentas):
        if cuentas[0] == cuentas[1]:
            raise osv.except_osv(('Atencion !'), ('La cuentas CxC y CxP no pueden ser iguales'))

    def _get_list(self, pattern):
        return [i.strip() for i in pattern.split(',')]

    def _pattern(self, cr, uid, ids):
        return self._get_list(self.pattern)

    def _get_pattern(self, pattern):
        if not pattern:
            raise osv.except_osv(('Falta de Definicion de Patron Contable en Company!!!'), ('No se ha definido un patron en la configuracion de la Compañia'))
        lista = self._get_list(pattern)
        patron = list(set(([len(lista[i]) for i in range(len(lista))])))
        patron.sort()
        return patron

    def _check_accounts(self,cr,uid,pattern,cuentas):
        if len(cuentas)==2:
            self._equal_accounts(cuentas)

        patron = self._get_pattern(pattern)

        obj = self.pool.get('account.account')
        acc_list = []
        for i in cuentas:
            acc_list.append(obj.browse(cr,uid,i).code)

        for i in acc_list:
            if not len(i)==patron[-2]:
                raise osv.except_osv(('Atencion !'), ('La cuenta %s no es del tipo en la penultima cuenta del patron \n%s caracteres, %s!!!')%(i,patron[-2], patron[-2]*'0'))
        '''
    def _ordering(self, cr, uid, patron, len_patron, dict, dict_i0, k, i=0):
        for j in dict.keys():
            if len(dict[j][0])==patron[i+1] and dict[j][0][:patron[i]]==dict_i0:
                dict[j][1]=True
                dict[j][2]=k
                if i+1 < len_patron:
                    self._ordering(cr, uid, patron, len_patron, dict, dict[j][0], j, i+1)

    def _get_order(self, cr, uid, ids, context=None):
        for id in ids:
            lista = self._get_list(cr, uid, id, context)
            patron = self._get_pattern(lista)
            par_acc = self.browse(cr,uid,id,context).parent_account.id
            aa = self.pool.get('account.account')
            #~ Excluyendo el id del padre para que no este dentro de los elementos a los que se les va asignar padre.
            #~ evitando asi redundancia ciclica
            unsorted_account_ids = list(set(aa.search(cr, uid, [('company_id','=', self.browse(cr, uid, id, context).company_id.id)], order='code'))-set([par_acc]))

            dict={}
            for i in unsorted_account_ids:
                dict[i]=[]
                dict[i]=[aa.browse(cr,uid,i).code, False, '']

            for i in dict.keys():
                if len(dict[i][0])==patron[0]:
                    dict[i][2]= par_acc
                    dict[i][1]= True
                    self._ordering(cr, uid, patron, len(patron)-1, dict, dict[i][0], i)

            for i in dict.keys():
                if dict[i][1]==True:
                    cr.execute("UPDATE account_account SET parent_id=%s WHERE id=%s", (dict[i][2],i))
        return True
        '''

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context={}
        from time import sleep
        context.update({'account_company_create':True})
        #~ pattern = vals['pattern']
        #~ vals['num_pattern'] = self._get_pattern(pattern)
        return super(res_company, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context={}
        from time import sleep
        context.update({'account_company_create':True})
        #~ pattern = vals['pattern']
        #~ vals['num_pattern'] = self._get_pattern(pattern)
        return super(res_company, self).write(cr, uid, ids, vals, context)

res_company()

__auto_help__ = '''
'Si esta seleccionado, debera indicar una cuenta padre o anfitriona,
 y al guardar el registro se autogenerara el codigo consecutivo
 de la cuenta contable huesped, evitando que vd. genere manualmente
 el codigo contable de la misma.'
'''

def _links_get(self, cr, uid, context=None):
    """Gets links value for reference field
    @param self: The object pointer
    @param cr: the current row, from the database cursor,
    @param uid: the current user’s ID for security checks,
    @param context: A standard dictionary for contextual values
    """
    obj = self.pool.get('ir.model.fields')
    ids = obj.search(cr,uid,[('ttype','=','many2one'),('relation','=','account.account'),('model','!=','account.account')])
    ids = list(set([i['model_id'][0] for i in obj.read(cr,uid,ids,['model_id'])]))
    obj = self.pool.get('ir.model')
    res = obj.read(cr, uid, ids, ['model', 'name'], context)
    return [(r['model'], r['name']) for r in res]

class account_account_records(osv.osv):
    _name = 'account.account.records'
    _auto = False
    _description = 'Records by Accounts'
    _rec_name = 'record_id'
    _columns = {
        'record_id':fields.reference('Record',selection=_links_get,size=128,readonly=True),
        'model_id':fields.many2one('ir.model', 'Model',readonly=True),
        'value_id':fields.integer('Value',readonly=True),
        'field_id':fields.many2one('ir.model.fields', 'Field',readonly=True),
    }
    def _get_records(self, cr, uid=1, id=None, context=None):
        if context is None:
            context = {}
        res=[]

        imf_obj = self.pool.get('ir.model.fields')
        #~ imf_ids = imf_obj.search(cr,uid,[('ttype','=','many2one'),('relation','=','account.account'),('model','!=','account.account'),('view_load','=',False)])
        imf_ids = imf_obj.search(cr,uid,[('ttype','=','many2one'),('relation','=','account.account'),('model','!=','account.account')])

        if imf_ids:
            for each in imf_obj.browse(cr, uid, imf_ids, context=context):
                if not each.model_id.osv_memory:
                    cr.execute("""SELECT attname FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = '%s') AND attname = '%s'"""%(each.model.replace('.','_'),each.name))
                    value = cr.fetchall()
                    if not value:
                        continue

                    res.append("""SELECT COALESCE(%s,NULL) as value_id, CASE WHEN id > 0 THEN (%s || id) END AS record_id, CASE WHEN id > 0 THEN %s END AS field_id, CASE WHEN id > 0 THEN %s END AS model_id, CASE WHEN id > 0 THEN (%s * %s + id) END AS id FROM %s"""%(each.name,"'%s,'"%each.model,each.id,each.model_id.id,each.id,each.model_id.id,each.model.replace('.','_')))
            res = ' UNION '.join(res)
        return res

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_account_records')
        cr.execute("""
            CREATE OR REPLACE view account_account_records AS (%s)
        """%(self._get_records(cr, 1),))

account_account_records()


class account_account(osv.osv):
    def _get_records(self, cr, uid, ids, fieldname, args, context=None):
        if context is None:
            context = {}
        res={}
        for id in ids:
            cr.execute('SELECT id FROM account_account_records where value_id = %s'%(id,))
            val = cr.fetchall()
            if val:
                res[id]=[i[0] for i in val]
            else:
                res[id]=[]
        return res

    _inherit='account.account'
    _columns={
            'auto':fields.boolean('AutoCodigo?', help=__auto_help__),
            'code': fields.char('Code', size=64, required=False),
            #~ 'record_ids': fields.many2many('account.account.records',
                #~ 'account_account_records',
                #~ 'value_id',
                #~ 'record_id',
                #~ 'Records by account'
            #~ ),
            #~ 'record_ids': fields.function(
                #~ _get_records,
                #~ method=True,
                #~ relation= 'account.account.records',
                #~ type='one2many',
                #~ help = 'Show all the record where this account is being used',
                #~ string = 'Records by account'
            #~ ),
            }

    def _get_parent(self, cr, uid, code, nivel, patron_nivel, company_id):
        parent_code = code[:patron_nivel]
        parent_id = self.search(cr, uid, [('code','=',parent_code),('company_id','=',company_id)])
        if parent_id:
            return parent_id[0]
        else:
            if not nivel == 0:
                nota = '''
                No hay una Cuenta Padre disponible para la cuenta que Vd. intenta crear,
                debe proceder a crearla antes de crear esta cuenta.'''
                raise osv.except_osv('ADVERTENCIA', nota)
            elif nivel == 0 and not code=='0':
                parent_id = self.search(cr, uid, [('code','=','0'),('company_id','=',company_id)])
                if parent_id:
                    return parent_id[0]
                else:
                    nota = '''
                    Debe Crear la cuenta Principal '0' del Catalogo de cuentas antes de proceder
                    a Crear cuentas en el catalogo para esta Empresa'''
                    raise osv.except_osv('ADVERTENCIA', nota)
            else:
                return None

    def _check_pattern(self, cr, uid, vals, context):
        rc = self.pool.get('res.company')
        pattern = rc._get_pattern(rc.browse(cr, uid, vals['company_id']).pattern)
        if not vals.get('auto',False):
            if len(vals['code']) in pattern:
                return (pattern , pattern.index(len(vals['code'])))
            else:
                note = '''
                El codigo de la cuenta que intenta crear no cumple con el patron establecido en la empresa'''
                raise osv.except_osv('ADVERTENCIA', note)
        else:
            parent_code = self.browse(cr, uid, vals['parent_id'], context).code
            if parent_code == '0':
                return (pattern , None)
            else:
                return (pattern , pattern.index(len(parent_code)))



    def _no_auto_code(self, cr, uid, vals, context):

        pattern, level = self._check_pattern(cr, uid, vals, context)

        if len(vals['code'])== pattern[-1]:    # Implica que el codigo que se ha introducido es del ultimo nivel
            if vals['type'] == 'view':
                vals['type'] = 'other'
        else:
            vals['type'] = 'view'

        vals['parent_id'] = self._get_parent(cr, uid, vals['code'], level, pattern[level-1], vals['company_id'])

        return vals

    def _get_custom_number(self, cr, uid, context=None):
        '''Override this method to set your
        own number used in the accounting accounts'''
        if context is None: context = {}
        return None

    def _get_number(self, cr, uid, acc_obj, scope,context=None):
        '''
         This method gets the children of the account host
         then with those children, get the codes that exist
         away from them generates a list of codes, and together
         the pattern found in the company accounts are obtained
         the numbers that are available, and from these numbers
         take the first number that is available
        '''
        if context is None: context = {}

        children_acc = acc_obj.child_parent_ids

        sequences = [int(acc.code[-scope:]) for acc in children_acc]
        sequences.sort()
        max_number = 10**scope-1
        number = self._get_custom_number(cr, uid, context=context)

        if number and number not in sequences and  number < max_number:
            return number
        else:
            number = None

        if sequences:
            if sequences[0] > 1:
                return 1
            elif len(sequences) == max_number:
                pass
            else:
                for i in sequences:
                    if i+1 not in sequences:
                        return i+1
        else:
            return 1

        if number is None:
            note = _('''The account [%s -%s] \nhas reached the limit that can be accommodated\nin the ledger accounts: [%d accounts]''')%(acc_obj.code, acc_obj.name.upper(),max_number)
            raise osv.except_osv(('ATTENTION !'), (note))

    def _auto_code(self, cr, uid, vals, context):
        pattern, level = self._check_pattern(cr, uid, vals, context)

        parent_brw = self.browse(cr, uid, vals['parent_id'], context)
        parent_code = parent_brw.code

        if len(parent_code)< pattern[-2]:
            vals['type'] = 'view'

        elif len(parent_code) == pattern[-2]:  # Implica que el codigo del padre que se ha introducido es del penultimo nivel
            if vals['type'] == 'view':         # por lo tanto los hijos son de ultimo nivel
                vals['type'] = 'other'
        elif len(parent_code) == pattern[-1]:
            note = '''
            Error de Consistencia
            La Cuenta Contable [ %s ]
            Esta en el Ultimo nivel de la Configuracion de Patron
            de Cuentas, una Cuenta Padre o Anfitriona no puede
            pertenecer al ultimo nivel, Corrija la Situacion
            Antes de proseguir con la creacion de las Cuentas'''%(parent_code,)
            raise osv.except_osv('ADVERTENCIA', note)
        if level is None:
            scope = 1
            vals['code'] = str(self._get_number(cr, uid, parent_brw,scope,context))
        else:
            scope = pattern[level+1] - pattern[level]
            vals['code'] = parent_code + str(self._get_number(cr, uid, parent_brw,scope,context)).rjust(scope, '0')
        return vals


    def _check_account(self, cr, uid, vals, context):
        '''Checks if Autocoding of accounting accounts applies'''

        if vals.get('auto',False):
            return self._auto_code(cr, uid, vals, context)
        else:
            return self._no_auto_code(cr, uid, vals, context)

    def create(self, cr, uid, vals, context=None):
        vals = self._check_account(cr, uid, vals, context)
        return super(account_account, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        acc_brw = self.browse(cr,uid,ids[0],context)
        if 'code' in vals.keys() or 'company_id' in vals.keys() or 'parent_id' in vals.keys() or  'type' in vals.keys() or 'auto' in vals.keys():
            vals['company_id'] = vals.get('company_id', acc_brw.company_id.id)
            vals['type'] = vals.get('type', acc_brw.type)
            vals['auto'] = vals.get('auto', acc_brw.auto)
            if not 'code' in vals.keys():
                vals['code'] = acc_brw.code
            else:
                if vals['code'] == acc_brw.code:
                    if not context.get('mass',False):
                        vals['parent_id'] = acc_brw.parent_id.id
                        return super(account_account, self).write(cr, uid, ids, vals, context)
                else:
                    if acc_brw.child_id:
                        context.update({'mass':True})

            if not 'parent_id' in vals.keys():
                vals['parent_id'] = acc_brw.parent_id.id
            else:
                if vals['parent_id'] == acc_brw.parent_id.id:
                    if not context.get('mass',False):
                        vals['code'] = acc_brw.code
                        return super(account_account, self).write(cr, uid, ids, vals, context)
                else:
                    if acc_brw.child_id:
                        context.update({'mass':True})

            vals = self._check_account(cr, uid, vals, context)
            res = super(account_account, self).write(cr, uid, ids, vals, context)
            if context.get('mass',False):
                for acc in acc_brw.child_id:
                    self.write(cr, uid, [acc.id], {'parent_id':acc.parent_id.id },context)
            return res
        else:
            return super(account_account, self).write(cr, uid, ids, vals, context)

    def _check_properties(self,cr,uid,ids,context=None):
        if context is None: context= {}
        ir_obj = self.pool.get('ir.property')
        res = []
        unlk_ids = []
        for id in ids:
            value_reference = 'account.account,' + str(id)
            ir_ids = ir_obj.search(cr, uid, [('value_reference','=',value_reference)], context=context)
            test = [True] if not ir_ids else []
            for ir_brw in ir_obj.browse(cr, uid, ir_ids, context=context):
                cr.execute('SELECT res_id FROM ir_property WHERE id = %s'%ir_brw.id)
                res_id=cr.fetchone()[0]
                if res_id:
                    model, res_id = tuple(res_id.split(','))
                    if not self.pool.get(model).search(cr, uid, [('id','=',int(res_id))]):
                        unlk_ids.append(ir_brw.id)
                        test.append(True)
                    else:

                        #~ The resource being checked does exist!!!
                        #~ it cannot be unlinked
                        test.append(False)
                else:
                    #~ Applies to all resources signaled in fields_id
                    #~ the id cannot be unlinked
                    test.append(False)
            if all(test):
                res.append(id)
        #~ Sanitizing the ir_property table
        #~ These properties are pointing to a non-existent resource
        ir_obj.unlink(cr, uid, unlk_ids, context=context)
        return res

    def unlink(self, cr, uid, ids, context={}):
        if context is None: context= {}
        res = self._check_properties(cr, uid, ids, context=context)
        if res:
            return super(account_account, self).unlink(cr, uid, res, context=context)
        else:
            return True
account_account()
