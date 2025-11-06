{
    "name" : "Babylon Customization",

    "category" : "Sales",
    "depends" : ['base','product','mrp','purchase_stock','stock','product_expiry','sale','purchase'],
    "author": "",
    'summary': 'customization',

    "website" : "",
    "data": [
        'security/ir.model.access.csv',
        'data/res_partner_demo.xml',
        'views/product_view.xml',
        'views/product_ingredients.xml',
        'views/product_formulas.xml',
        'views/product_components.xml',
        'views/stock_location.xml',
        'views/bom.xml',
        'views/sale_order.xml',
        'views/product_finished_goods.xml',



    ],
    "auto_install": False,
    "installable": True,

}

