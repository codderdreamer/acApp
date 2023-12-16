import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { w3cwebsocket as W3CWebSocket } from "websocket"
import { useState } from "react";
import React, { useEffect } from 'react';

interface Props {
  socket: W3CWebSocket | null;
  jsonString: string | null;
}

const FourGSettings: React.FC<Props> = ({ socket, jsonString }) => {

  const { t } = useTranslation();
  const [newSocket, setSocket] = useState(socket);
  var [newNetworkPriorityString, setFourGSettingsString] = useState(jsonString);
  const [apn, setApn] = useState("");
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [pin, setPin] = useState("");
  const [activate, setActivate] = useState<boolean>(false);

  useEffect(() => {
    setFourGSettingsString(jsonString)
    console.log("networkPriorityString", jsonString)
    if (jsonString) {
      const jsonData = JSON.parse(jsonString);
      setActivate(jsonData.Data["enableModification"])
      setApn(jsonData.Data["apn"])
      setUser(jsonData.Data["user"])
      setPassword(jsonData.Data["password"])
      setPin(jsonData.Data["pin"])
    }

  }, [jsonString]);


  async function SaveFourGSettings() {
    if (socket) {
      if (socket.readyState == socket.OPEN) {
        socket.send(JSON.stringify(
          {
            "Command": "4GSettings",
            "Data": {
              "enableModification": activate,
              "apn": apn,
              "user": user,
              "password": password,
              "pin": pin
            }
          }
        ))
      }
    }
  }


  return (
    <div className="row mb-3">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <h5 className="font-weight-bolder">{t("4g-configuration")}</h5>
            <div className="row">
              <div className="col-12">
                <input
                  name="four_g_enable"
                  type="checkbox"
                  checked={activate}
                  onChange={(e) => setActivate(e.target.checked)}
                />
                <label htmlFor="4g-configuration">
                  {t("enable-modification")}
                </label>
                <div
                  id="4g-configuration-form"
                >
                  <div className="row mb-3">
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("apn")}</label>
                      <input
                        name="apn"
                        id="apn"
                        value={apn}
                        onChange={(e) => setApn(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("user")}</label>
                      <input
                        name="user"
                        value={user}
                        onChange={(e) => setUser(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("password")}</label>
                      <input
                        name="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("pin")}</label>
                      <input
                        name="pin"
                        value={pin}
                        onChange={(e) => setPin(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                  </div>
                </div>
                <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0">
                  <button
                    className="btn btn-primary btn-sm mb-0"
                    type="button"
                    name="button"
                    onClick={SaveFourGSettings}
                  >
                    {t("submit")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FourGSettings;
