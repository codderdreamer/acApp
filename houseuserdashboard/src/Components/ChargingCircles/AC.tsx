import { useState } from "react";
import "./AC.css";

const ACCircle = () => {
  const [SelectedSocket, setSelectedSocket] = useState<any>({
    lastMeterValue: {
      kWh: 0,
    },
  });

  const GetIdStyle: any = (id: number) => {
    return {
      "--i": `${id}`,
    };
  };

  return (
    <div className="pulse">
      {SelectedSocket?.lastMeterValue ? (
        <>
          <span style={GetIdStyle(0)}></span>
          <span style={GetIdStyle(1)}></span>
          <span style={GetIdStyle(2)}></span>
        </>
      ) : (
        <></>
      )}
      <div
        className="pulseTextArea"
        style={{ display: "flex", flexDirection: "column" }}
      >
        <i
          className="fa fa-bolt"
          style={{ fontSize: "3em", paddingTop: "20px", color: "#ec671d" }}
        />
        <div
          style={{
            marginLeft: "30px",
            fontWeight: "bold",
            display: "flex",
            flexDirection: "row",
          }}
        >
          <label
            className=""
            style={{ fontSize: "3em", lineHeight: "70px", color: "#ec671d" }}
          >
            {SelectedSocket?.lastMeterValue
              ? `${Number(SelectedSocket.lastMeterValue.kWh).toFixed(0)}`
              : "0"}
          </label>
          <sup style={{ fontSize: "1em", marginTop: "20px" }}>kWh</sup>
        </div>
      </div>
    </div>
  );
};

export default ACCircle;
