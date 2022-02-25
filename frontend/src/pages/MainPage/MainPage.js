import React, { useEffect, useState } from "react";
import DeviceCard from "../../components/DeviceCard/DeviceCard";
import {
  EuiPage,
  EuiEmptyPrompt,
  EuiLoadingLogo,
  EuiPageBody,
  EuiFlexGrid,
} from "@elastic/eui";
import { CONNECTED_LINK, DATA_LINK } from "../../Constants";
import axios from "axios";
const MainPage = () => {
  const [meterData, setMeterData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    axios
      .get(CONNECTED_LINK)
      .then(function (response) {
        // handle success
        const data = response.data;
        if (data) {
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

  useEffect(() => {
    let timer;
    console.log(error, isLoading);
    if (!error && !isLoading) {
      timer = setInterval(() => {
        axios
          .get(DATA_LINK)
          .then(function (response) {
            // handle success
            const data = response.data;
            setMeterData(data);
          })
          .catch(function (error) {
            // handle error
            console.log(error);
          })
          .then(function () {
            // always executed
          });
      }, 2500);
    }

    return () => clearInterval(timer);
  }, [isLoading, error]);

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
  return (
    <EuiPage paddingSize="l">
      <EuiPageBody>
        {isLoading ? (
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
