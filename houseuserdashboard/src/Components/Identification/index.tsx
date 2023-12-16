import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../Stores/reducers";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const Identification = () => {
  const { t } = useTranslation();

  async function SaveIdentificationSettings() {
    // await SetDS({ key: 'group_number', value: Values.data.group_number })
    // toast.success(t('save-successful'))
  }

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("identification")}</h5>
            <div className="row mb-3">
              <div className="col-12 col-sm-6">
                <label>{t("group-number")}</label>
                <input
                  name="group_number"
                  // value={Values.data.group_number}
                  // onChange={(e) => SetStoreValue(e)}
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
                onClick={() => SaveIdentificationSettings()}
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

export default Identification;
