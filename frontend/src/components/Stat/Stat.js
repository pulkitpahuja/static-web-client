import React from "react";
import { EuiStat, EuiIcon } from "@elastic/eui";

const Stat = (props) => {
  const { variableName, variableVal } = props;
  return (
    <EuiStat
      titleColor="success"
      title={variableVal || "--"}
      description={variableName || "--"}
      textAlign="center"
      titleSize="xs"
    >
      <EuiIcon type="empty" />
    </EuiStat>
  );
};

export default Stat;
