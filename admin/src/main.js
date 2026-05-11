import { createApp } from 'vue'
import App from './App.vue'
import { ConfigProvider, Button, Cell, CellGroup, NavBar, Tab, Tabs, Card, Tag, Dialog, Toast } from 'vant';
import 'vant/lib/index.css';
import './style.css'

const app = createApp(App)
app.use(ConfigProvider)
app.use(Button)
app.use(Cell).use(CellGroup)
app.use(NavBar)
app.use(Tab).use(Tabs)
app.use(Card)
app.use(Tag)
app.use(Dialog)
app.use(Toast)
app.mount('#app')
