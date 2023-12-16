import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const BluetoothSettings = () => {
  const { t } = useTranslation();

  async function SaveBluetoothSettings() {
    // await SetDS({ key: "server_enable", value: Values.data.server_enable });
    // await SetDS({ key: "server_name", value: Values.data.server_name });
    // await SetDS({ key: "server_pin", value: Values.data.server_pin });
    toast.success(t("save-successful"));
  }

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("bluetooth")}</h5>
            <div className="row mb-3">
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("bluetooth-enable")}</label>
                <select
                  name="server_enable"
                  // value={Values.data.server_enable}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                >
                  <option value={0}>{t("disable")}</option>
                  <option value={1}>{t("enable")}</option>
                </select>
              </div>
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("bluetooth-name")}</label>
                <input
                  disabled
                  name="server_name"
                  // value={Values.data.server_name}
                  className="form-control"
                  type="text"
                />
              </div>
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("pin")}</label>
                <input
                  disabled
                  name="server_pin"
                  // value={Values.data.server_pin}
                  className="form-control"
                  type="text"
                />
              </div>
            </div>
            <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0">
              <button
                className="btn btn-primary btn-sm mb-0"
                type="button"
                name="button"
                onClick={SaveBluetoothSettings}
              >
                {t("submit")}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BluetoothSettings;
