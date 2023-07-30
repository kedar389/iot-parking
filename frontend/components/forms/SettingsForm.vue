<!--suppress JSUnresolvedVariable -->
<template>
  <v-dialog v-model="show" max-width="500px">
    <v-card>
      <v-card-title class="text-h5">Nastavenia</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" lazy-validation>
          <v-select v-model="langSelect" :items="languages" :label="'Jazyk'" @change="changeLocale" item-text="name" item-value="code" outlined dense/>
          <v-switch v-model="darkMode" :label="'Tmavý režim'" @change="changeDarkMode" dense/>
        </v-form>
      </v-card-text>
      <v-divider/>
      <v-card-actions>
        <v-spacer/>
        <v-btn color="primary" @click.stop="show=false">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import {defineComponent} from "vue";

export default defineComponent({
  name: "SettingsForm",
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  computed: {
    show: {
      get(){
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      }
    }
  },
  data() {
    return {
      valid: true,
      langSelect: this.$i18n.locale,
      languages: this.$i18n.locales,
      darkMode: this.$vuetify.theme.dark,
    }
  },
  methods: {
    changeLocale() {
      this.$i18n.locale = this.langSelect
      this.$router.replace(this.switchLocalePath(this.$i18n.locale));
    },
    changeDarkMode() {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
      this.$root.$emit('darkModeChanged', this.$vuetify.theme.dark);
      this.$cookies.set('app.darkMode', this.$vuetify.theme.dark);
    },
  }
})
</script>

