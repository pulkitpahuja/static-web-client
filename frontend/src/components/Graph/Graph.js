import React from "react";
import PropTypes from "prop-types";
import { Chart, Settings, LineSeries } from "@elastic/charts";
import { euiPaletteForLightBackground } from "@elastic/eui";
const Graph = (props) => {
  const { data } = props;
  return (
    <Chart size={{ height: 48 }}>
      <Settings showLegend={false} tooltip="none" />
      <LineSeries
        id="increase"
        data={data || []}
        xAccessor="x"
        yAccessors={["y"]}
        color={[euiPaletteForLightBackground()[1]]}
      />
    </Chart>
  );
};

Graph.propTypes = {};

export default Graph;
