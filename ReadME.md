## GET (/invoice)
This endpoint is used to get all present invoices.
if we provide invoice's id it generates a filtered data.

## POST (/invoice)
This endpoint is used to create a new invoice.

The json file to send is as follows:
```
{
    "customer_name" :,
    "billing_address":,
    "shipping_address":,
    "GSTIN" :,
    "total_amount" : ,
    "invoice_items":[
        {
            "item_name":,
            "quantity" :,
            "price" :,
            "amount":,
        },
        {
            "item_name":,
            "quantity" :,
            "price" :,
            "amount":,
        }
        
    ], 
    "invoice_bill_sundries":[
        {
            "name":,
            "amount":,
        },
        {
            "name":,
            "amount":,
        },
    ]
}
```

## PUT (/invoice)
This endpoint is used to update an existing invoice or invoice item or invoice sundry.

This functionality is done using the action attribute.

if action = "invoice"

The json file to send is as follows:
```
{
    "action":"invoice",
    "date":,
    "customer_name" :,
    "billing_address":,
    "shipping_address":,
    "GSTIN" :,
}
```
if action = "invoiceItem"

The json file to send is as follows:
```
{
    "action":"invoiceItem",
    "quantity" :,
    "price":,
    "amount":,
}
```
if action = "invoiceSundry"

The json file to send is as follows:
```
{
    "action":"invoiceSundry",
    "name":,
    "amount":
}
```
## DELETE
This endpoint is used to delete an existinginvoice or invoice item or invoice sundry.

This functionality is done using the action attribute.

if action = "invoice"

The json file to send is as follows:
```
{
    "action":"invoice",
    "id":
}
```
if action = "invoiceItem"

The json file to send is as follows:
```
{
    "action":"invoiceItem",
    "id":
}
```
if action = "invoiceSundry"

The json file to send is as follows:
```
{
    "action":"invoiceSundry",
    "id":
}
```