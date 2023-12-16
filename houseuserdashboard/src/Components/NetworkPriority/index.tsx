import { toast } from "react-toastify";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { w3cwebsocket as W3CWebSocket } from "websocket"
import React, { useEffect } from 'react';


interface Props {
  socket: W3CWebSocket | null;
  jsonString: string | null;
}

const NetworkPriority: React.FC<Props> = ({ socket, jsonString }) => {
  const { t } = useTranslation();
  const [newSocket, setSocket] = useState(socket);
  const [newjsonString, setNetworkPriorityString] = useState(jsonString);
  const [EnableWorkmode, setEnableWorkmode] = useState<boolean>(false);
  const [Priority1, setPriority1] = useState("");
  const [Priority2, setPriority2] = useState("");
  const [Priority3, setPriority3] = useState("");

  useEffect(() => {
    setNetworkPriorityString(jsonString)
    console.log("networkPriorityString", jsonString)
    if (jsonString) {
      const jsonData = JSON.parse(jsonString);
      setEnableWorkmode(jsonData.Data["enableWorkmode"])
      setPriority1(jsonData.Data["1"])
      setPriority2(jsonData.Data["2"])
      setPriority3(jsonData.Data["3"])
    }

  }, [jsonString]);


  async function SavePrioritySettings() {
    if (socket) {
      if (socket.readyState == socket.OPEN) {
        socket.send(JSON.stringify(
          {
            "Command": "NetworkPriority",
            "Data": {
              "enableWorkmode": EnableWorkmode,
              "1": Priority1,
              "2": Priority2,
              "3": Priority3
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
              {t("network-priority-selection")}
            </h5>
            <div className="row">
              <div className="col-12">
                <input
                  checked={EnableWorkmode}
                  name="network_priority_enabled"
                  type="checkbox"
                  onChange={(e) => setEnableWorkmode(e.target.checked)}
                />
                <label htmlFor="enable-workmode">{t("enable-workmode")}</label>
                <div
                  id="enable-workmode-form"
                >
                  <div className="row mb-3">
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("priority-no")} 1</label>
                      <select
                        value={Priority1}
                        onChange={(e) => setPriority1(e.target.value)}
                        id="priority1"
                        className="form-control"
                      >
                        <option value="">{t("select")}</option>
                        <option value="ETH">Eth</option>
                        <option value="WLAN">WLAN</option>
                        <option value="4G">4G</option>
                      </select>
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("priority-no")} 2</label>
                      <select
                        value={Priority2}
                        onChange={(e) => setPriority2(e.target.value)}
                        id="priority2"
                        className="form-control"
                      >
                        <option value="">{t("select")}</option>
                        <option value="ETH">Eth</option>
                        <option value="WLAN">WLAN</option>
                        <option value="4G">4G</option>
                      </select>
                    </div>
                    <div className="col-12 col-md-6 col-md-6">
                      <label className="mt-4">{t("priority-no")} 3</label>
                      <select
                        value={Priority3}
                        onChange={(e) => setPriority3(e.target.value)}
                        id="priority3"
                        className="form-control"
                      >
                        <option value="">{t("select")}</option>
                        <option value="ETH">Eth</option>
                        <option value="WLAN">WLAN</option>
                        <option value="4G">4G</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="d-flex justify-content-between justify-content-sm-start gap-sm-3 gap-0">
                  <button
                    className="btn btn-primary btn-sm mb-0"
                    type="button"
                    name="button"
                    onClick={SavePrioritySettings}
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

export default NetworkPriority;
