import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import classes from "./MainPage.module.css";
import DataCard from "../../components/DataCard/DataCard";
import {
  EuiPage,
  EuiPageHeader,
  EuiButton,
  EuiPageContentBody,
  EuiPageBody,
  EuiFlexGrid,
} from "@elastic/eui";
const MainPage = (props) => {
  const { colorModeHandler } = props;
  const [meterData, setMeterData] = useState({
    1: 1,
    2: 2,
    3: 3,
    4: 4,
  });
  return (
    <EuiPage paddingSize="l">
      <EuiPageBody>
        <EuiPageHeader
          iconType="logoElastic"
          pageTitle="Page title"
          rightSideItems={[<></>, <EuiButton>Do something</EuiButton>]}
          bottomBorder
        />
        <EuiPageContentBody>
          <EuiFlexGrid columns={4}>
            {Object.keys(meterData).map((dataPoint, idx) => (
              <DataCard
                variableName={dataPoint}
                variableVal={meterData[dataPoint]}
                key={idx}
              />
            ))}
          </EuiFlexGrid>
        </EuiPageContentBody>
      </EuiPageBody>
    </EuiPage>
  );
};

MainPage.propTypes = {};

export default MainPage;
