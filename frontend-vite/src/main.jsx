import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { MantineProvider } from '@mantine/core'
import { NotificationsProvider } from '@mantine/notifications'

ReactDOM.createRoot(document.getElementById('root')).render(
  <MantineProvider withGlobalStyles withNormalizeCSS>
    <NotificationsProvider>
      <App />
    </NotificationsProvider>
  </MantineProvider>
)
