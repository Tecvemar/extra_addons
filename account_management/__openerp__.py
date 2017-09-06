# -*- encoding: utf-8 -*-
{
    "name" : "Account Management",
    "version" : "1.0",
    "depends" : ["base","product","account",'account_anglo_saxon'],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
    This module adds the field where the plan establishes the structure of accounts 
    and also adds functions that can be used for the ranking of accounts.
                    """,
    "website" : "http://Vauxoo.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [],
    "update_xml" : [
                    "view/account_company.xml",
                    "view/account_partner.xml",
                    "view/account_product.xml",
                    "view/product_order_view.xml",
                    "security/ir.model.access.csv",
                    "data/account_management_data.xml",],
    "active": False,
    "installable": True,
}
