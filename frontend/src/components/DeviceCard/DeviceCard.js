import React from "react";
import PropTypes from "prop-types";
import DataCard from "../DataCard/DataCard";
import classes from "./DeviceCard.module.css";
import { EuiFlexGrid, EuiFlexItem } from "@elastic/eui";
const DeviceCard = (props) => {
  const { deviceName, deviceData } = props;
  return (
    <EuiFlexItem
      className={classes.root}
      grow={Object.keys(deviceData).length < 5 ? false : 1}
    >
      <p style={{ fontSize: "1.2rem", textAlign: "center" }}>{deviceName}</p>
      <EuiFlexGrid columns={6}>
        {Object.keys(deviceData).map((dataPoint, idx) => (
          <DataCard
            key={Math.random()}
            variableName={dataPoint}
            variableVal={deviceData[dataPoint]}
          />
        ))}
      </EuiFlexGrid>
    </EuiFlexItem>
  );
};

DeviceCard.propTypes = {};

export default DeviceCard;
