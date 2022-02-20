import React from "react";
import PropTypes from "prop-types";
import { EuiSpacer, EuiFlexItem, EuiPanel } from "@elastic/eui";

import Stat from "../Stat/Stat";
import Graph from "../Graph/Graph";
const DataCard = (props) => {
  const { variableName, variableVal } = props;
  return (
    <EuiFlexItem style={{ width: "80px" }}>
      <EuiPanel>
        <Stat variableName={variableName} variableVal={variableVal} />
      </EuiPanel>
    </EuiFlexItem>
  );
};

DataCard.propTypes = {};

export default DataCard;
