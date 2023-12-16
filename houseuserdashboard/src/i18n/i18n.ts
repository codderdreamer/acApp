import i18next from 'i18next'
import { initReactI18next } from 'react-i18next'
import EN from './locales/en.json'
import TR from './locales/tr.json'

const resources = {
  en: {
    translation: EN
  },
  tr: {
    translation: TR
  }
}

i18next.use(initReactI18next).init({
  resources,
  fallbackLng: 'en',
  lng: localStorage.getItem('lang') || 'en',
  interpolation: { escapeValue: false }
})

export default i18next
