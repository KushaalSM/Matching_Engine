from orderbook import OrderBook
from orders import create_order
from database import RedisDB

class MatchingEngine:
    def __init__(self, instrument_name, config) -> None:
        # Instrument being matched by this instance of the matching engine.
        self.instrument_name = instrument_name
        self.orderbook = OrderBook(instrument_name)
        self.pending_market_orders_list = []
        self.redis_db = RedisDB(config)

    def start_service(self):
        self.redis_db.create_connections()

        order_trigger = self.redis_db.get_pubsub_client(pattern="ORDER")
        # Triggered whenever there is an order update (new order arriving or old order getting cancelled)
        for message in order_trigger.listen():
            order_info = self.redis_db.extract_data_from_pubsub_message(message)
            if not order_info == {}:
                order = create_order(order_info)
                self.on_new_order(order)
            
            # Stopping mechanism to be added.
        
        self.redis_db.destroy_connections()
        return

    def on_new_order(self, order):
        if order.purpose == 'NEW' and order.order_type == 'MARKET':
            # Immediately execute market order.
            self.on_new_market_order(order)
        else:
            # Add the limit order to the orderbook and check for limit order matches.
            self.orderbook.on_new_order(order)
            self.check_limit_order_match()
        return

    def check_limit_order_match(self):
        bid_price, bid_quantity = self.orderbook.get_best_qoutes(quote_type='BID')
        ask_price, ask_quantity = self.orderbook.get_best_qoutes(quote_type='ASK')
        if bid_price >= ask_price:
            # If there is a price match, execute the matched orders.
            matched_quantity = min(bid_quantity, ask_quantity)
            self.orderbook.on_order_match(quote_type='BID', quantity=matched_quantity)
            self.orderbook.on_order_match(quote_type='ASK', quantity=matched_quantity)
        return

    def on_new_market_order(self, order):
        """
        Method to execute market orders without adding them to the orderbook.
        """
        quantity = order.disclosed_quantity
        opposite_quote_type = 'BID' if order.direction == 'Sell' else 'ASK'
        while not order._is_filled():
            _, best_quantity_available = self.orderbook.get_best_qoutes(quote_type=opposite_quote_type)
            matched_quantity = min(best_quantity_available, quantity)
            self.orderbook.on_order_match(quote_type=opposite_quote_type, quantity=matched_quantity)
            order._update_filled_quantity(matched_quantity)
            if order._quantity_release_needed():
                order._release_quantity()
        return

    def execute_pending_market_orders(self):
        for order in self.pending_market_orders_list:
            pass
        return

