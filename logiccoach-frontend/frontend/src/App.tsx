import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AppRoutes } from './router';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { track } from './analytics';
import { EVENTS } from './analytics/events';


function App() {
  useEffect(() => {
    track(EVENTS.MY_CUSTOM_EVENT, { property: 'value' });
  }, []);

  return (
    <I18nextProvider i18n={i18n}>
      <BrowserRouter basename={__BASE_PATH__}>
        <AppRoutes />
      </BrowserRouter>
    </I18nextProvider>
  );
}

export default App;