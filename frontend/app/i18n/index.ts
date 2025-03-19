import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';


import en from './en.json';
import es from './es.json';

import type { Resource } from 'i18next';


// Create a type for our translations that matches i18next's Resource type
interface Resources extends Resource {
  en: {
    translation: {
      [key: string]: string | { [key: string]: string };
    };
  };
  es: {
    translation: {
      [key: string]: string | { [key: string]: string };
    };
  };
}

const resources: Resources = {
  en: {
    translation: en
  },
  es: {
    translation: es
  }
};

i18next
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    compatibilityJSON: 'v4'
  });

export default i18next; 