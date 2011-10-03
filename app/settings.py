# settings for app

PAYPAL_ENDPOINT = 'https://svcs.sandbox.paypal.com/AdaptivePayments/' # sandbox
#PAYPAL_ENDPOINT = 'https://svcs.paypal.com/AdaptivePayments/' # production

PAYPAL_PAYMENT_HOST = 'https://www.sandbox.paypal.com/au/cgi-bin/webscr' # sandbox
#PAYPAL_PAYMENT_HOST = 'https://www.paypal.com/webscr' # production

PAYPAL_USERID = '*** REQUIRED ***'
PAYPAL_PASSWORD = '*** REQUIRED ***'
PAYPAL_SIGNATURE = '*** REQUIRED ***'
PAYPAL_APPLICATION_ID = 'APP-80W284485P519543T' # sandbox only
PAYPAL_EMAIL = '*** REQUIRED ***'

PAYPAL_COMMISSION = 0.2 # 20%

USE_IPN = False
USE_EMBEDDED = False
SHIPPING = False # not yet working properly; PayPal bug

# EMBEDDED_ENDPOINT = 'https://paypal.com/webapps/adaptivepayment/flow/pay'
EMBEDDED_ENDPOINT = 'https://www.sandbox.paypal.com/webapps/adaptivepayment/flow/pay'

# ebay settings
USE_EBAY = True
EBAY_DEVID = '*** YOUR EBAY DEVID ***'
EBAY_APPID = '*** YOUR EBAY APPID ***'
EBAY_CERTID = '*** YOUR EBAY CERTID ***'
EBAY_AUTHTOKEN = '*** YOUR EBAY TOKEN ***'

EBAY_ENDPOINT = 'https://api.sandbox.ebay.com/ws/api.dll' # sandbox
#EBAY_ENDPOINT = 'https://api.ebay.com/ws/api.dll' # live

EBAY_FIND_ENDPOINT = 'http://svcs.sandbox.ebay.com/services/search/FindingService/v1' # sandbox
#EBAY_FIND_ENDPOINT = 'http://svcs.ebay.com/services/search/FindingService/v1' # live
USE_EBAY_PRICER = False
