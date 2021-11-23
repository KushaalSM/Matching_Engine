from orderbook import OrderBook

class MatchingEngine:
    def __init__(self, instrument_name) -> None:
        # Instrument being matched by this instance of the matching engine.
        self.instrument_name = instrument_name
        self.orderbook = OrderBook(instrument_name)
        self.pending_market_orders_list = []

    def on_new_order(self, order):
        if order.purpose == 'NEW' and order.order_type == 'MARKET':
            self.on_new_market_order(order)
        else:
            self.orderbook.on_new_order(order)
            self.check_limit_order_match()
        return

    def check_limit_order_match(self):
        
        bid_price, bid_quantity = self.orderbook.get_best_qoutes(quote_type='BID')
        ask_price, ask_quantity = self.orderbook.get_best_qoutes(quote_type='ASK')
        if bid_price >= ask_price:
            matched_quantity = min(bid_quantity, ask_quantity)
            self.orderbook.on_order_match(quote_type='BID', quantity=matched_quantity)
            self.orderbook.on_order_match(quote_type='ASK', quantity=matched_quantity)
        return

    def on_new_market_order(self, order):
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

