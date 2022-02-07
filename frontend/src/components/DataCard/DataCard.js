import React from "react";
import PropTypes from "prop-types";
import { EuiSpacer, EuiFlexItem, EuiPanel } from "@elastic/eui";
import Stat from "../Stat/Stat";
import Graph from "../Graph/Graph";
const DataCard = (props) => {
  const { variableName, variableVal } = props;
  return (
    <EuiFlexItem>
      <EuiPanel>
        <div>
          <Stat />
        </div>
        <EuiSpacer size="s" />
        <div>
          <Graph />
        </div>
      </EuiPanel>
    </EuiFlexItem>
  );
};

DataCard.propTypes = {};

export default DataCard;
