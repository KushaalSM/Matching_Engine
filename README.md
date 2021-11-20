# Matching_Engine

## Disclaimer : 
### a) '*' before a functionality of a module implies that functionality is in a state of development and isn't frozen. I will be trying out different ideas and implementations for these starred functionalities.
### b) '#' before a functionality of a module implies that functionality isn't completed yet. Some aspects of the functionality described are yet to be implemented.

## Description:
This is a pet project wherein I am building an Electronic Matching Engine. A Matching Engine is a module which matches incoming buy and sell orders and executes trades. This is a project that will be in a constant state of development and upgrades.

There are 2 main modules in this project - 
### * 1) Orderbook : This is a list of buy and sell orders for a particular instrument that are open and yet to be executed (when the price is available). The orderbook can be decomposed into smaller components as described below (increasing granularity) -
#### i) Orderpage : This consists of the orders in a particular direction i.e. either buy or sell. The Buy orderpage has orders arranged in descending order of the limit prices, whereas the Sell orderpage has orders arranged in ascending orders of the limit prices.
#### ii) Orderlevel : Each orderpage has different orderlevels, one for each price at which orders were placed. Multiple orders being placed at the same price will be added to a queue in a time priority fashion i.e. earliest order will have top priority when a matching order is available.
#### iii) Order : This is the smallest component. Every limit order placed will be added to a particular orderlevel and will be executed when the limit price is available and when all orders in front of this order are executed. Market orders are immediately executed without being added to any orderlevel.

### * 2) Matching Engine : This is the brain of any exchange. This monitors the orderbook and whenever there is an overlap between the bid orderpage and ask orderpage, it immediately records the overlap as an executed trade and logs the relevant information like time, average price.