const mapSatspots = obj => {
  obj.closing_date = Quasar.date.formatDate(new Date(obj.closing_date), 'YYYY-MM-DD HH:mm')
  return obj
}


window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      satspots: [],
      satspotsTable: {
        columns: [
          {name: 'id', align: 'left', label: 'ID', field: 'id'},
          {name: 'name', align: 'left', label: 'Name', field: 'name'},
          {
            name: 'closing_date',
            align: 'right',
            label: 'Closing Date',
            field: 'closing_date'
          },
          {
            name: 'buy_in',
            align: 'left',
            label: 'buy_in',
            field: 'buy_in'
          },
          {
            name: 'players',
            align: 'left',
            label: 'players',
            field: 'players'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
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
    exportCSV() {
      LNbits.utils.exportCSV(this.satspotsTable.columns, this.satspots)
    },
    async getSatspotGames() {
      await LNbits.api
        .request(
          'GET',
          '/satspot/api/v1/satspot',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          this.satspots = response.data.map(obj => {
            return mapSatspots(obj)
          })
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
          url.pathname = `/satspot/satspot/${response.data}`
          window.open(url)
        }
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    }
  },
  async created() {
    // CHECK COINFLIP SETTINGS
    await this.getSatspotGames()
  }
})
