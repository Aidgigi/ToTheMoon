import cbpro, time, json

class BasicClient:
    def __init__(self, secrets):
        self.auth = cbpro.AuthenticatedClient(secrets['API']['KEY'], secrets['API']['SECERET'], secrets['API']['PASSPHRASE'])

        self.buy_op =  False
        self.startup = True
        self.prices = []

        self.xlm_account = secrets['API']['XLM_ACCOUNT']
        self.usd_account = secrets['API']['USD_ACCOUNT']

        self.UP_TREND  = float(secrets['CONFIG']['UPWARD_TREND_THRESHOLD'])
        self.DIP       = float(secrets['CONFIG']['DIP_THRESHOLD'])
        self.PROFIT    = float(secrets['CONFIG']['PROFIT_THRESHOLD'])
        self.STOP_LOSS = float(secrets['CONFIG']['STOP_LOSS_THRESHOLD'])

        self.GRANULARITY = secrets['CONFIG']['GRANULARITY']

    def check_price(self):
        return float(self.auth.get_product_ticker(product_id = 'XLM-USD')['price'])

    def check_balance(self):
        account_usd = self.auth.get_account(self.usd_account)
        account_xlm = self.auth.get_account(self.xlm_account)
        return account_usd['balance'], account_xlm['balance']

    def sell_all(self):
        xlm = self.check_balance()[1]
        price = self.check_price()
        order = self.auth.place_market_order(product_id = "XLM-USD",
                                             side = "sell",
                                             size = xlm)
        print(f"Sold {xlm} lumens at ${price}.")
        return order

    def buy_all(self):
        usd = self.check_balance()[0]
        order = self.auth.place_market_order(product_id = "XLM-USD",
                                             side = "buy",
                                             funds = str(usd)[:8])
        print(f"Bought ${str(usd)[:8]} worth of lumens.")
        return order

    def attempt_trade(self):
        if self.startup:
            self.startup    = False
            self.last_price = self.check_price()
            time.sleep(self.GRANULARITY)

        current_price = self.check_price()
        movement = (current_price - self.last_price) / self.last_price * 100
        print(movement)

        if self.buy_op:
            if movement >= self.UP_TREND or movement <= self.DIP:
                self.last_price = current_price
                self.buy_all()
                self.buy_op = False

        if not self.buy_op:
            if movement >= self.PROFIT or movement <= self.STOP_LOSS:
                self.last_price = current_price
                self.sell_all()
                self.buy_op = True

    def main_loop(self):
        while True:
            try: self.attempt_trade()
            except Exception as e: print(f"Error! {e}")

            time.sleep(self.GRANULARITY)

secrets = json.load(open("./core/secrets.json", 'r'))
c = BasicClient(secrets)
c.main_loop()
