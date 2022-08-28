import Vue from 'vue'
import App from './App'
import router from './router'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'

import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';

// import iView from 'iview'
// import 'iview/dist/styles/iview.css'
// import locale from 'iview/dist/locale/zh-CN';

Vue.config.productionTip = false

Vue.use(Buefy)
Vue.use(ElementUI);

// Vue.use(iView, {locale})

new Vue({
  el: '#app',
  router,
  render: h => h(App),
  components: { App },
  template: '<App/>'
})
