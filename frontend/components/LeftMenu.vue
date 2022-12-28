<template>
  <v-list dense>
    <div v-for="item in items">
      <v-list-item :key="item.title" link @click.stop="item.target">
        <v-list-item-icon><v-icon>{{ item.icon }}</v-icon></v-list-item-icon>
        <v-list-item-content><v-list-item-title>{{ item.title }}</v-list-item-title></v-list-item-content>
      </v-list-item>
    </div>
    <settings-form v-model="showSettingsForm"/>
    <about-app-form v-model="showAboutAppForm"/>
  </v-list>
</template>

<script>
import SettingsForm from "../components/forms/SettingsForm.vue";
import AboutAppForm from "../components/forms/AboutAppForm.vue";
import { defineComponent } from "vue";

export default defineComponent({
  name: "LeftMenu",
  methods: {
    openHome(){
      this.$router.push({ path: this.localePath({ path: '/' }) });
    },
    openMap(){
      this.$router.push({ path: this.localePath({ path: 'map/' }) });
    },
    openSettingsForm(){
      this.showSettingsForm = true
    },
    // openReservation(){
    //   this.$router.push({ path: this.localePath({ path: 'reservation/' }) });
    // },
    openAboutAppForm(){
      this.showAboutAppForm = true
    },
  },
  data() {
    let showSettingsForm = false;
    let showAboutAppForm = false;

    return {
      showSettingsForm: showSettingsForm,
      showAboutAppForm: showAboutAppForm,
      items: [
        { title: 'Domov', icon: 'mdi-home-city', target: this.openHome },
        { title: 'Mapa', icon: 'mdi-table', target: this.openMap },
        { title: 'Nastavenia', icon: 'mdi-cog', target: this.openSettingsForm},
        { title: 'O aplikácií', icon: 'mdi-information', target: this.openAboutAppForm },
      ]
    }
  },
  components: {
    SettingsForm,
    AboutAppForm
  },
});
</script>

