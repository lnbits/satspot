const mapSatspots = (obj) => {
  obj._data = _.clone(obj)
  obj.closing_date = Quasar.date.formatDate(
    new Date(obj.closing_date),
    "YYYY-MM-DD HH:mm",
  )
  return obj
}

window.app = Vue.createApp({
  el: "#vue",
  mixins: [windowMixin],
  data() {
    return {
      satspots: [],
      players: {
        show: false,
        data: [],
      },
      satspotsTable: {
        columns: [
          { name: "id", align: "left", label: "ID", field: "id" },
          { name: "name", align: "left", label: "Name", field: "name" },
          {
            name: "closing_date",
            align: "right",
            label: "Closing Date",
            field: "closing_date",
          },
          {
            name: "buy_in",
            align: "left",
            label: "buy_in",
            field: "buy_in",
          },
          {
            name: "haircut",
            align: "left",
            label: "haircut",
            field: "haircut",
          }
        ],
        pagination: {
          rowsPerPage: 10,
        },
      },
      formDialogSatspot: {
        show: false,
        fixedAmount: true,
        data: {
          name: "",
          number_of_players: 2,
          buy_in: 1000,
          wallet: null,
        },
      },
    }
  },
  methods: {
    exportCSV() {
      LNbits.utils.exportCSV(this.satspotsTable.columns, this.satspots)
    },
    async getSatspotGames() {
      await LNbits.api
        .request(
          "GET",
          "/satspot/api/v1/satspot",
          this.g.user.wallets[0].adminkey,
        )
        .then((response) => {
          if(response.data != null) {
            console.log(response.data)
            this.satspots = response.data
          }
        })
        .catch((err) => {
          LNbits.utils.notifyApiError(err)
        })
    },
    async openPlayers(players) {
      this.players.show = true
      this.players.data = players.split(',')
    },
    async createGame() {
      const date = new Date(this.formDialogSatspot.data.closing_date)
      const unixTimestamp = Math.floor(date.getTime() / 1000)
      console.log(parseInt(unixTimestamp))
      const data = {
        name: this.formDialogSatspot.data.name,
        buy_in: this.formDialogSatspot.data.buy_in,
        closing_date: parseInt(unixTimestamp),
        haircut: this.formDialogSatspot.data.haircut
      }
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.formDialogSatspot.data.wallet
      })
      try {
        const response = await LNbits.api.request(
          "POST",
          "/satspot/api/v1/satspot",
          wallet.adminkey,
          data,
        )
        if (response.data) {
          this.satspots = response.data.map(mapSatspots)
          this.formDialogSatspot.show = false
        }
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    deleteSatspot(satpotid) {
      const satspot = _.findWhere(this.satspots, {id: satpotid})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this satspot?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/satspot/api/v1/satspot/' + satpotid,
              _.findWhere(this.g.user.wallets, {id: satspot.wallet}).adminkey
            )
            .then(response => {
              this.satspots = _.reject(this.satspots, obj => obj.id === satpotid)
            })
            .catch(err => {
              LNbits.utils.notifyApiError(err)
            })
        })
    },
  },
  async created() {
    // CHECK COINFLIP SETTINGS
    await this.getSatspotGames()
  },
})
