import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const FunctionsSettings = () => {
  const { t } = useTranslation();

  async function SaveFunctionsSettings() {}

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("functions-enable")}</h5>
            <div className="row">
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("card-type")}</label>
                <select
                  name="card_type"
                  // value={Values.card_type}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                >
                  <option value="1">{t("start-stop-card")}</option>
                  <option value="2">{t("local-pnc")}</option>
                  <option value="3">{t("billing-card")}</option>
                </select>
              </div>
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("local-startup-absolute")}</label>
                <select
                  name="local_startup"
                  // value={Values.local_startup}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                >
                  <option value="0">{t("no")}</option>
                  <option value="1">{t("yes")}</option>
                </select>
              </div>
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("qr-open-absolute")}</label>
                <select
                  name="qr_code_process"
                  // value={Values.qr_code_process}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                >
                  <option value="0">{t("no")}</option>
                  <option value="1">{t("yes")}</option>
                </select>
              </div>
              <div className="col-12 col-sm-6">
                <label className="mt-4">{t("transfer-private-data")}</label>
                <select
                  name="transfer_private_data"
                  // value={Values.transfer_private_data}
                  // onChange={(e) => SetStoreValue(e)}
                  className="form-control"
                >
                  <option value="0">{t("no")}</option>
                  <option value="1">{t("yes")}</option>
                </select>
              </div>
            </div>
            <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0 mt-3">
              <button
                className="btn btn-primary btn-sm mb-0"
                type="button"
                name="button"
                onClick={SaveFunctionsSettings}
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

export default FunctionsSettings;
