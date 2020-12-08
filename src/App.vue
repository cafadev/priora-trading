<template>
  <v-app>
    <v-app-bar
      color="primary"
      app
      dark
      dense
    >
      <div class="d-flex align-center">
        <h1 class="display-1">Priora</h1>
      </div>
    </v-app-bar>

    <main>
      <CurrenciesList/>
    </main>

  </v-app>
</template>

<script>
import CurrenciesList from './views/CurrenciesList';

export default {
  name: 'App',

  components: {
    CurrenciesList,
  },

  data: () => ({}),

  beforeCreate() {
    document.title = 'Priora - Binary Option Signals'
  }
};
</script>

<style lang="sass" scoped>
main
  padding-top: 3rem
</style>
