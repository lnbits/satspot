window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      formDialogSatspot: {
        show: false,
        fixedAmount: true,
        data: {
          number_of_players: 2,
          buy_in: 1000,
          wallet: null
        }
      }
    }
  },
  methods: {
    async saveSatspotSettings() {
      let settings = {
        enabled: this.satspotSettings.enabled,
        haircut: this.satspotSettings.haircut,
        max_players: this.satspotSettings.max_players,
        max_bet: this.satspotSettings.max_bet
      }
      let method = ''
      if (this.satspotSettings.id != null) {
        settings.id = this.satspotSettings.id
        settings.wallet_id = this.satspotSettings.wallet_id
        settings.user_id = this.g.user.id
        method = 'PUT'
      } else {
        method = 'POST'
      }
      console.log(this.g.user)
      await LNbits.api
        .request(
          method,
          '/satspot/api/v1/satspot/settings',
          this.g.user.wallets[0].adminkey,
          settings
        )
        .then(response => {
          this.satspotSettings = response.data
          Quasar.Notify.create({
            type: 'positive',
            message: 'Satspot settings saved!'
          })
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    async getSatspotSettings() {
      await LNbits.api
        .request(
          'GET',
          '/satspot/api/v1/satspot/settings',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          console.log(response.data)
          this.satspotSettings.id = response.data.id
          this.satspotSettings.enabled = response.data.enabled
          this.satspotSettings.haircut = response.data.haircut
          this.satspotSettings.max_players = response.data.max_players
          this.satspotSettings.max_bet = response.data.max_bet
          this.satspotSettings.wallet_id = response.data.wallet_id
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    async createGame() {
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.satspotSettings.wallet_id
      })
      const data = {
        name: this.formDialogSatspot.data.title,
        number_of_players: parseInt(
          this.formDialogSatspot.data.number_of_players
        ),
        buy_in: parseInt(this.formDialogSatspot.data.buy_in),
        settings_id: this.satspotSettings.id
      }
      if (data.buy_in > this.satspotSettings.max_bet) {
        Quasar.Notify.create({
          type: 'negative',
          message: `Max bet is ${this.satspotSettings.max_bet}`
        })
        return
      }
      if (
        this.formDialogSatspot.number_of_players >
        this.satspotSettings.max_players
      ) {
        Quasar.Notify.create({
          type: 'negative',
          message: `Max players is ${this.satspotSettings.max_players}`
        })
        return
      }
      try {
        const response = await LNbits.api.request(
          'POST',
          '/satspot/api/v1/satspot',
          wallet.inkey,
          data
        )
        if (response.data) {
          this.activeGame = true

          const url = new URL(window.location)
          url.pathname = `/satspot/satspot/${this.satspotSettings.id}/${response.data}`
          window.open(url)
        }
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    }
  },
  async created() {
    // CHECK COINFLIP SETTINGS
    await this.getSatspotSettings()
  }
})
