import React, { useState } from "react";
import MainPage from "./pages/MainPage/MainPage";
import { EuiProvider } from "@elastic/eui";
import '@elastic/eui/dist/eui_theme_dark.css';

function App() {
  const [isDark, setIsDark] = useState(true);
  const colorModeHandler = () => {
    setIsDark((prev) => !prev);
  };
  return (
    <EuiProvider colorMode={isDark ? "dark" : "light"}>
      <div className="App">
        <MainPage colorModeHandler={colorModeHandler} />
      </div>
    </EuiProvider>
  );
}

export default App;
