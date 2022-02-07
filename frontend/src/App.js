import React from "react";
import MainPage from "./pages/MainPage/MainPage";
import { EuiProvider } from "@elastic/eui";
import "@elastic/eui/dist/eui_theme_light.css";
import "@elastic/charts/dist/theme_only_light.css";

function App() {
  return (
    <EuiProvider colorMode="light">
      <div className="App">
        <MainPage />
      </div>
    </EuiProvider>
  );
}

export default App;
