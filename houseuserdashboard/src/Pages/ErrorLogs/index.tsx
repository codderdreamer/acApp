import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

const Reports = () => {
  const [Logs, setLogs] = useState<any>({ logs: [], errors: [] });
  const { t } = useTranslation();

  useEffect(() => {}, []);

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
                <img src="../assets/img/analytics.png" />
              </div>
            </div>
            <div className="col-auto my-auto">
              <div className="h-100">
                <h5 className="mb-1">{t("errors")}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container-fluid py-4">
        <div className="col-12">
          <div className="card" style={{ marginTop: "10px" }}>
            <div className="card-body">
              <h5 className="card-title">{t("errors")}</h5>
              <div className="col-12">
                <div className="row">
                  {/* Ornek Error */}
                  <div id="data-col" className="col-6" key={"12.12.12"}>
                    <div className="card p-4">
                      <div className="body">
                        <h5 className="card-title">
                          {t("date")} :<span> {"12.12.12"}</span>
                        </h5>
                        <h5 className="card-title">
                          {t("description")} :<span> {"Hata mesaji 1"}</span>
                        </h5>
                      </div>
                    </div>
                  </div>
                  {/* Ornek Error */}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        @media (max-width: 1200px) {
          #data-col {
            width: 100% !important;
            margin-bottom: 20px !important;
          }
        }`}</style>
    </>
  );
};

export default Reports;
