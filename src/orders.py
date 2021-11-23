import datetime as dt
from random import randint

class Order:
    order_request_contents = {
        'client_id': int,
        'custom_id': str
        }

    def __init__(self) -> None:
        self.client_id = None
        self.custom_id = None
        self.order_id = None
        self.arrival_time = dt.datetime.now()
    
    def _verify_and_set_order_request(self, order_request_dict, order_request_contents=None):
        if not order_request_contents:
            order_request_contents = self.order_request_contents

        for key in order_request_contents:
            if key in order_request_dict:
                if isinstance(order_request_dict[key], order_request_contents[key]):
                    self.__setattr__(key, order_request_dict[key])
                else:
                    raise TypeError(f"'{key}' field must have type {order_request_contents[key]} \
                        but Invalid type passed : {order_request_dict[key]}")
            else:
                raise Exception(f"{key} field not present in the request.")
        
        self._set_order(order_request_dict)
        return
    
    def _set_order(self, order_dict):
        """
        Set the class attributes.
        """
        for key, value in order_dict.items():
            self.__setattr__(key, value)
        return
        

class NewOrder(Order):
    """
    This is an order object present at a particular level. This has all the neccessary data regarding a particular order placed 
    by a particular client.
    """
    order_request_contents = {
        'order_type': str,
        'direction': str,
        'instrument_name': str,
        'price': float,
        'total_quantity': int,
        'disclosed_quantity': int
    }
    order_type_choices = ['LIMIT', 'MARKET']
    direction_choices = ['BUY', 'SELL']

    def __init__(self, order_request_dict) -> None:
        super().__init__()
        self.order_purpose = 'NEW'
        self.order_type = None
        self.direction = None
        self.instrument_name = None
        self.price = None
        self.total_quantity = None
        self.disclosed_quantity = None

        self.filled_quantity = 0
        self.display_quantity = None
        super()._verify_and_set_order_request(order_request_dict)
        self._verify_and_set_order_request(order_request_dict)

    def _verify_and_set_custom_attributes(self):
        """
        Verifies the order request and populates the class attributes.

        ###############################################################################################
        Need to seperate the 'verify' and 'set' parts.
        ###############################################################################################
        """
        # Quantity check
        if self.disclosed_quantity > self.total_quantity:
            raise ValueError(f"disclosed_quantity({self.disclosed_quantity}) must be less \
                than or equal to total_quantity({self.total_quantity})")

        # Quantity to show in the orderbook.
        self.display_quantity = self.disclosed_quantity
        self.order_id = randint(1, 1000000)

        # Field specific checks
        for attribute in ['order_type', 'direction']:
            attribute_value = self.__getattribute__(attribute)
            if attribute_value not in self.__getattribute__(f"{attribute}_choices"):
                raise ValueError(f"'{attribute_value}' not a valid value for the field {attribute}")

        for attribute in ['price', 'total_quantity', 'disclosed_quantity']:
            attribute_value = self.__getattribute__(attribute)
            if attribute_value <= 0:
                raise ValueError(f"Value of field {attribute} must be non-zero. Instead it is '{attribute_value}'")
            
        ############################### Add check for instrument_name based on regex ######################################
        #################################### Add check for arrival_time based on regex ########################################
        return
    
    def _release_quantity(self):
        """
        Release more quantity based on the disclosed quantity as and when the display quantity is filled.
        """
        self.display_quantity = min(self.total_quantity - self.filled_quantity, self.disclosed_quantity)
        return

    def _update_filled_quantity(self, filled_quantity):
        """
        Update the filled quantity for this order.
        """
        self.filled_quantity += filled_quantity
        self.display_quantity -= filled_quantity
        return
    
    def _is_filled(self):
        return self.filled_quantity == self.total_quantity
    
    def _quantity_release_needed(self):
        return self.display_quantity == 0 and self.filled_quantity != 0

class CancelOrder(Order):
    order_request_contents = {
        'order_id': int,
        'direction': str
    }
    direction_choices = ['BUY', 'SELL']

    def __init__(self, order_request_dict) -> None:
        super().__init__()
        self.order_purpose = 'CANCEL'
        self.direction = None
        super()._verify_and_set_order_request(order_request_dict)
        self._verify_and_set_order_request(order_request_dict)