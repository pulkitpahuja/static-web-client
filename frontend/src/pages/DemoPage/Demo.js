import React, { useEffect } from "react";
import PropTypes from "prop-types";

const Demo = (props) => {
  useEffect(() => {
    var targetContainer = document.getElementById("target_div");
    var eventSource = new EventSource("http://127.0.0.1:5000/stream");
    eventSource.onmessage = function (e) {
      console.log(e);
      targetContainer.innerHTML = e.data;
    };
  }, []);

  return <div id="target_div">Demo</div>;
};

Demo.propTypes = {};

export default Demo;
