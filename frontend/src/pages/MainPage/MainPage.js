import React from "react";
import PropTypes from "prop-types";
import classes from "./MainPage.module.css";
import {
  EuiPage,
  EuiPageHeader,
  EuiButton,
  EuiPageContentBody,
  EuiPageBody,
  EuiFlexGrid,
  EuiFlexItem,
  EuiPanel,
} from "@elastic/eui";
const MainPage = (props) => {
  const { colorModeHandler } = props;
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
            <EuiFlexItem>
              <EuiPanel />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiPanel />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiPanel />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiPanel style={{ height: 200 }} />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiPanel />
            </EuiFlexItem>
          </EuiFlexGrid>
        </EuiPageContentBody>
      </EuiPageBody>
    </EuiPage>
  );
};

MainPage.propTypes = {};

export default MainPage;
