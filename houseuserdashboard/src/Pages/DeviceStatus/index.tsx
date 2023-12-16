import { useTranslation } from "react-i18next";

const DeviceStatus = () => {
  const { t } = useTranslation();

  return (
    <>
      <div
        className="card shadow-lg mx-4 card-profile-bottom"
        style={{ marginTop: "12rem" }}
      >
        <div className="card-body p-3">
          <div className="row gx-4">
            <div className="col-auto">
              <div className="avatar avatar-xl position-relative">
                <img src="../assets/img/charging_status.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t("device-status")}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        <div className="row mb-3">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <h5 className="font-weight-bolder mb-4">
                  {t("network-state")}
                </h5>
                <div className="row g-3">
                  <div className="col-12 col-sm-6 col-md-4">
                    <div className="card">
                      <div className="card-body">
                        <h5 className="font-weight-bolder">
                          {t("link-status")}
                        </h5>
                        <div className="row">
                          <div className="col-12 col-sm-6">
                            <p
                            // style={{
                            //   color: `${
                            //     Values.data.link_status === "1"
                            //       ? "green"
                            //       : "red"
                            //   }`,
                            // }}
                            >
                              {/* {Values.data.link_status === "1"
                                ? "Online"
                                : "Offline"} */}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-12 col-sm-6 col-md-4">
                    <div className="card">
                      <div className="card-body">
                        <h5 className="font-weight-bolder">
                          {t("strength-of-4g")}
                        </h5>
                        <div className="row">
                          <div className="col-12 col-sm-6">
                            {/* <p>{Values.data.four_g_signal}</p> */}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-12 col-sm-6 col-md-4">
                    <div className="card">
                      <div className="card-body">
                        <h5 className="font-weight-bolder">
                          {t("network-card")}
                        </h5>
                        <div className="row">
                          <div className="col-12 col-sm-6">
                            {/* <p>{Values.data.network_card}</p> */}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="row mb-3">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <h5 className="font-weight-bolder mb-4">
                  {t("state-of-ocpp")}
                </h5>
                <div className="row">
                  <div className="col-12 col-sm-6 col-md-4">
                    <div className="card">
                      <div className="card-body">
                        <h5 className="font-weight-bolder">
                          {t("background-connection")}
                        </h5>
                        <div className="row">
                          <div className="col-12 col-sm-6">
                            <p
                            // style={{
                            //   color: `${
                            //     Values.data.ocpp_state === "1"
                            //       ? "green"
                            //       : "red"
                            //   }`,
                            // }}
                            >
                              {/* {Values.data.ocpp_state === "1"
                                ? "Online"
                                : "Offline"} */}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DeviceStatus;
