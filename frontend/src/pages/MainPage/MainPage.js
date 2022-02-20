import React, { useEffect, useState } from "react";
import DataCard from "../../components/DataCard/DataCard";
import {
  EuiPage,
  EuiPageHeader,
  EuiButton,
  EuiEmptyPrompt,
  EuiLoadingLogo,
  EuiPageContentBody,
  EuiPageBody,
  EuiFlexGrid,
} from "@elastic/eui";
import axios from "axios";
const MainPage = (props) => {
  const [meterData, setMeterData] = useState({
    V1: "--",
    V2: "--",
    V3: "--",
    V4: "--",
    V5: "--",
    V6: "--",
    V7: "--",
    V8: "--",
    V9: "--",
    V10: "--",
    A1: "--",
    A2: "--",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    axios
      .get("/connected")
      .then(function (response) {
        // handle success
        const data = response.data;
        if (data === "true") {
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
  return (
    <EuiPage paddingSize="l">
      <EuiPageBody>
        <EuiPageHeader
          iconType="logoElastic"
          pageTitle="Meter Dashboard"
          rightSideItems={[<EuiButton>Print</EuiButton>]}
          bottomBorder
        />
        <EuiPageContentBody>
          {isLoading ? (
            loadingPrompt
          ) : error ? (
            errorPrompt
          ) : (
            <EuiFlexGrid columns={4}>
              {Object.keys(meterData).map((dataPoint, idx) => (
                <DataCard
                  variableName={dataPoint}
                  variableVal={meterData[dataPoint]}
                  key={idx}
                />
              ))}
            </EuiFlexGrid>
          )}
        </EuiPageContentBody>
      </EuiPageBody>
    </EuiPage>
  );
};

MainPage.propTypes = {};

export default MainPage;
