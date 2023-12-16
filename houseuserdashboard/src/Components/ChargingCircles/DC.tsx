import { useEffect, useState } from "react";
import "./DC.css";

const GetRangeArray = (start: number, end: number) => {
  return Array(end - start + 1)
    .fill(0)
    .map((_, idx) => start + idx);
};

const GetTwoCharNumber = (num: number) => {
  return num < 10 ? `0${num}` : `${num}`;
};

const DCCircle = () => {
  const [SelectedSocket, setSelectedSocket] = useState({
    lastMeterValue: {
      current: 0,
      percent: 10,
    },
    statusNotification: {
      sessionStartDate: "",
    },
  });

  const [PercentItems, setPercentItems] = useState<Array<number>>(
    GetRangeArray(0, 1)
  );
  const [Percent, setPercent] = useState(0);

  console.log(SelectedSocket?.lastMeterValue);

  useEffect(() => {
    if (!SelectedSocket?.lastMeterValue) {
      setPercentItems([]);
      setPercent(0);
      return;
    }

    let percentNumber = Number(SelectedSocket?.lastMeterValue.percent ?? 0);
    if (!percentNumber || percentNumber <= 0) return;

    setPercent(percentNumber);
    setPercentItems(GetRangeArray(0, percentNumber));
  }, [SelectedSocket]);

  return (
    <div className="chargeCard">
      <div className="chargeRating">
        <h2 style={{ color: "#ec671d" }}>
          <sup>%</sup>
          <span className="chargeCounter" style={{ paddingRight: "20px" }}>
            {GetTwoCharNumber(Percent)}
          </span>
          <br></br>
        </h2>
        {PercentItems.map((item, index) => {
          let style: any = {
            transform: `rotate(${3.6 * index}deg)`,
          };

          if (index < Percent) {
            style.background = "#0f0";
            style.boxShadow = "0 0 15px #0f0, 0 0 30px #0f0";
          }

          if (index === Percent - 1) {
            style.animationName = "blinker";
            style.animationDuration = "0.9s";
            style.animationTimingFunction = "linear";
            style.animationDelay = `${index / 10}s`;
            style.animationIterationCount = "infinite";
          }

          return (
            <div className={`chargeBlock`} style={style} key={index}></div>
          );
        })}
      </div>
    </div>
  );
};

export default DCCircle;
