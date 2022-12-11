<!--suppress JSUnresolvedVariable -->
<template>
  <v-dialog v-model="show" max-width="500px">
    <v-card>
      <v-card-title class="text-h5">Nastavenia</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" lazy-validation>
          <v-select v-model="langSelect" :items="languages" :label="'Jazyk'" @change="changeLocale" item-text="name" item-value="code"></v-select>
          <v-switch v-model="darkMode" :label="'Tmavý režim'" @change="changeDarkMode"></v-switch>
          <v-switch v-model="compactView" :label="'Kompaktný režim zobrazenia pri vizualizácií'" @change="changeCompactView"></v-switch>
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
    value:{
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
      compactView: this.$cookies.get('app.compactView')
    }
  },
  methods: {
    changeLocale() {
      this.$i18n.locale = this.langSelect
      this.$router.replace(this.switchLocalePath(this.$i18n.locale));
    },
    changeDarkMode() {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
      this.$cookies.set('app.darkMode', this.$vuetify.theme.dark);
    },
    changeCompactView() {
      this.compactView = !this.$cookies.get('app.compactView');
      this.$cookies.set('app.compactView', this.compactView);
      this.$root.$emit('compactViewChanged', this.compactView);
    },
  }
})
</script>

