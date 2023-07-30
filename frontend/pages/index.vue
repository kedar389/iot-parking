<!--suppress JSUnresolvedVariable -->
<template>
  <div class="content">
    <v-row>
      <v-col class="col-12">
        <div class="header">
          <v-card v-show="!loadingIotServer">
            <v-card-title class="text-h5">Voľné parkovacie miesta</v-card-title>
            <v-card-subtitle style="padding-top: 0.5em">
              <v-progress-linear
                :value="freeParkingSpotsPercentage"
                height="10"
                color="primary"
              />
            </v-card-subtitle>
            <v-card-text class="text-h4 text-center">
              {{freeParkingSpotsCount}}/{{allParkingSpotsCount}}
            </v-card-text>
          </v-card>
          <v-skeleton-loader class="" type="card" v-show="loadingIotServer" max-height="140" min-width="400"/>
          <v-card v-show="!loadingIotServer">
            <v-card-title class="text-h5">Voľné parkovacie miesta pre invalidov</v-card-title>
            <v-card-subtitle style="padding-top: 0.5em">
              <v-progress-linear
                :value="freeParkingSpotsInvalidPercentage"
                height="10"
                color="primary"
              />
            </v-card-subtitle>
            <v-card-text class="text-h4 text-center">
              {{freeParkingSpotsInvalidCount}}/{{allParkingSpotsInvalidCount}}
            </v-card-text>
          </v-card>
          <v-skeleton-loader class="" type="card" v-show="loadingIotServer" max-height="140" min-width="400"/>
          <v-card>
            <v-card-title class="text-h5">Aktuálna teplota</v-card-title>
            <v-card-text class="text-h5">
              {{currentTemperature}}°C
            </v-card-text>
          </v-card>
          <v-card>
            <v-card-title class="text-h5">Aktuálna vlhkosť</v-card-title>
            <v-card-text class="text-h5">
              {{currentHumidity}}%
            </v-card-text>
          </v-card>
          <v-card>
            <v-card-title class="text-h5">Počasie</v-card-title>
            <v-card-subtitle>{{currentWeatherDescription}}</v-card-subtitle>
            <v-card-text class="text-h5 text-center">
              <v-icon x-large>{{currentWeatherIcon}}</v-icon>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="col-sm-12 col-md-8">
        <v-card>
          <v-card-title class="text-h5">
            <span style="align-self: flex-start">Obľúbené časy</span>
            <span style="max-width: 10em; margin-left: 1em">
              <v-select
                v-model="selectedDay"
                :items="days"
                item-text="name"
                item-value="id"
                label="Vyberte deň"
                dense outlined
                @change="onSelectedDayChange"/>
            </span>
          </v-card-title>
          <v-card-subtitle>
            <span><v-icon style="padding-right: 0.3em">mdi-clock-time-eight-outline</v-icon>{{'Najrušnejšie: okolo ' + getAttendance.mostBusiestHour + ':00'}}</span>
          </v-card-subtitle>
          <v-card-text>
            <v-sparkline :labels="getLabels" :value="getAttendance.attendance" line-width="2" color="secondary"/>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col class="col-sm-12 col-md-4">
        <v-card color="info" dark style="height: 100%">
          <v-card-title class="text-h5">Oznamy</v-card-title>
          <v-card-text>
            <v-list color="info">
              <v-list-item v-for="item in infoTable" :key="item.id">
                <v-list-item-content>
                  <v-list-item-title>{{item.title}}</v-list-item-title>
                  <v-list-item-subtitle>{{item.subtitle}}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from 'axios';

export let weatherIcons = {
  "01d": "mdi-weather-sunny",
  "01n": "mdi-weather-night",
  "02d": "mdi-weather-partly-cloudy",
  "02n": "mdi-weather-partly-cloudy",
  "03d": "mdi-weather-cloudy",
  "03n": "mdi-weather-cloudy",
  "04d": "mdi-weather-cloudy",
  "04n": "mdi-weather-cloudy",
  "09d": "mdi-weather-pouring",
  "09n": "mdi-weather-pouring",
  "10d": "mdi-weather-rainy",
  "10n": "mdi-weather-rainy",
  "11d": "mdi-weather-lightning",
  "11n": "mdi-weather-lightning",
  "13d": "mdi-weather-snowy",
  "13n": "mdi-weather-snowy",
  "50d": "mdi-weather-fog",
  "50n": "mdi-weather-fog",
};

export let weatherDescriptions = {
  "01d": "Clear sky",
  "01n": "Clear sky",
  "02d": "Few clouds",
  "02n": "Few clouds",
  "03d": "Scattered clouds",
  "03n": "Scattered clouds",
  "04d": "Broken clouds",
  "04n": "Broken clouds",
  "09d": "Shower rain",
  "09n": "Shower rain",
  "10d": "Rain",
  "10n": "Rain",
  "11d": "Thunderstorm",
  "11n": "Thunderstorm",
  "13d": "Snow",
  "13n": "Snow",
  "50d": "Mist",
  "50n": "Mist",
};

export default {
  name: 'IndexPage',
  data() {
    return {
      allParkingSpotsCount: 14,
      freeParkingSpotsCount: 14,
      allParkingSpotsInvalidCount: 2,
      freeParkingSpotsInvalidCount: 2,
      currentTemperature: null,
      currentHumidity: null,
      currentWeatherIcon: null,
      currentWeatherDescription: null,
      loadingOpenWeather: true,
      errorOpenWeather: false,
      loadingIotServer: false,
      errorIotServer: false,
      days: [
        {id: 1, name: "Pondelok"},
        {id: 2, name: "Utorok"},
        {id: 3, name: "Streda"},
        {id: 4, name: "Štvrtok"},
        {id: 5, name: "Piatok"},
        {id: 6, name: "Sobota"},
        {id: 0, name: "Nedeľa"},
    ],
      selectedDay: new Date().getDay(),
      attendance: null,
      infoTable: null
    };
  },
  mounted() {
    this.freeParkingSpotsInvalidCount = 2;
    this.freeParkingSpotsCount = 14;

    axios
      .get('https://api.openweathermap.org/data/2.5/weather?units=metric&q=kosice,sk&appid=2b7d61cfafe37bd68540092f20ba864a')
      .then(response => {
        this.currentTemperature = Math.round(response.data.main["temp"]);
        this.currentHumidity = response.data.main["humidity"];
        this.currentWeatherIcon = weatherIcons[response.data["weather"][0].icon];
        this.currentWeatherDescription = weatherDescriptions[response.data["weather"][0].icon];
      })
      .catch(error => {
        console.log(error)
        this.errorOpenWeather = true
      })
      .finally(() => this.loadingOpenWeather = false)

    axios
      .get('http://localhost:3000/api/parkslots')
      .then(response => {
        let parkslotsRaw = response.data;
        let parkslots = new Map();
        let attendanceByDay = new Map();
        parkslotsRaw.forEach(parkslot => {
          if (parkslot.distance === 1){
            if (parkslots.has(parkslot.IoTHub.ConnectionDeviceId)){
              parkslots.get(parkslot.IoTHub.ConnectionDeviceId).push(parkslot);
            } else {
              parkslots.set(parkslot.IoTHub.ConnectionDeviceId, [parkslot]);
            }

            let date = new Date(parkslot.EventProcessedUtcTime);
            let day = date.getDay();
            let hour = date.getHours();
            if (attendanceByDay.has(day)){
              if (attendanceByDay.get(day).has(hour)){
                attendanceByDay.get(day).set(hour, attendanceByDay.get(day).get(hour) + 1);
              } else {
                attendanceByDay.get(day).set(hour, 1);
              }
            } else {
              attendanceByDay.set(day, new Map());
            }
          }
        });

        //pre kazdy slot zistit ci bol poslednu pol hodinu obsadeny
        for (let key of parkslots.keys()) {
          if (key === 'parkslot2'){
            this.freeParkingSpotsInvalidCount--;
          } else {
            this.freeParkingSpotsCount--;
          }
        }

        //Obsadenost parkoviska v case
        this.attendance = {
          0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {},
        }

        attendanceByDay.forEach((map, key) => {
          map.forEach((number, hour) => {
            this.attendance[key][hour] = number;
          })
        })
      })
      .finally(() => this.loadingIotServer = false)

    this.infoTable = {
      0: {
        id: 1,
        title: "Oznam 1",
        subtitle: "Oznam test 1"
      },
      1: {
        id: 2,
        title: "Zmena vývoja",
        subtitle: "Oznam test 2"
      },
    }
  },
  methods: {
    onSelectedDayChange() {
      console.log(this.selectedDay);
    }
  },
  computed:{
    freeParkingSpotsPercentage() {
      return Math.round((this.freeParkingSpotsCount / this.allParkingSpotsCount) * 100);
    },
    freeParkingSpotsInvalidPercentage() {
      return Math.round((this.freeParkingSpotsInvalidCount / this.allParkingSpotsInvalidCount) * 100);
    },
    getAttendance() {
      let attendance = [];
      if (this.attendance == null || this.attendance[this.selectedDay] == null) {
        for (let i = 0; i < 24; i++) {
          attendance.push(0);
        }
      }
      else
        for (let i = 0; i < 24; i++) {
          if (this.attendance[this.selectedDay][i] === undefined)
            attendance.push(0);
          else
            attendance.push(this.attendance[this.selectedDay][i]);
        }
      return {
        attendance: attendance,
        mostBusiestHour: attendance.indexOf(Math.max(...attendance))
      }
    },
    getLabels() {
      let labels = [];
      for (let i = 0; i < 24; i++) {
        labels.push(i % 2 === 1 ? '   ' : i + "h");
      }
      return labels;
    }
  }
}
</script>

<style scoped>

.header {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 1em;
  flex-wrap: wrap;
}

.content{
  padding: 1.5em;
}
</style>
