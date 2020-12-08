import datetime
from operator import index
from rest_framework.views import APIView
from rest_framework.response import Response
from tapy import Indicators
from iqoptionapi.stable_api import IQ_Option
import time
import pandas
import ntplib

from ta.trend import ADXIndicator
import calendar

Iq=IQ_Option("kershingf@gmail.com","T3.md5.pp7.3.4.PI")
Iq.connect()


class SignalTracker:

    def __init__(self, *args, **kwargs):
        currencies = kwargs.get('currencies')[0]

        unique_currencies = list(dict.fromkeys(currencies.split(';')))
        is_otc = True if 'is_otc' in kwargs else False

        self.currencies = unique_currencies if not is_otc else [p + '-OTC' for p in unique_currencies]
        self.timelapse = 60

    def get_candels(self, currency):
        """Get last 80 minutes price info from IQ option

        Args:
            currency (str): currency to get price info

        Returns:
            list of dicts with last 80 minutes price info
        """
        t = time.time() + 125
        return Iq.get_candles(currency, self.timelapse, 80, t)

    def signal(self, df):
        price_close = df.iloc[-1].Close
        price_open = df.iloc[-1].Open

        xs_ma = df.iloc[-1].xs_ma
        medium_ma = df.iloc[-1].medium_ma
        long_ma = df.iloc[-1].long_ma

        adx_pos = df.iloc[-1].adx_pos
        adx_neg = df.iloc[-1].adx_neg

        bullish_conditions = [
            xs_ma > medium_ma,
            medium_ma > long_ma,
            price_close > medium_ma,
            price_close < price_open,
            adx_pos > 20,
            adx_neg < 20
        ]

        bearish_conditions = [
            xs_ma < medium_ma,
            medium_ma < long_ma,
            price_close < medium_ma,
            price_close > price_open,
            adx_pos < 20,
            adx_neg > 20
        ]

        if all(bullish_conditions):
            signal = 'THROWBACK'
        elif all(bearish_conditions):
            signal = 'PULLBACK'
        else:
            signal = ''

        return signal

    def run(self):
        response = []
        for currency in self.currencies:
            candels = self.get_candels(currency)

            data = pandas.DataFrame(candels).rename(columns={
                'open':'Open', 'close':'Close', 'max':'High', 'min':'Low', 'volume':'Volume'
            })

            indicators = Indicators(data)
            indicators.ema(period=10, column_name='xs_ma', apply_to='Close')
            indicators.ema(period=15, column_name='short_ma', apply_to='Close')
            indicators.ema(period=20, column_name='medium_ma', apply_to='Close')
            indicators.ema(period=30, column_name='long_ma', apply_to='Close')

            adx = ADXIndicator(data['High'], data['Low'], data['Close'], 14, fillna=True)

            df = indicators.df
            df['adx_pos'] = adx.adx_pos()
            df['adx_neg'] = adx.adx_neg()

            signal = self.signal(df)

            response.append({
                'currency': currency,
                'signal': signal,
                'short_trend': round(indicators.df['xs_ma'].iloc[-1], 5),
                'medium_trend': round(indicators.df['medium_ma'].iloc[-1], 5),
                'long_trend': round(indicators.df['long_ma'].iloc[-1], 5)
            })

        return response


class Signal(APIView):

    def get(self, request):
        currencies = request.query_params.get('currencies')
        currencies = currencies.split(';')
        
        if not currencies:
            return Response({})

        signal_tracker = SignalTracker(**request.query_params)
        return Response(signal_tracker.run())


class DatetimeRetrieve(APIView):

    def get(self, request):
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')

        t = time.ctime(response.tx_time-1).split(' ')[-2].split(':')
        return Response([int(x) for x in t])
