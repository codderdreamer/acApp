import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { w3cwebsocket as W3CWebSocket } from "websocket"
import React, { useEffect } from 'react';
import { useState } from "react";


interface Props {
  socket: W3CWebSocket | null;
  jsonString: string | null;
}

const EthernetSettings: React.FC<Props> = ({ socket, jsonString }) => {
  const { t } = useTranslation();
  const [newSocket, setSocket] = useState(socket);
  const [newjsonString, setEthernetSettingsString] = useState(jsonString);
  const [ethernetEnable, setethernetEnable] = useState<boolean>(false);
  const [ip, setip] = useState("");
  const [netmask, setnetmask] = useState("");
  const [gateway, setgateway] = useState("");

  useEffect(() => {
    setEthernetSettingsString(jsonString)
    if (jsonString) {
      const jsonData = JSON.parse(jsonString);
      setethernetEnable(jsonData.Data["ethernetEnable"])
      setip(jsonData.Data["ip"])
      setnetmask(jsonData.Data["netmask"])
      setgateway(jsonData.Data["gateway"])
    }

  }, [jsonString]);

  async function SaveEthernetSettings() {
    if (socket) {
      if (socket.readyState == socket.OPEN) {
        socket.send(JSON.stringify(
          {
            "Command" : "EthernetSettings",
            "Data" : {
                        "ethernetEnable" : ethernetEnable,
                        "ip" : ip,
                        "netmask" : netmask,
                        "gateway" : gateway
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
            <h5 className="font-weight-bolder">
              {t("ethernet-configuration")}
            </h5>
            <div className="row">
              <div className="col-12">
                <input
                  name="dhcp_enable"
                  checked={ethernetEnable}
                  onChange={(e) => setethernetEnable(e.target.checked)}
                  type="checkbox"
                />
                <label htmlFor="ethernet-configuration">
                  {t("ethernet-enable")}
                </label>
                <div
                  id="ethernet-configuration-form"
                >
                  <div className="row mb-3">
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("ip")}</label>
                      <input
                        name="ip"
                        value={ip}
                        onChange={(e) => setip(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("subnet-mask")}</label>
                      <input
                        name="netmask"
                        value={netmask}
                        onChange={(e) => setnetmask(e.target.value)}
                        className="form-control"
                        type="text"
                      />
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("gateway")}</label>
                      <input
                        name="gateway"
                        value={gateway}
                        onChange={(e) => setgateway(e.target.value)}
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
                    onClick={SaveEthernetSettings}
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

export default EthernetSettings;
