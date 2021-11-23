import datetime as dt
from typing import Type

class OrderBook:
    def __init__(self, instrument_name) -> None:
        self.bid_order_page = None
        self.ask_order_page = None

    def initialize_orderbook(self):
        self.bid_order_page = OrderPage('BID')
        self.ask_order_page = OrderPage('ASK')
        return

    def on_new_order(self, order):
        order_type = 'bid' if order.direction == 'BUY' else 'ask'
        self.__getattribute__(f"{order_type}_order_page").on_new_order(order)
        return

    def get_best_qoutes(self, quote_type):
        if not quote_type in ['BID', 'ASK']:
            raise ValueError(f"Invalid quote_type {quote_type}")
        return self.__getattribute__(f"{quote_type.lower()}_order_page").get_best_level_info()

    def execute(self):
        return

class OrderPage:
    """
    This holds all the order levels for bid/ask sorted in price priority.
    """
    def __init__(self, page_type):
        # page_type can be one of two values : BID or ASK
        self.page_type = page_type
        assert self.page_type in ['ASK', 'BID']
        
        # Dictionary containing the orderlevels(value) for the prices(key).
        self.order_level_dict = {}

        # Holds the best price for the orderpage.
        self.best_price_level = None
    
    def _update_best_level(self):
        self.best_price_level = (min if self.page_type == 'ASK' else max)(self.order_level_dict)
        return

    def get_best_level_info(self):
        quantity_at_best_price = self.order_level_dict[self.best_price_level].combined_quantity
        return self.best_price_level, quantity_at_best_price
    
    def on_new_order(self, order):
        order_price = order.price
        if order.order_purpose == 'NEW':
            if not order_price in self.order_level_dict:
                self._add_order_level(order_price, order)
            self.order_level_dict[order_price].add_order(order)
        elif order.order_purpose == 'CANCEL':
            if not order_price in self.order_level_dict:
                raise Exception(f"Order level for the price {order_price} not present in the orderbook.")
            self.order_level_dict[order_price].delete_order(order.order_id)
        return

    def _add_order_level(self, price, order):
        self.order_level_dict[price] = OrderLevel(order)
        return

    def _delete_order_level(self):
        return

class OrderLevel:
    """
    This is one level in the orderbook. This has the list of all orders with the same direction and price.
    The orders are sorted based on the order placement times.
    All new orders are appended to the list and filled orders are popped from the beginning of the list.
    """
    def __init__(self, order) -> None:
        # List of Order objects sorted by arrival_time.
        self.order_list = [order]

        # Set the price of this orderlevel.
        self.price = order.price

        # Total quantity of all orders at this price level.
        self.combined_quantity = order.display_quantity

        # Number of different orders at this price level.
        self.number_of_orders = 1
    
    def add_order(self, order):
        """
        Update the order_list with the new order.
        Update the combined_quantity at this price level.
        """
        self.order_list.append(order)
        self.number_of_orders += 1
        self._update_quantity(order.display_quantity)
        return
    
    def delete_order(self, order_id):
        """
        Remove the order corresponding to the order_id and update the combined quantity at this level.
        """
        idx = 0
        order_list_length = len(self.order_list)
        order_found = False
        while idx < order_list_length:
            if self.order_list[idx].order_id == order_id:
                order_found = True
                # Argument passed is negative in order to decrement the combined_quantity
                self._update_quantity(-self.order_list[idx].display_quantity)
                self.order_list.pop(idx)
                self.number_of_orders -= 1
                break
        if not order_found:
            # raise Exception(f"Order with the order_id {order_id} not present.")
            pass
        return

    def _update_quantity(self, updated_quantity):
        self.combined_quantity += updated_quantity
        return

    def fill_quantity(self, quantity_to_match):
        """
        Distribute the quantity_to_match among the orders in the queue.
        """
        # Step 1 : Fill the orders.
        for order in self.order_list:
            fill_quantity = min(quantity_to_match, order.display_quantity)
            quantity_to_match -= fill_quantity
            order._update_filled_quantity(fill_quantity)
            if quantity_to_match == 0:
                break
        # Post order fill tasks.
        self._on_fill()

        return
    
    def _on_fill(self):
        """
        2 tasks must be performed whenever there is an order fill.
        1) Completely filled orders must be removed from the order_list at this level.
        2) If an order isn't completely filled, the remaining quantity must be released and the order must be pushed back to the 
           end of the order_list.
        """
        order_list_length = len(self.order_list)
        idx = 0
        while idx < order_list_length:
            if self.order_list[idx]._is_filled():
                # If the order is completely filled, pop out the order from the order_list.
                self.order_list.pop(idx)
                self.number_of_orders -= 1
                order_list_length = max(order_list_length - 1, 0)
            
            elif self.order_list[idx]._quantity_release_needed():
                # If the order isn't completely filled, release the disclosed quantity and push the order to the end of the order_list.
                order = self.order_list.pop(idx)
                order._release_quantity()
                self.order_list.append(order)
                order_list_length = max(order_list_length - 1, 0)
            else:
                idx += 1
        return
    
    def is_empty(self):
        return self.order_list == []

    def __str__(self) -> str:
        if self.order_list == []:
            print("Order Level Empty")
        order_attribute_list = ['arrival_time', 'direction', 'price', 'display_quantity']
        for attribute in order_attribute_list:
            print(attribute, end=' ')
        for order in self.order_list:
            for attribute in order_attribute_list:
                print(f"{order.__getattribute__(attribute)}", end=' ')
            print('\n')
        return