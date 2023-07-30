<!--suppress JSUnresolvedVariable -->
<template>
  <div>
    <div class="recent-subtasks">
      <div class="carinfo-header">
        <h2>Parkovacie miesto</h2>
        <h3>B{{carId}}</h3>
        <span>TUKE areal</span>
      </div>
      <!-- ParkingSlot temperature -->
      <div class="subtasks">
        <div class="service">
          <v-icon>mdi-thermometer</v-icon>
          <div class="details">
            <h4>Teplota</h4>
          </div>
        </div>
        <div class="subtask-details">
          <div class="card bg-danger">
              <h4>{{currentTemperature}}°C</h4>
          </div>
        </div>
      </div>
      <!-- ParkingSlot humidity -->
      <div class="subtasks">
        <div class="service">
          <v-icon>mdi-water-percent</v-icon>
          <div class="details">
            <h4>Vlhkosť</h4>
          </div>
        </div>
        <div class="subtask-details">
          <div class="card bg-danger">
              <h4>{{currentHumidity}}%</h4>
          </div>
        </div>
      </div>
      <!-- ParkingSlot warning -->
      <div class="subtasks" v-if="warningType.valueOf() !== ParkingSlotWarning.None">
        <div class="service">
          <v-icon>{{isFreezing ? 'mdi-snowflake' : 'mdi-white-balance-sunny'}}</v-icon>
          <div class="details">
            <h4>{{isFreezing ? 'Možnosť námrazy' : 'Horúčava'}}</h4>
          </div>
        </div>
        <div class="subtask-details">
          <div class="card bg-danger">
            <v-icon :id="`alert-${isFreezing ? 'freezing' : 'overheating'}`">mdi-alert-outline</v-icon>
          </div>
        </div>
      </div>
      <!-- ParkSlot if accesible -->
      <div class="subtasks" v-if="isAccessible">
        <div class="service">
          <v-icon>mdi-wheelchair</v-icon>
          <div class="details">
            <h4>Vyhradené</h4>
            <p>miesto určené ZŤP</p>
          </div>
        </div>
      </div>
      <!-- ParkSlot state -->
      <div class="subtasks" :style="getStateColor">
        <div class="service">
          <v-icon>{{stateIcon}}</v-icon>
          <div class="details">
            <h4>{{stateText}}</h4>
            <span v-if="state.valueOf() === ParkingSlotState.Reserved">od {{ reservedFrom }} do {{ reservedTo }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="refresh">
      <span>Dáta k: {{ lastUpdate }}</span>
      <v-btn @click="refresh" color="info">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </div>

    <v-btn color="primary" class="rounded-pill btn-book" @click="doReserve" :disabled="state.valueOf() === ParkingSlotState.Reserved || disableReserveBtn">
      <v-icon left>mdi-calendar-check</v-icon>Rezervovať
    </v-btn>
    <reservation-dialog v-model="showReservationDialog"/>
  </div>
</template>

<script>
import {ParkingSlotState} from "~/static/js/ParkingSlotState";
import {ParkingSlotWarning} from "~/static/js/ParkingSlotWarning";
import {randomNumber} from "~/static/js/utils";
import axios from "axios";

function dateBetween(from,to,check) {
  return (check <= to && check >= from);
}

export default {
  name: 'CarInfo',
  props:{
    car: {
      type: Number,
      required: true
    },
    reservedSlots: {
      type: Map,
      required: true
    }
  },
  computed:{
    isFreezing(){
      return this.warningType.valueOf() === ParkingSlotWarning.PossibleFreezing;
    },
    getStateColor(){
      switch (this.state) {
        case ParkingSlotState.Free.valueOf():
          return {color: '#4caf50'};
        case ParkingSlotState.Reserved.valueOf():
          return {color: '#fcaa32'};
        case ParkingSlotState.Occupied.valueOf():
          return {color: '#d5555d'};
        default:
          return {color: 'inherit'};
      }
    },
  },
  methods: {
    refresh() {
      this.updateInfo();
    },
    doReserve() {
      this.showReservationDialog = true;
    },
    afterReservation() {
      this.disableReserveBtn = true;
    },
    updateInfo() {
      if (this.carId === -1)
        return

      this.currentTemperature = '-- ';
      this.currentHumidity = '-- ';

      this.lastUpdate = new Date().toLocaleString();
      this.isAccessible = this.carId === 2;

      axios.get('http://localhost:3000/api/parkslot/' + this.carId)
        .then(response => {
          let cData = response.data;
          let reservedSlot = this.reservedSlots.get(this.carId);

          if (cData?.distance === 1){
            this.state = ParkingSlotState.Occupied;
          } else if (reservedSlot && dateBetween(reservedSlot.from, reservedSlot.to, new Date())){
            this.state = ParkingSlotState.Reserved;
          } else {
            this.state = ParkingSlotState.Free;
          }
        })

      axios.get('http://localhost:3000/api/temperature/' + this.carId)
        .then(response => {
          let tData = response.data;
          if (tData?.temperature !== undefined)
            this.currentTemperature = Math.round(tData.temperature);
          axios.get('http://localhost:3000/api/humidity/' + this.carId)
            .then(response1 => {
              let hData = response1.data;
              if (hData?.humidity !== undefined)
                this.currentHumidity = Math.round(hData.humidity);
              if (hData?.humidity > 70 && tData?.temperature < 0) {
                this.warningType = ParkingSlotWarning.PossibleFreezing;
              }
              else if (hData.humidity < 30 && tData?.temperature > 35) {
                this.warningType = ParkingSlotWarning.Overheating;
              }
              else {
                this.warningType = ParkingSlotWarning.None;
              }
            })
        })
    },
  },
  data() {
    return {
      carId: -1,
      currentTemperature: '-- ',
      currentHumidity: '-- ',
      isAccessible: false,
      state: ParkingSlotState.Free,
      stateIcon: 'mdi-parking',
      stateText: 'Voľné',
      warningType: ParkingSlotWarning.None,
      lastUpdate: new Date().toLocaleString(),
      ParkingSlotWarning, ParkingSlotState,
      showReservationDialog: false,
      reservedFrom: '',
      reservedTo: '',
      disableReserveBtn: false
    };
  },
  mounted() {
    this.$root.$on('reserve', this.afterReservation);
    this.updateInfo();
    setInterval(this.updateInfo, 30000);
  },
  watch: {
    car: function (val) {
      this.carId = val;
      this.updateInfo()
    },
    state: function (val) {
      switch (val.valueOf()) {
        case ParkingSlotState.Free:
          this.stateIcon = 'mdi-parking';
          this.stateText = 'Voľné';
          break;
        case ParkingSlotState.Reserved:
          this.stateIcon = 'mdi-calendar-check';
          this.stateText = 'Rezervované';
          let reservedSlot = this.reservedSlots.get(this.carId);
          this.reservedFrom = reservedSlot?.from;
          this.reservedTo = reservedSlot?.to;
          break;
        case ParkingSlotState.Occupied:
          this.stateIcon = 'mdi-car';
          this.stateText = 'Obsadené';
          break;
      }
    }
  }
}
</script>

<!--suppress CssUnusedSymbol -->
<style>
  .refresh {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1em;
  }

  .recent-subtasks {
    margin-top: 2rem;
  }

  .recent-subtasks span {
    width: 2.2rem;
  }

  .recent-subtasks .carinfo-header {
    display: flex;
    justify-content: space-around;
    margin-bottom: 1rem;
    align-items: center;
    gap: 0.5em;
  }

  .recent-subtasks .header h2 {
    margin-left: 1.5rem;
  }

  .recent-subtasks .header h3 {
    margin-right: 1.5rem;
    display: flex;
    align-items: center;
  }

  .recent-subtasks .subtasks {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 1.4rem;
    border-radius: 1.6rem;
  }

  .recent-subtasks .subtasks .service {
    display: flex;
    gap: 1rem;
  }

  .recent-subtasks .subtasks .service {
    padding: 8px;
    border-radius: 1rem;
    display: flex;
    align-items: center;
  }

  .recent-subtasks .subtask-details {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .recent-subtasks .subtask-details .card {
    display: flex;
    width: 4rem;
    height: 2.2rem;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
  }

  /*noinspection CssUnusedSymbol*/
  button.btn-book {
    display: flex;
    width: 15rem;
    height: 2rem;
    margin-top: 20%;
    margin-bottom: 1rem;
    margin-left: 5rem;
    justify-content: center;
    align-items: center;
    /*padding: 1.5rem var(--card-padding);*/
  }

  #alert-freezing {
    display: flex;
    color: #1477da;
    animation: blinker 1s linear infinite;
  }

  #alert-overheating {
    display: flex;
    color: #d5555d;
    animation: blinker 1s linear infinite;
  }

  @keyframes blinker {
    50%{
      opacity: 0;
    }
  }
</style>
