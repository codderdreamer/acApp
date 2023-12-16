import { useState } from "react";
import { LoginService } from "./services";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import PasswordInput from "../../Components/PasswordInput";

const Login = () => {
  const [Email, setEmail] = useState("");
  const [Password, setPassword] = useState("");
  const { t } = useTranslation();

  const navigate = useNavigate();

  async function LoginClickEvent() {
    try {
      // const data = (await LoginService({ email: Email, password: Password })).data

      localStorage.setItem("access_token", "1234567890"); // example token
      // localStorage.setItem("email", Email);

      navigate("/admin/dashboard");
    } catch (error: any) {
      if (error.response.data.message) {
        toast.error(error.response.data.message);
        return;
      }

      toast.error(t("email-or-password-wrong"));
    }
  }

  return (
    <>
      <div className="col-xl-8 col-lg-12 col-md-12 d-flex flex-column">
        <div className="card card-plain">
          <div className="card-header pb-0 text-start">
            <div className="d-flex justify-content-center col-12 py-1">
              <img
                style={{ width: "auto", height: 70 }}
                src="https://heracharge.com/logo.webp"
                alt=""
              />
            </div>
            <div className="d-flex justify-content-center py-1">
              <h4 className="font-weight-bolder">{t("sign-in")}</h4>
            </div>
            <div className="d-flex justify-content-center py-1">
              <p className="mb-0">{t("enter-email")}</p>
            </div>
          </div>
          <div className="card-body">
            <div className="mb-3">
              <input
                type="email"
                className="form-control form-control-lg"
                placeholder={t("email")}
                aria-label={t("email")}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <PasswordInput
                onChange={(value: string) => setPassword(value)}
                placeholder={t("password")}
                title=""
              />
            </div>
            <div className="text-center">
              <button
                type="button"
                className="btn btn-lg btn-dark text-white btn-lg w-100 mt-2 mb-0"
                onClick={LoginClickEvent}
              >
                {t("sign-in")}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Login;
