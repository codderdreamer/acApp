import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const WifiSettings = () => {
  const { t } = useTranslation();

  async function SaveWifiSettings() {}

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("wifi-configuration")}</h5>
            <div className="row">
              <div className="col-12">
                <input
                  name="dhcpd_enable"
                  // checked={Values.data.dhcpd_enable === "1"}
                  // onChange={(e) => SetStoreValue(e, true)}
                  type="checkbox"
                />
                <label htmlFor="wifi-configuration">{t("wifi-enable")}</label>
                <div
                  id="wifi-configuration-form"
                  // className={`${
                  //   Values.data.dhcpd_enable === "1" ? "" : "d-none"
                  // }`}
                >
                  <div className="row mb-3">
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("mode-selection")}</label>
                      <select
                        name="mode_selection"
                        // value={Values.data.mode_selection}
                        // onChange={(e) => SetStoreValue(e)}
                        className="form-control"
                      >
                        <option value="">{t("select")}</option>
                        <option value="STA">STA</option>
                        <option value="AP">AP</option>
                      </select>
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("ssid")}</label>
                      <input
                        name="ssid"
                        // value={Values.data.ssid}
                        // onChange={(e) => SetStoreValue(e)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("password")}</label>
                      <input
                        name="wifi_password"
                        // value={Values.data.wifi_password}
                        // onChange={(e) => SetStoreValue(e)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("encryption")}</label>
                      <select
                        name="encryption"
                        // value={Values.data.encryption}
                        // onChange={(e) => SetStoreValue(e)}
                        className="form-control"
                      >
                        <option value="OPEN">OPEN</option>
                        <option value="WEP">WEP</option>
                        <option value="WPA">WPA</option>
                        <option value="WPA2">WPA2</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0">
                  <button
                    className="btn btn-primary btn-sm mb-0"
                    type="button"
                    name="button"
                    onClick={SaveWifiSettings}
                  >
                    {t("submit")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WifiSettings;
