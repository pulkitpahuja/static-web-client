import React, { useEffect, useState } from "react";
import DeviceCard from "../../components/DeviceCard/DeviceCard";
import {
  EuiPage,
  EuiEmptyPrompt,
  EuiLoadingLogo,
  EuiPageBody,
  EuiPageHeader,
  EuiTitle,
  EuiButton,
  EuiFlexGrid,
} from "@elastic/eui";
import { CONNECTED_LINK, DATA_LINK } from "../../Constants";
import axios from "axios";
const MainPage = () => {
  const [meterData, setMeterData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(false);
  const [started, setStarted] = useState(false);
  const [eventSource, setEventSource] = useState(null);
  const [status, setStatus] = useState("Stopped");

  useEffect(() => {
    setIsLoading(true);
    axios
      .get(CONNECTED_LINK)
      .then(function (response) {
        // handle success
        const d = response.data;
        if (d) {
        } else {
          setError(true);
        }
      })
      .catch(function (error) {
        // handle error
        console.log(error);
        setError(true);
      })
      .then(function () {
        // always executed
        setIsLoading(false);
      });
  }, []);

  const loadingPrompt = (
    <EuiEmptyPrompt
      icon={<EuiLoadingLogo logo="logoKibana" size="xl" />}
      title={<h2>Connecting to device...</h2>}
    />
  );
  const errorPrompt = (
    <EuiEmptyPrompt
      iconType="alert"
      color="danger"
      title={<h2>Error loading Dashboards</h2>}
      body={
        <p>
          There was an error connecting to the device. Please connect the USB
          cable and try again.
        </p>
      }
    />
  );

  const startStrean = () => {
    const eSource = new EventSource(DATA_LINK);
    setIsLoading(true);
    eSource.onmessage = function (e) {
      const data = JSON.parse(e.data);
      setStatus("Running");
      setMeterData(data);
      setIsLoading(false);
    };
    setStarted(true);
    setEventSource(eSource);
  };

  const stopStream = (type) => {
    eventSource.close();
    console.log(eventSource.readyState);
    if (type === "stop") {
      setStatus("Stopped");
      setStarted(false);
    } else {
      setStatus("Paused");
    }
  };
  return (
    <EuiPage paddingSize="l">
      <EuiPageBody>
        <EuiPageHeader
          iconType="logoElastic"
          pageTitle={status}
          rightSideItems={[
            <EuiButton
              onClick={() => {
                stopStream("stop");
              }}
              color="danger"
            >
              Stop
            </EuiButton>,
            <EuiButton onClick={stopStream} color="accent">
              Pause
            </EuiButton>,
            <EuiButton onClick={startStrean} color="success">
              Start
            </EuiButton>,
          ]}
          paddingSize="l"
        />
        {!started ? (
          <EuiTitle style={{ textAlign: "center" }} size="l">
            <h1>
              Please press the start button to start the communication. <br />{" "}
              Please wait for 20 seconds before starting
            </h1>
          </EuiTitle>
        ) : isLoading ? (
          loadingPrompt
        ) : error ? (
          errorPrompt
        ) : (
          <EuiFlexGrid columns={2}>
            {Object.keys(meterData).map((dataPoint, idx) => (
              <DeviceCard
                deviceName={dataPoint}
                deviceData={meterData[dataPoint]}
                key={idx}
              />
            ))}
          </EuiFlexGrid>
        )}
      </EuiPageBody>
    </EuiPage>
  );
};

MainPage.propTypes = {};

export default MainPage;
