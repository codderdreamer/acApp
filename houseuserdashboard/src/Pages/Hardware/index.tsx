import ChargePointId from "../../Components/ChargePointId";
import GetVersion from "../../Components/GetVersion";
import Identification from "../../Components/Identification";
import { useTranslation } from "react-i18next";

const Hardware = () => {
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
                <img src="../assets/img/hardware_settings.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t("hardware-settings")}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        <ChargePointId />
        {/* Identification */}
        <Identification />
        {/* common settings */}
        {/* <CommonSettings /> */}
        {/* get version */}
        <GetVersion />
      </div>
    </>
  );
};

export default Hardware;
