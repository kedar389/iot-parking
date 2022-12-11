<!--suppress CssUnusedSymbol -->
<template>
  <v-app>
    <v-navigation-drawer app v-model="drawer" :mini-variant.sync="mini" permanent>
      <v-list-item class="px-2">
        <v-list-item-avatar tile>
          <v-img src="icon.png"></v-img>
        </v-list-item-avatar>

        <v-list-item-title>IOT</v-list-item-title>

        <v-btn icon @click.stop="mini = !mini">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
      </v-list-item>
      <v-divider/>
      <LeftMenu/>
    </v-navigation-drawer>

    <v-main>
      <top-menu :title="title"/>
      <v-container fluid :class="scrollbarTheme">
        <Nuxt/>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import {defineComponent} from 'vue';
import LeftMenu from "../components/LeftMenu.vue";
import TopMenu from "../components/TopMenu.vue";

export default defineComponent({
  components: {LeftMenu, TopMenu},
  data(){
    //TODO - title changing in TopMenu is not working correctly
    let title = "Chyba";
    let pathParts = this.$route.path.split('/');
    if (pathParts.length === 1 || pathParts[1] === ''){
      title = "Domov";
    }
    else {
      let lastPart = pathParts[pathParts.length - 1];
      switch (lastPart) {
        case "map":
          title = "Mapa";
          break;
        case "reservation":
          title = "Rezervácia";
          break;
      }
    }
    return {
      drawer: true,
      mini: false,
      title: title,
    }
  },
  created() {
    const darkModeCookie = this.$cookies.get('app.darkMode');
    if (darkModeCookie) {
      this.$vuetify.theme.dark = darkModeCookie;
    }
  },
  computed: {
    scrollbarTheme() {
      return this.$vuetify.theme.dark ? 'dark' : 'light';
    },
  },
})
</script>

<style>
 /* stylelint-disable */
.container--fluid{
  overflow-x: hidden;
  overflow-y: auto;
  max-height: calc(100vh - 4em);
  width: 100%;
}

.container{
  min-width: 100%;
  height: 100%;
  padding: 6px;
}
</style>
