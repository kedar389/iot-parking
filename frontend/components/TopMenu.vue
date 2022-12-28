<template>
  <v-app-bar app color="primary" class="white--text" dark>
    <v-toolbar-title>{{title}}</v-toolbar-title>
    <v-spacer/>
<!--    <v-btn icon>-->
<!--      <v-icon>mdi-play</v-icon>-->
<!--    </v-btn>-->
  </v-app-bar>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  name: "TopMenu",
  props:{
    title: {
      type: String,
      required: true
    }
  },
  methods: {
  },
  data(){

    return {

    }
  },
  mounted() {
  }
})
</script>
