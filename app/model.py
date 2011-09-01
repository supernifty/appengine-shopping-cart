import decimal
import logging

from google.appengine.ext import db

import ebay
import settings

class Profile(db.Model):
  '''extra user details'''
  owner = db.UserProperty()
  paypal_email = db.EmailProperty()  # for payment

  @staticmethod
  def from_user( u ):
    return Profile.all().filter( "owner = ", u ).get()

class Item(db.Model):
  '''an item for sale'''
  created = db.DateTimeProperty(auto_now_add=True)
  title = db.StringProperty()
  description = db.StringProperty()
  price = db.IntegerProperty() # cents
  available = db.IntegerProperty()
  image = db.BlobProperty()
  enabled = db.BooleanProperty()
  uuid = db.StringProperty() # ebay id
  ebay_item_id = db.StringProperty() # ebay id

  def price_dollars( self ):
    return self.price / 100.0

  def price_decimal( self ):
    return decimal.Decimal( str( self.price / 100.0 ) )

  @staticmethod
  def forsale():
    return Item.all().filter( "enabled", True ).filter( "available >", 0 ).fetch(10)

  def fulfil_web_order( self ):
    '''order has been completed'''
    self.available -= 1
    self.put()

    if settings.USE_EBAY and self.available == 0:
      ebay.Remove( self )

  def fulfil_ebay_order( self, transaction_id, host_url ):
    '''order has been completed'''
    purchase = Purchase( item=self, status='COMPLETED', ebay_transaction_id=transaction_id )
    purchase.put()

    self.available -= 1
    self.put()

    # relist if stock still available
    if self.available > 0:
      adder = ebay.Add( self, host_url )
      if adder.success:
        logging.info( "relisted %s" % self )
      else:
        logging.warn( "failed to relist %s" % self )

class Purchase(db.Model):
  '''a completed transaction'''
  item = db.ReferenceProperty(Item)
  purchaser = db.UserProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  status = db.StringProperty( choices=( 'NEW', 'CREATED', 'ERROR', 'CANCELLED', 'RETURNED', 'COMPLETED' ) )
  status_detail = db.StringProperty()
  secret = db.StringProperty() # to verify return_url
  debug_request = db.TextProperty()
  debug_response = db.TextProperty()
  paykey = db.StringProperty()
  shipping = db.TextProperty()
  ebay_transaction_id = db.StringProperty()
