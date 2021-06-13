from binance import Client
import json

class Binance:

    def __init__(self):
        self.apiKey = ""
        self.api_secret = ""
        self.client = Client(self.apiKey, self.api_secret)
        self.priceMedium = "BUSD"
        self.assets = self.getAssets()
        self.assetPrices = self.getAssetPrices()
        self.historicalPrices = self.getHistoricalPrices()

    def getAssets(self):
        assets = []
        assetInfo = self.client.get_account()
        assetInfo = assetInfo["balances"]
        for entry in assetInfo:
            if float(entry["free"]) > 0.0:
                assets.append(entry)
        return assets

    def getAssetPrices(self):
        toReturn = {}
        assetKeys = set()
        for asset in self.assets:
            assetKeys.add(asset["asset"] + self.priceMedium)
        #print(assetKeys)
        tickerPrices = self.client.get_ticker()
        for ticker in tickerPrices:
            symbol = ticker["symbol"]
            if self.priceMedium in symbol[1:]:
                if symbol in assetKeys:
                    toReturn[symbol] = ticker["lastPrice"]
        return toReturn

    def getHistoricalPrices(self):
        historyPrices = {}
        for asset in self.assets:
            assetAmount = float(asset["free"])
            symbol = asset["asset"] + self.priceMedium
            # Extra hacky for my staked ethereum, its pegged at ETH prices anyways
            if symbol == "BETHBUSD":
                symbol = "ETHBUSD"
            if symbol in self.assetPrices.keys():
                klines = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2021")
                closePrices = []
                for kline in klines:
                    # Index 4 is our closing price, OHLCV
                    closePrices.append(float(kline[4]))
                historyPrices[asset["asset"]] = closePrices
        return historyPrices

    def getAccountValue(self):
        accountValue = {}
        accountTotal = 0.0
        for asset in self.assets:
            assetAmount = float(asset["free"])
            symbol = asset["asset"] + self.priceMedium
            # Extra hacky for my staked ethereum, its pegged at ETH prices anyways
            if symbol == "BETHBUSD":
                symbol = "ETHBUSD"
            if symbol in self.assetPrices.keys():
                assetPrice = float(self.assetPrices[symbol])
                holdingValue = assetAmount * assetPrice
                accountTotal += holdingValue
                accountValue[asset["asset"]] = holdingValue
        accountValue["total"] = accountTotal
        return accountValue

    def getAccountPerformance(self):
        performance = {}
        # For each crypto we provide the following performance metrics
        # Performance today so far
        # Performance this week
        # Performance 30 days ago
        # Performance total since jan 1st
        totalTodayDiff = 0.0
        totalWeekDiff = 0.0
        totalLast30Diff = 0.0
        totalTotalDiff = 0.0
        currAccountValue = self.getAccountValue()
        currentPrices = self.getAssetPrices()
        for asset in currAccountValue.keys():
            if asset == "total":
                continue
            symbol = asset + self.priceMedium
            # Extra hacky for my staked ethereum, its pegged at ETH prices anyways
            if symbol == "BETHBUSD":
                symbol = "ETHBUSD"
            # Get the price right now
            if not symbol in currentPrices:
                continue

            # Lets work out the performances
            today = len(self.historicalPrices[asset]) - 1
            yesterday = today - 1
            lastWeek = today - 7
            last30 = today - 30
            total = 0
            # Now get all percentage differences
            todayDiff = 1.0 - (self.historicalPrices[asset][yesterday] / float(currentPrices[symbol]))
            weekDiff = 1.0 - (self.historicalPrices[asset][lastWeek] / float(currentPrices[symbol]))
            last30Diff = 1.0 - (self.historicalPrices[asset][last30] / float(currentPrices[symbol]))
            totalDiff = 1.0 - (self.historicalPrices[asset][total] / float(currentPrices[symbol]))
            # Store percentages
            performance[asset] = [todayDiff, weekDiff, last30Diff, totalDiff]
            # Update total percentages
            totalTodayDiff += todayDiff
            totalWeekDiff += weekDiff
            totalLast30Diff += last30Diff
            totalTotalDiff += totalDiff
        performance[asset] = [totalTodayDiff, totalWeekDiff, totalLast30Diff, totalTotalDiff]
        print(performance)
        return performance

    def get10DayPerformance(self):
        currAccountValue = self.getAccountValue()
        del currAccountValue["total"]
        del currAccountValue["GBP"]
        prices = self.historicalPrices
        accountHistory = []
        for i in range(0, 10):
            currAccValue = 0.0
            for asset in self.assets:
                if asset["asset"] == "USDT":
                    continue
                assetAmount = float(asset["free"])
                dayPrice = self.historicalPrices[asset["asset"]][(len(self.historicalPrices[asset["asset"]]) - 1) - i]
                currAccValue += (dayPrice * assetAmount)
            accountHistory.append(currAccValue)
        return accountHistory