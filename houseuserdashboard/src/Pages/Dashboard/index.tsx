import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const Dashboard = () => {
  const { t } = useTranslation();

  return (
    <>
      <div className="container-fluid" style={{ marginTop: "12rem" }}>
        <div className="row mt-4">
          <div className="col-12">
            <div className="card shadow-lg">
              <div className="card-body px-5 z-index-1 bg-cover">
                <div className="row">
                  <div className="col-lg-3 col-12 my-auto"></div>
                  <div className="col-lg-6 col-12 text-center">
                    <img
                      id="car-image"
                      className="w-lg-100 mt-n7 mt-lg-n8 d-none d-md-block"
                      src="../assets/img/hera_car.png"
                      alt="A good car"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* BOXES */}
        <div className="row mt-4">
          <Link
            className="col-lg-3 col-md-6 col-12 mt-4 mt-md-0 p-md-2 p-0"
            to={"/admin/software"}
          >
            <div id="linkCard" className="card bg-primary">
              <div className="card-body p-3">
                <div className="row">
                  <div className="col-9">
                    <div className="numbers">
                      <p className="text-white text-sm mb-0 text-uppercase font-weight-bold opacity-7">
                        {t("device-settings")}
                      </p>
                      <h5 className="text-white font-weight-bolder mb-0">
                        {t("software-settings")}
                      </h5>
                    </div>
                  </div>
                  <div className="col-3 text-end">
                    <div className="icon icon-shape bg-white shadow text-center rounded-circle">
                      <i
                        className="ni fa fa-cogs text-dark text-lg opacity-10"
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Link>

          <Link
            className="col-lg-3 col-md-6 col-12 mt-4 mt-md-0 p-md-2 p-0"
            to={"/admin/status"}
          >
            <div id="linkCard" className="card bg-primary">
              <div className="card-body p-3">
                <div className="row">
                  <div className="col-8">
                    <div className="numbers">
                      <p className="text-white text-sm mb-0 text-uppercase font-weight-bold opacity-7">
                        {t("status")}
                      </p>
                      <h5 className="text-white font-weight-bolder mb-0">
                        {t("device-status")}
                      </h5>
                    </div>
                  </div>
                  <div className="col-4 text-end">
                    <div className="icon icon-shape bg-white shadow text-center rounded-circle">
                      <i
                        className="ni fa fa-cogs text-dark text-lg opacity-10"
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Link>

          <Link
            className="col-lg-3 col-md-6 col-12 mt-4 mt-md-0 p-md-2 p-0"
            to={"/admin/quick-setup"}
          >
            <div id="linkCard" className="card bg-primary">
              <div className="card-body p-3">
                <div className="row">
                  <div className="col-8">
                    <div className="numbers">
                      <p className="text-white text-sm mb-0 text-uppercase font-weight-bold opacity-7">
                        {t("setup")}
                      </p>
                      <h5 className="text-white font-weight-bolder mb-0">
                        {t("quick-setup")}
                      </h5>
                    </div>
                  </div>
                  <div className="col-4 text-end">
                    <div className="icon icon-shape bg-white shadow text-center rounded-circle">
                      <i
                        className="ni fa fa-cogs text-dark text-lg opacity-10"
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Link>

          <Link
            className="col-lg-3 col-md-6 col-12 mt-4 mt-md-0 p-md-2 p-0"
            to={"/admin/profile"}
          >
            <div id="linkCard" className="card bg-primary">
              <div className="card-body p-3">
                <div className="row">
                  <div className="col-8">
                    <div className="numbers">
                      <p className="text-white text-sm mb-0 text-uppercase font-weight-bold opacity-7">
                        {t("users")}
                      </p>
                      <h5 className="text-white font-weight-bolder mb-0">
                        {t("profile")}
                      </h5>
                    </div>
                  </div>
                  <div className="col-4 text-end">
                    <div className="icon icon-shape bg-white shadow text-center rounded-circle">
                      <i
                        className="ni fa fa-cogs text-dark text-lg opacity-10"
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        </div>
      </div>
      <style>{`
        #linkCard:hover {
          background-color: #ca5c1f !important;
        }

        @media (max-width: 1200px) {
          #mobile-column {
            flex-direction: column !important;
          }
        }
        
        @media (max-width: 1000px) {
          #car-image {
              display: none !important;
          }
        }
        `}</style>
    </>
  );
};

export default Dashboard;
