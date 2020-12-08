<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-select v-model="selectedCurrencies" :items="currencies" item-text="label" item-value="value" chips multiple filled deletable-chips filter></v-select>
        <v-card>
          <v-card-title>
            Pares de divisas activos
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <div class="d-flex align-center">
              <v-checkbox label="Activar OTC" v-model="isOTC"></v-checkbox>
              <v-spacer></v-spacer>
              <p>{{ currentTime }}</p>
            </div>
            <v-data-table
              :headers="headers"
              :items="signals"
              :items-per-page="100"
              multi-sort
              hide-default-footer
            ></v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

import axios from 'axios'
export default {
  name: 'CurrenciesList',

  data: () => {
    let currencies = [
      { label: 'EUR/USD', value: 'EURUSD' },
      { label: 'NZD/USD', value: 'NZDUSD' },
      { label: 'AUD/JPY', value: 'AUDJPY' },
      { label: 'EUR/AUD', value: 'EURAUD' },
      { label: 'AUD/USD', value: 'AUDUSD' },
      { label: 'EUR/JPY', value: 'EURJPY' },
      { label: 'EUR/NZD', value: 'EURNZD' },
      { label: 'EUR/GBP', value: 'EURGBP' },
      { label: 'GBP/USD', value: 'GBPUSD' },
      { label: 'GBP/JPY', value: 'GBPJPY' },
      { label: 'EUR/CAD', value: 'EURCAD' },
      { label: 'GBP/CHF', value: 'GBPCHF' },
      { label: 'AUD/CAD', value: 'AUDCAD' },
      { label: 'USD/CAD', value: 'USDCAD' },
      { label: 'USD/NOK', value: 'USDNOK' },
      { label: 'USD/CHF', value: 'USDCHF' },
      { label: 'USD/JPY', value: 'USDJPY' },
      { label: 'CAD/CHF', value: 'CADCHF' },
      { label: 'AUD/CHF', value: 'AUDCHF' },
      { label: 'GBP/CAD', value: 'GBPCAD' },
      { label: 'AUD/NZD', value: 'AUDNZD' },
      { label: 'GBP/NZD', value: 'GBPNZD' },
      { label: 'GBP/AUD', value: 'GBPAUD' },
      { label: 'CAD/JPY', value: 'CADJPY' },
      { label: 'CHF/JPY', value: 'CHFJPY' }
    ];

    currencies.sort((a, b) => {
      let result = 0;

      if (a.value > b.value) {
        result = 1
      } else if (a.value < b.value) {
        result = -1;
      }

      return result
    })

    return {
      // server: 'http://192.168.1.3:9001/',
      server: 'http://127.0.0.1:9000/',
      datetime: null,
      requesting: false,
      isOTC: false,
      currencies,
      selectedCurrencies: [],
      currentTime: null,
      dialog: false,
      interval: 60,
      headers: [
        { text: 'Currency', value: 'currency' },
        { text: 'Signal', value: 'signal' },
        { text: 'Previous signal', value: 'prev_signal' },
        { text: 'Short trend', value: 'short_trend' },
        { text: 'Medium trend', value: 'medium_trend' },
        { text: 'Long trend', value: 'long_trend' },
      ],
      signals: []
    }
  },

  created() {
    // Get current time from server
    axios.get(this.server + 'datetime').then(response => {
      const data = response.data
      let datetime = new Date();

      datetime = new Date(
        datetime.getFullYear(),
        datetime.getMonth(),
        datetime.getDate(),
        data[0],
        data[1],
        data[2]
      )
      this.datetime = datetime
    })
  },

  mounted() {
    this.watchSignal()
  },

  methods: {
    watchSignal() {
      setInterval(() => {
        this.clock();

        let snd = new Audio(require('@/assets/notification.mp3'));
        let seconds = this.datetime ? this.datetime.getSeconds(): -1;

        if (this.selectedCurrencies.length > 0 && seconds === 59 && !this.requesting) {
          this.requesting = true;

          let params = {
            currencies: this.selectedCurrencies.join(';')
          }

          if (this.isOTC) {
            params = {
              ...params,
              is_otc: true
            }
          }

          axios.get(this.server + 'signals', { params }).then(response => {
            let data = response.data;
            let emit_beep = false;
            let signals = [];
  
            data.forEach(item => {
              let signal = item.signal;
              let prev_signal = ''

              if (signal !== '') {
                emit_beep = true;
              }

              for (let index = 0; index < this.signals.length; index++) {
                const element = this.signals[index];
                if (item.currency === element.currency) {
                  prev_signal = element.signal;
                  break;
                }
              }

              signals.push({
                ...item,
                signal,
                currency: item.currency,
                prev_signal,
              });
            });

            this.signals = signals;

            if (emit_beep) snd.play();
            this.requesting = false
          });
        }
      }, 1000)
  
    },

    retrieveSignals() {

    },

    clock() {
      this.datetime.setMilliseconds(this.datetime.getMilliseconds() + 1000);

      let seconds = this.datetime.getSeconds();
      let minutes = this.datetime.getMinutes();
      let hours = this.datetime.getHours();

      let currentTime = hours + ":" + minutes + ":" + seconds;
      this.currentTime = currentTime
    },

    order(a, b) {
      // Use toUpperCase() to ignore character casing
      const bandA = a.currency.toUpperCase();
      const bandB = b.currency.toUpperCase();

      let comparison = 0;
      if (bandA > bandB) {
        comparison = 1;
      } else if (bandA < bandB) {
        comparison = -1;
      }
      return comparison;
    },

    toggleCurrency(item) {
      const i_active = this.selectedCurrencies.indexOf(item);
      const i_currencies = this.currencies.indexOf(item);

      if (i_active < 0) {
        this.selectedCurrencies.push(item);
        this.currencies.splice(i_currencies, 1)
      } else {
        this.currencies.push(item)
        this.selectedCurrencies.splice(i_active, 1);
      }

      this.currencies.sort(this.order)
      this.selectedCurrencies.sort(this.order)
    }
  }
}
</script>

<style lang="sass">
.complete-list
  overflow-y: scroll

.v-list-item--link
  &::before
    background-color: transparent !important

.v-list-item__title
  max-width: 100px

.complete-space
  display: inline-block !important
  width: 100%
</style>