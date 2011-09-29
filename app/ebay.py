# interface to ebay API
import base64
import datetime
import hashlib
import logging
import os
import re
import uuid

from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

import settings

class Add(object):
  '''add an item to be listed at eBay'''
  def __init__(self, item, host_url):
    item.uuid = uuid.uuid4().hex

    headers = {
      'X-EBAY-API-COMPATIBILITY-LEVEL': '731',
      'X-EBAY-API-DEV-NAME': settings.EBAY_DEVID,
      'X-EBAY-API-APP-NAME': settings.EBAY_APPID,
      'X-EBAY-API-CERT-NAME': settings.EBAY_CERTID,
      'X-EBAY-API-SITEID': '0',
      'X-EBAY-API-CALL-NAME': 'AddItem',
    }

    data = {
      'title': item.title,
      'description': item.description,
      'category': 1000, # TODO
      'price': item.price_dollars(),
      'paypal_email': settings.PAYPAL_EMAIL,
      'image_url': "%s/image/%s/" % ( host_url, item.key() ),
      'uuid': item.uuid,
      'ebay_token': settings.EBAY_AUTHTOKEN
    }
    logging.info( data )
    template_path = os.path.join(os.path.dirname(__file__), 'templates/ebay_add.xml')
    self.raw_request = template.render(template_path, data)
    logging.info( 'ebay request: ' + self.raw_request )
    self.raw_response = url_request( settings.EBAY_ENDPOINT, data=self.raw_request, headers=headers ).content()
    logging.info( 'ebay response: ' + self.raw_response )
    
    # extract item id and set success flag
    match = re.search( "<ItemID>([^<]*)</ItemID>", self.raw_response )
    if match != None:
      self.success = True
      self.item_id = match.group(1)
      item.ebay_item_id = self.item_id
      item.put()
    else:
      self.success = False
    
class Remove(object):
  def __init__(self, item):
    headers = {
      'X-EBAY-API-COMPATIBILITY-LEVEL': '731',
      'X-EBAY-API-DEV-NAME': settings.EBAY_DEVID,
      'X-EBAY-API-APP-NAME': settings.EBAY_APPID,
      'X-EBAY-API-CERT-NAME': settings.EBAY_CERTID,
      'X-EBAY-API-SITEID': '0',
      'X-EBAY-API-CALL-NAME': 'EndFixedPriceItem',
    }

    data = {
      'item_id': item.ebay_item_id,
      'ebay_token': settings.EBAY_AUTHTOKEN
    }
    template_path = os.path.join(os.path.dirname(__file__), 'templates/ebay_remove.xml')
    self.raw_request = template.render(template_path, data)
    logging.info( 'ebay request: ' + self.raw_request )
    self.raw_response = url_request( settings.EBAY_ENDPOINT, data=self.raw_request, headers=headers ).content()
    logging.info( 'ebay response: ' + self.raw_response )

class Notification(object):
  '''handle an incoming notification from ebay'''
  def __init__(self, content):
    logging.info( 'ebay notification: ' + content )

    if self.validate( content ):
      # extract item id and set success flag
      match = re.search( "<ItemID>([^<]*)</ItemID>", content )
      if match != None:
        self.item_id = match.group(1)
        match = re.search( "<TransactionID>([^<]*)</TransactionID>", content )
        if match != None:
          self.transaction_id = match.group(1)
          self.success = True
        else:
          self.success = False
      else:
        self.success = False
    else:
      logging.info( 'notification failed to validate' )
      self.success = False

  def validate( self, content ):
    # get incoming signature
    match = re.search( "<ebl:NotificationSignature[^>]*>([^<]*)</ebl:NotificationSignature>", content )
    if match != None:
      incoming_signature = match.group(1)
      # get timestamp
      match = re.search( "<Timestamp>([^<]*)</Timestamp>", content )
      if match != None:
        timestamp = match.group(1)
        expected_signature_input = "%s%s%s%s" % ( timestamp, settings.EBAY_DEVID, settings.EBAY_APPID, settings.EBAY_CERTID )
        md5 = hashlib.md5()
        md5.update( expected_signature_input )
        expected_signature = base64.b64encode( md5.digest() )
        if incoming_signature == expected_signature:
          # check timestamp
          ebay_datetime = datetime.datetime.strptime(timestamp.split(".")[0] + "UTC", '%Y-%m-%dT%H:%M:%S%Z' ) # dodgy ISO parser
          datediff = datetime.datetime.utcnow() - ebay_datetime
          if datediff < datetime.timedelta( minutes=10 ) and datediff > datetime.timedelta( minutes=-10 ):
            return True
          else:
            logging.info( "notification timestamp outside 10 minute range" )
        else:
          logging.info( "notification signatures did not match: expected %s incoming %s" % ( expected_signature, incoming_signature ) )
      else:
        logging.info( "notification timestamp not found" )
    else:
      logging.info( "notification signature not found" )
    return False

class Order(object):
  '''get order details of a completed transaction'''
  def __init__(self, item, transaction ):
    headers = {
      'X-EBAY-API-COMPATIBILITY-LEVEL': '731',
      'X-EBAY-API-DEV-NAME': settings.EBAY_DEVID,
      'X-EBAY-API-APP-NAME': settings.EBAY_APPID,
      'X-EBAY-API-CERT-NAME': settings.EBAY_CERTID,
      'X-EBAY-API-SITEID': '0',
      'X-EBAY-API-CALL-NAME': 'GetOrders',
    }

    data = {
      'item_id': item.ebay_item_id,
      'transaction_id': transaction,
      'ebay_token': settings.EBAY_AUTHTOKEN
    }
    template_path = os.path.join(os.path.dirname(__file__), 'templates/ebay_orders.xml')
    self.raw_request = template.render(template_path, data)
    logging.info( 'ebay request: ' + self.raw_request )
    self.raw_response = url_request( settings.EBAY_ENDPOINT, data=self.raw_request, headers=headers ).content()
    logging.info( 'ebay response: ' + self.raw_response )
    self.success = self.raw_response.find( "<eBayPaymentStatus>NoPaymentFailure</eBayPaymentStatus>" )

class SetNotifications(object):
  '''register to receive (or not receive) eBay notifications'''
  def __init__(self, enable, host_url):
    headers = {
      'X-EBAY-API-COMPATIBILITY-LEVEL': '731',
      'X-EBAY-API-DEV-NAME': settings.EBAY_DEVID,
      'X-EBAY-API-APP-NAME': settings.EBAY_APPID,
      'X-EBAY-API-CERT-NAME': settings.EBAY_CERTID,
      'X-EBAY-API-SITEID': '0',
      'X-EBAY-API-CALL-NAME': 'SetNotificationPreferences',
    }

    if enable:
      enable_status = 'Enable'
    else:
      enable_status = 'Disable'

    data = {
      'enable': enable_status,
      'notification_url': "%s/notification" % host_url,
      'ebay_token': settings.EBAY_AUTHTOKEN
    }
    logging.info( data )
    template_path = os.path.join(os.path.dirname(__file__), 'templates/ebay_set_notifications.xml')
    self.raw_request = template.render(template_path, data)
    logging.info( 'ebay request: ' + self.raw_request )
    self.raw_response = url_request( settings.EBAY_ENDPOINT, data=self.raw_request, headers=headers ).content()
    logging.info( 'ebay response: ' + self.raw_response )
    self.success = ( self.raw_response.find( '<Ack>Success</Ack>' ) != -1 )

class url_request( object ):
  '''wrapper for urlfetch'''
  def __init__( self, url, data=None, headers={} ):
    # urlfetch - validated
    self.response = urlfetch.fetch( url, payload=data, headers=headers, method=urlfetch.POST, validate_certificate=True )
    # urllib - not validated
    #request = urllib2.Request(url, data=data, headers=headers) 
    #self.response = urllib2.urlopen( https_request )

  def content( self ):
    return self.response.content

  def code( self ):
    return self.response.status_code

