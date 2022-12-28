import colors from 'vuetify/es5/util/colors'
import YAML from 'yaml'
import fs from 'fs'

function loadYaml(path) {
  return YAML.parse(fs.readFileSync(path, 'utf8'))
}

export default {
  FOR DEPLOYMENT
  *server: {
    port: 8080, // default: 3000
    host: '0.0.0.0', // default: localhost,
    timing: false
  },
  mode: 'spa',

  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s',
    title: 'IOTparking',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },
  lintOnSave: false,
  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    './assets/css/styles.css'
  ],
  styleResources: {
    scss: ['./assets/css/*.scss']
  },

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    '@nuxt/typescript-build',
    // https://go.nuxtjs.dev/eslint
    //'@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/stylelint
    //'@nuxtjs/stylelint-module',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/pwa
    '@nuxtjs/pwa',
    '@nuxtjs/i18n',
    'cookie-universal-nuxt'
  ],

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    workbox: {
      enabled: true
    },
    icon: {

    },
    manifest: {
      name: 'XXX',
      short_name: 'XXX',
      description: 'Project description',
      theme_color: '#d5d5d1',
      background_color: '#ffffff',
      display: 'standalone',
      lang: 'sk'
    }
  },

  // I18n module configuration: https://i18n.nuxtjs.org/
  i18n: {
    locales: [
      { code: 'en', name: 'English' },
      { code: 'sk', name: 'Slovenský' }
    ],
    defaultLocale: 'sk',
    parsePages: false,
    vueI18n: {
      fallbackLocale: 'sk',
      messages: {
        en: loadYaml('./locales/en-US.yaml'),
        sk: loadYaml('./locales/sk-SK.yaml')
      }
    }
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ['./assets/css/variables.scss'],
    customProperties: true,
    theme: {
      dark: false,
      themes: {
        light: {
          primary: colors.green.darken1,
          secondary: colors.cyan.base,
          accent: colors.lime.base,
          error: colors.red.base,
          warning: colors.amber.base,
          info: colors.lightBlue.base,
          success: colors.lightGreen.base
        },
        dark: {
          primary: colors.green.darken1,
          secondary: colors.cyan.base,
          accent: colors.lime.base,
          error: colors.red.base,
          warning: colors.amber.base,
          info: colors.lightBlue.base,
          success: colors.lightGreen.base
        }
      },
    },
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    extend (config, { isDev }) {
      config.node = {
        fs: 'empty'
      }
      // Sets webpack's mode to development if `isDev` is true.
      if (isDev) {
        config.mode = 'development'
      }
      config.module.rules.push({
        test: /\.ya?ml$/,
        use: 'yaml-loader'
      });
    }
  },
}
