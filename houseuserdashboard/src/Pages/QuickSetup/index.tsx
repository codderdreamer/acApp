import OCPPSettings from "../../Components/OCPPSettings";
import FourGSettings from "../../Components/FourGSettings";
import ChargePointId from "../../Components/ChargePointId";
import GetVersion from "../../Components/GetVersion";
import { useTranslation } from "react-i18next";

const QuickSetup = () => {
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
                <img src="../assets/img/quick_setup.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t("quick-setup")}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        {/* charge point id */}
        <ChargePointId />
        {/* ocpp settings */}
        <OCPPSettings />
        {/* 4g config */}
        {/* <FourGSettings /> */}
        {/* get version */}
        <GetVersion />
      </div>
    </>
  );
};

export default QuickSetup;
