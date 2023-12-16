import { useTranslation } from "react-i18next";

const ChargePointId = () => {
  const { t } = useTranslation();

  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <div className="row mb-3">
              <div className="col-12 col-sm-12">
                <label>{t("charge-point-id")}</label>
                <input
                  disabled
                  name="charge_point_id"
                  // value={Values.data.charge_point_id}
                  className="form-control"
                  type="text"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChargePointId;
