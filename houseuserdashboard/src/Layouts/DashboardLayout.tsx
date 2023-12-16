import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { RootState } from "../Stores/reducers";
import { INavItemProps } from "./models";
import { AppDispatch } from "../Stores";
import { GetUserThunk } from "../Stores/Reducers/Account/thunks";
import { useTranslation } from "react-i18next";
import "./custom.css";

const DashboardLayout = () => {
  const User = useSelector((state: RootState) => state.user.data);

  const [SideNavType, setSideNavType] = useState<"hidden" | "pinned">("pinned");
  const [SelectedIndex, setSelectedIndex] = useState(0);

  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const AdminNavigateItems = () => [
    {
      title: t("dashboard"),
      icon: "fas fa-home",
      href: "/admin/dashboard",
    },
    {
      title: t("quick-setup"),
      icon: "ni-settings",
      href: "/admin/quick-setup",
    },
    {
      title: t("charge"),
      icon: "fas fa-charging-station",
      href: "/admin/charging",
    },
    {
      title: t("error-logs"),
      icon: "fa fa-line-chart",
      href: "/admin/error-logs",
    },
    {
      title: t("hardware-settings"),
      icon: "ni-atom",
      href: "/admin/hardware",
    },
    {
      title: t("software-settings"),
      icon: "ni-ui-04",
      href: "/admin/software",
    },
    {
      title: t("device-status"),
      icon: "ni-badge",
      href: "/admin/status",
    },
    {
      title: t("upload-and-download"),
      icon: "ni-cloud-download-95",
      href: "/admin/uploads",
    },

    {
      title: t("profile"),
      icon: "fas fa-user",
      href: "/admin/profile",
    },
  ];

  const [NavigateItems, setNavigateItems] =
    useState<Array<INavItemProps>>(AdminNavigateItems);

  const location = useLocation();
  useEffect(() => {
    const path = location.pathname;

    const index = AdminNavigateItems().findIndex((item) => item.href === path);
    setSelectedIndex(index);
  }, [location]);

  const dispatch = useDispatch<AppDispatch>();
  useEffect(() => {
    dispatch(GetUserThunk());
  }, []);

  function Logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("device_auth_token");
    localStorage.removeItem("cpid");
    localStorage.removeItem("email");
    localStorage.removeItem("is_admin");
    navigate("/account/login");
  }

  function ChangeLanguage(lang: string) {
    i18n.changeLanguage(lang);
    localStorage.setItem("lang", lang);
    setNavigateItems(AdminNavigateItems());
  }

  return (
    <div className={`g-sidenav-${SideNavType}`}>
      <div
        className="position-absolute w-100 min-height-300 top-0"
        style={{
          backgroundImage:
            'url("https://raw.githubusercontent.com/creativetimofficial/public-assets/master/argon-dashboard-pro/assets/img/profile-layout-header.jpg")',
          backgroundPositionY: "50%",
        }}
      >
        <span className="mask bg-primary opacity-6" />
      </div>
      <aside
        className="sidenav overflow-hidden sidebar-color-custom navbar navbar-vertical navbar-expand-xs border-0 border-radius-xl my-3 fixed-start ms-4"
        id="sidenav-main"
      >
        <div className="sidenav-header" style={{ background: "white" }}>
          <i
            className="fas fa-times p-3 cursor-pointer text-secondary opacity-5 position-absolute end-0 top-0 d-none d-xl-none"
            aria-hidden="true"
            id="iconSidenav"
          />
          <a
            className="m-0 text-center d-flex align-items-center justify-content-center h-100"
            href="/admin/dashboard"
          >
            <img
              src="/assets/img/logo-ct-dark.png"
              className=""
              alt="main_logo"
              style={{ objectFit: "contain", width: "180px" }}
            />
          </a>
        </div>
        <div className="collapse navbar-collapse w-auto h-auto" id="main-menu">
          <ul className="navbar-nav">
            {NavigateItems.map((item, index) => (
              <li id="navItem" className="nav-item" key={index}>
                <Link
                  to={item.href}
                  id="navItemA"
                  className={`nav-link ${
                    SelectedIndex === index ? "active" : ""
                  }`}
                  aria-controls="dashboardsExamples"
                  role="button"
                  aria-expanded="false"
                  onClick={() => {
                    setSelectedIndex(index);
                  }}
                >
                  <div
                    id="navItemA"
                    className="icon icon-shape icon-sm text-center d-flex align-items-center justify-content-center"
                  >
                    <i
                      id="navItemA"
                      className={`ni nav-link-text text-sm opacity-10 sidebar-icon-color ${item.icon}`}
                    />
                  </div>
                  <span
                    id="navItemA"
                    className="nav-link-text ms-1 sidebar-text-color"
                  >
                    {item.title}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </aside>
      <div className="main-content position-relative border-radius-lg">
        <nav
          className="navbar navbar-main navbar-expand-lg px-0 mx-4 shadow-none border-radius-xl z-index-sticky"
          id="navbarBlur"
          data-scroll="false"
        >
          <div id="navbar" className="container-fluid py-1 px-3">
            <div
              id="navbarToggle"
              className="sidenav-toggler sidenav-toggler-inner"
            >
              <a
                onClick={() =>
                  setSideNavType(SideNavType === "hidden" ? "pinned" : "hidden")
                }
                className="nav-link p-0"
              >
                <div className="sidenav-toggler-inner">
                  <i className="sidenav-toggler-line bg-white" />
                  <i className="sidenav-toggler-line bg-white" />
                  <i className="sidenav-toggler-line bg-white" />
                </div>
              </a>
            </div>
            <div className="mt-sm-0 mt-2 me-md-0 me-sm-4" id="navbar">
              <div className="ms-md-auto pe-md-3 d-flex align-items-center">
                <div className="input-group" />
              </div>
              <ul className="navbar-nav justify-content-end">
                <li
                  className="nav-item d-flex align-items-center"
                  style={{ gap: "30px" }}
                >
                  <div>
                    <select
                      className="form-control text-white"
                      style={{ background: "transparent", border: "none" }}
                      defaultValue={localStorage.getItem("lang") ?? "en"}
                      onChange={(e) => ChangeLanguage(e.target.value)}
                    >
                      <option value="tr">Türkçe</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                  <Link
                    to="/admin/profile"
                    className="nav-link text-white font-weight-bold px-0"
                  >
                    <i className="fa fa-user me-sm-1" />
                    <span className="d-sm-inline d-none">{`${User.firstName} ${User.lastName}`}</span>
                  </Link>
                  <i className="fa fa-sign-out text-white" onClick={Logout} />
                </li>
                <li className="nav-item dropdown pe-2 d-flex align-items-center" />
              </ul>
            </div>
          </div>
        </nav>
        <Outlet />
      </div>
      <style>{`
        @media (min-width: 1200px) {
          #navbarToggle {
            display: none !important;
          }

          #navbar {
            flex-direction: row !important;
            justify-content: end !important;
          }
        }

        @media (max-width: 1200px) {
          #navbar {
            flex-direction: row-reverse !important;
          }

          #sidenav-main {
            overflow-y: scroll !important;
            margin: 0 !important;
            border-bottom-left-radius: 0 !important;
            border-top-left-radius: 0 !important;

            ${
              SideNavType === "pinned"
                ? "display: block !important;"
                : "display: none !important;"
            }
          }
        }`}</style>
    </div>
  );
};

export default DashboardLayout;
