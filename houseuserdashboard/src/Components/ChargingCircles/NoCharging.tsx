import "./AC.css";

const NoChargingCircle = () => {
  return (
    <div className="pulse">
      <div
        className="pulseTextArea"
        style={{ display: "flex", flexDirection: "column" }}
      >
        <div
          style={{
            marginTop: "25px",
            fontWeight: "bold",
            display: "flex",
            flexDirection: "row",
          }}
        >
          <label
            className=""
            style={{ fontSize: "1.2em", color: "#ec671d", textAlign: "center" }}
          >
            NO CHARGING
          </label>
        </div>
      </div>
    </div>
  );
};

export default NoChargingCircle;
