import { useTranslation } from "react-i18next";

const GetVersion = () => {
  const { t } = useTranslation();

  return (
    <div className="row">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("get-version")}</h5>
            <div className="row mb-3">
              <div className="col-12">
                <label>{t("version")}</label>
                {/* <input disabled name="version" value={Values.data.get_version} className="form-control" type="text" /> */}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GetVersion;
