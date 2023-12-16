import { useState } from "react";
import "./loader.css";
import { useTranslation } from "react-i18next";
import DCCircle from "../../Components/ChargingCircles/DC";
import ACCircle from "../../Components/ChargingCircles/AC";
import NoChargingCircle from "../../Components/ChargingCircles/NoCharging";
import { getTimeDifference } from "../../Utils/getTimeDifference";

const Charging = () => {
  const { t } = useTranslation();
  const [isCharging, setIsCharging] = useState(false);
  const [chargeType, setChargeType] = useState<"AC" | "DC">("AC");
  const [SelectedSocket, setSelectedSocket] = useState<any>({
    lastMeterValue: {
      current: 0,
    },
    statusNotification: {
      sessionStartDate: "",
    },
  });

  return (
    <>
      <div className="container-fluid">
        <div
          id="ccMain"
          className="d-flex align-items-center justify-content-center"
          style={{ marginTop: "12vh", height: "300px" }}
        >
          {!isCharging ? (
            <NoChargingCircle />
          ) : chargeType === "DC" ? (
            <DCCircle />
          ) : (
            <ACCircle />
          )}
        </div>
        <div className="row mt-4">
          <div className="col-12">
            <div className="card shadow-lg">
              <div className="px-5 z-index-1 bg-cover">
                <div className="row d-flex justify-content-between mt-3">
                  <div className="col-lg-3 col-12 my-auto">
                    <h4 className="text-body opacity-9 text-center">
                      {t("charge-details")}
                    </h4>
                    <hr className="horizontal light mt-1 mb-3" />
                    <div
                      id="mobile-column"
                      className="d-flex justify-content-center"
                      style={{ gap: "20px" }}
                    >
                      <div className="text-center">
                        <h6 className="mb-0 text-body opacity-7 text-center">
                          {t("start-date")}
                        </h6>
                        <h3
                          className="text-body"
                          style={{ fontSize: "20px", textAlign: "center" }}
                        >
                          {/* {StartDate} */}
                        </h3>
                      </div>
                      <div className="text-center">
                        <h6 className="mb-0 text-body opacity-7">
                          {t("current")}
                        </h6>
                        <h3 className="text-body">
                          {!SelectedSocket?.lastMeterValue?.current
                            ? "0"
                            : `${(
                                Number(SelectedSocket?.lastMeterValue.current) /
                                1000
                              ).toFixed(0)}`}{" "}
                          <small className="text-sm align-top">A</small>
                        </h3>
                      </div>
                    </div>
                  </div>
                  <div className="col-lg-3 col-12 my-auto">
                    <div
                      className="card d-flex justify-content-center cursor-pointer"
                      style={{
                        width: "100%",
                        height: "50px",
                        fontSize: "20px",
                        textAlign: "center",
                        color: "white",
                        background: isCharging ? "#CF182C" : "#39A56F",
                      }}
                      onClick={() => {
                        // isCharging ? StopCharge() : StartCharge();
                      }}
                    >
                      {isCharging ? t("stop") : t("start")}
                    </div>
                  </div>
                  <div className="col-lg-3 col-12 my-auto text-center">
                    <h4 className="text-body opacity-9">{t("time")}</h4>
                    <div className="d-flex justify-content-center aling-items-center">
                      <div className="text-body" style={{ fontSize: "23px" }}>
                        {isCharging ? (
                          <h3 className="text-body">
                            {SelectedSocket?.statusNotification
                              .sessionStartDate &&
                              getTimeDifference(
                                SelectedSocket?.statusNotification
                                  .sessionStartDate
                              )}
                          </h3>
                        ) : (
                          "-"
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="row mt-4 text-center">
              <p className="text-sm">**{t("how-to-charge")}</p>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        @media (max-width: 1200px) {
          #mobile-column {
            flex-direction: column !important;
          }

          #ccMain {
            margin-top: 100px !important;
          }

          #chargingCicle {
            height: 250px !important;
            width: 250px !important;
          }
        }`}</style>
    </>
  );
};

export default Charging;
