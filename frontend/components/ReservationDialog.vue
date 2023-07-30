<template>
  <v-dialog v-model="show" max-width="600px">
    <validation-observer ref="observer" v-slot="{ invalid }">
      <v-card>
        <v-card-title>Rezervácia miesta</v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <validation-provider rules="required" v-slot="{ errors }">
                  <v-text-field v-model="name" label="Meno a priezvisko" type="text" :error-messages="errors"/>
                </validation-provider>
              </v-col>
              <v-col cols="12">
                <validation-provider rules="required|email" v-slot="{ errors }">
                  <v-text-field v-model="email" label="E-mail" type="email" :error-messages="errors"/>
                </validation-provider>
              </v-col>
              <v-col cols="12">
                <validation-provider name="dateFrom" rules="required|fromNow" v-slot="{ errors }">
                  <v-text-field v-model="dateFrom" label="Začiatok rezervácie" type="datetime-local" :error-messages="errors"/>
                </validation-provider>
              </v-col>
              <v-col cols="12">
                <validation-provider rules="required|afterDate:@dateFrom" v-slot="{ errors }">
                  <v-text-field v-model="dateTo" label="Koniec rezervácie" type="datetime-local" :error-messages="errors"/>
                </validation-provider>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="close">Zrušiť</v-btn>
          <v-btn text type="submit" :disabled="invalid" @click="reserve">Rezervovať</v-btn>
        </v-card-actions>
      </v-card>
    </validation-observer>
  </v-dialog>
</template>

<script>
import { required, email } from 'vee-validate/dist/rules';
import { extend, ValidationProvider, ValidationObserver } from 'vee-validate';

extend('required', {
  ...required,
  message: 'Povinné pole'
});

extend('email', {
  ...email,
  message: 'Nesprávny formát e-mailu'
});

extend('fromNow', {
  validate(value) {
    return new Date(value) > new Date();
  },
  message: 'Dátum musí byť v budúcnosti'
});

extend('afterDate', {
  params: ['dateFrom'],
  validate(value, { dateFrom }) {
    return new Date(value) > new Date(dateFrom);
  },
  message: 'Dátum konca rezervácie musí byť po dátume začiatku'
});

export default {
  name: "ReservationDialog",
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  components: {
    ValidationProvider,
    ValidationObserver
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
    let now = new Date();
    let dateFrom = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes());
    let dateTo = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + 1, now.getMinutes());
    return {
      name: "",
      email: "",
      dateFrom: dateFrom.toISOString().substr(0, 16),
      dateTo: dateTo.toISOString().substr(0, 16),
    };
  },
  methods: {
    close() {
      this.show = false;
    },
    reserve() {
      if (!this.$refs.observer?.validate())
        return

      this.show = false;
      this.$root.$emit("reserve", {
        name: this.name,
        email: this.email,
        dateFrom: new Date(this.dateFrom),
        dateTo: new Date(this.dateTo)
      });
    },
  }
}
</script>

<style scoped>

</style>
